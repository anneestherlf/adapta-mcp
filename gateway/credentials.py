"""Gerenciamento simples de credenciais centralizadas.

AVISO: Para PoC armazenamos credenciais em um arquivo JSON local `.credentials.json`.
Em produção, use um cofre de segredos (HashiCorp Vault, Azure Key Vault, AWS Secrets).
"""
import json
from pathlib import Path
from threading import Lock
from typing import Optional

_CRED_FILE = Path(".credentials.json")
_lock = Lock()


def _read_all() -> dict:
    if not _CRED_FILE.exists():
        return {}
    try:
        return json.loads(_CRED_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_all(data: dict) -> None:
    _CRED_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def set_credential(service: str, key: str, value: str) -> None:
    with _lock:
        data = _read_all()
        svc = data.get(service, {})
        svc[key] = value
        data[service] = svc
        _write_all(data)


def get_credential(service: str, key: str = "api_key") -> Optional[str]:
    with _lock:
        data = _read_all()
        svc = data.get(service, {})
        return svc.get(key)


def list_credentials() -> dict:
    return _read_all()
