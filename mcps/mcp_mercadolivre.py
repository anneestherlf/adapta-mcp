import requests


def search_mercadolivre(query: str, api_key: str = None) -> dict:
    """Busca simples no Mercado Livre usando a API pública.

    Observações:
    - Para buscas públicas a API não exige chave (usamos endpoint público).
    - Retornamos lista simplificada de itens para a PoC.
    """
    try:
        params = {"q": query, "limit": 5}
        resp = requests.get("https://api.mercadolibre.com/sites/MLB/search", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        simplified = []
        for it in results:
            simplified.append({
                "id": it.get("id"),
                "title": it.get("title"),
                "price": it.get("price"),
                "currency": it.get("currency_id"),
                "permalink": it.get("permalink"),
                "thumbnail": it.get("thumbnail"),
            })

        return {"status": "success", "data": simplified}

    except requests.exceptions.HTTPError as http_err:
        return {"status": "error", "message": f"HTTP error: {http_err}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
