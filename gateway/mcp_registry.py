"""Registry para MCPs dinamicamente registrados via API admin.

Funcionalidades:
- registrar metadata sobre MCPs (name, filename, description, entrypoint)
- carregar módulos dos arquivos salvos em `mcps/custom/` e retornar funções
  utilizáveis pelo Gateway (com injeção de credenciais quando necessário)
"""
import json
from pathlib import Path
import importlib.util
import inspect
from typing import Dict, Callable
from functools import wraps

REGISTRY_FILE = Path("mcps/registry.json")
CUSTOM_DIR = Path("mcps/custom")
CUSTOM_DIR.mkdir(parents=True, exist_ok=True)


def _read_registry() -> Dict[str, dict]:
    if not REGISTRY_FILE.exists():
        return {}
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_registry(d: Dict[str, dict]) -> None:
    REGISTRY_FILE.write_text(json.dumps(d, indent=2), encoding="utf-8")


def register_mcp(name: str, filename: str, description: str, entrypoint: str) -> None:
    """Registra um MCP no arquivo de registry. Espera que o arquivo já esteja salvo em mcps/custom."""
    reg = _read_registry()
    reg[name] = {
        "filename": filename,
        "description": description,
        "entrypoint": entrypoint,
    }
    _write_registry(reg)


def list_mcp() -> Dict[str, dict]:
    return _read_registry()


def _import_module_from_path(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        raise ImportError("Cannot load module")
    loader.exec_module(mod)
    return mod


def _wrap_with_creds(func: Callable, service_name: str, cred_getter: Callable[[str, str], str]):
    """Cria um wrapper em torno de func que injeta credencial se necessário.

    Preserva a assinatura original para que ferramentas como LLMs consigam
    introspecionar parâmetros.
    """
    sig = inspect.signature(func)

    @wraps(func)
    def wrapper(**kwargs):
        # Se função espera 'api_key' e não foi fornecida, preencha via cred_getter
        if 'api_key' in sig.parameters and 'api_key' not in kwargs:
            api_key = cred_getter(service_name, 'api_key')
            if api_key:
                kwargs['api_key'] = api_key
        return func(**kwargs)

    # Preserve signature so introspection sees the original params
    wrapper.__signature__ = sig
    return wrapper


def load_all_tools(cred_getter: Callable[[str, str], str]) -> Dict[str, Callable]:
    """Carrega todas as ferramentas registradas e retorna nome->callable.

    cred_getter(service_name, key_name) -> credential string
    """
    tools: Dict[str, Callable] = {}
    registry = _read_registry()
    for name, info in registry.items():
        filename = info.get('filename')
        entrypoint = info.get('entrypoint')
        path = CUSTOM_DIR / filename
        if not path.exists():
            continue
        try:
            mod = _import_module_from_path(path)
            func = getattr(mod, entrypoint, None)
            if func and callable(func):
                wrapped = _wrap_with_creds(func, name, cred_getter)
                # Expose as tool with key equal to registered name
                tools[name] = wrapped
        except Exception:
            # skip broken modules for now
            continue

    return tools
