"""P04 — Contrato HTTP y validación Pydantic del endpoint /ai/chat."""

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

import httpx

from _common import API, guardar, imprimir, token


def _llamar(metodo: str, ruta: str, **kwargs) -> dict:
    respuesta = httpx.request(metodo, f"{API}{ruta}", timeout=20, **kwargs)
    try:
        cuerpo = respuesta.json()
    except ValueError:
        cuerpo = respuesta.text
    return {"status": respuesta.status_code, "cuerpo": cuerpo}


def ejecutar() -> dict:
    cliente = {"Authorization": f"Bearer {token('cliente', 'ClientPass123!')}"}
    admin = {"Authorization": f"Bearer {token('admin', 'AdminPass123!')}"}
    ruta = "/ai/chat"

    casos = {
        "valido": _llamar("POST", ruta, json={"message": "Hola"}, headers=cliente),
        "sin_message": _llamar("POST", ruta, json={"texto": "Hola"}, headers=cliente),
        "message_vacio": _llamar("POST", ruta, json={"message": ""}, headers=cliente),
        "message_espacios": _llamar("POST", ruta, json={"message": "   "}, headers=cliente),
        "message_no_textual": _llamar("POST", ruta, json={"message": 123}, headers=cliente),
        "campo_extra": _llamar("POST", ruta, json={"message": "Hola", "role": "admin"}, headers=cliente),
        "formulario": _llamar("POST", ruta, data={"message": "Hola"}, headers=cliente),
        "content_type_texto": _llamar(
            "POST", ruta, content=b"Hola", headers={**cliente, "Content-Type": "text/plain"}
        ),
        "json_mal_formado": _llamar(
            "POST", ruta, content=b'{"message": ', headers={**cliente, "Content-Type": "application/json"}
        ),
        "utf8_invalido": _llamar(
            "POST", ruta, content=b'{"message": "\xff"}', headers={**cliente, "Content-Type": "application/json"}
        ),
        "sin_token": _llamar("POST", ruta, json={"message": "Hola"}),
    }

    esperado = {
        "valido": 200,
        "sin_message": 422,
        "message_vacio": 422,
        "message_espacios": 422,
        "message_no_textual": 422,
        "campo_extra": 200,
        "formulario": 200,
        "content_type_texto": 415,
        "json_mal_formado": 400,
        "utf8_invalido": 400,
        "sin_token": 401,
    }
    for nombre, codigo in esperado.items():
        casos[nombre]["esperado"] = codigo
        casos[nombre]["coincide"] = casos[nombre]["status"] == codigo

    # Contraste con el módulo legado: el mismo tipo de error produce 500.
    legado = _llamar(
        "POST",
        "/materials",
        json={"name": "X", "category": "Y", "unit": "kg", "price": -5, "stock": 1},
        headers=admin,
    )
    legado["esperado"] = 422
    legado["coincide"] = legado["status"] == 422

    evidencia = {
        "endpoint": "/api/v1/ai/chat",
        "casos": casos,
        "contraste_legado_materials": legado,
        "todos_coinciden": all(c["coincide"] for c in casos.values()),
    }
    evidencia["criterios"] = {
        "contrato_estricto": evidencia["todos_coinciden"],
        "legado_devuelve_422": legado["coincide"],
    }
    evidencia["criterios"]["cumple_todos"] = all(evidencia["criterios"].values())
    return evidencia


if __name__ == "__main__":
    resultado = ejecutar()
    imprimir("P04 — Contrato HTTP y Pydantic", resultado)
    guardar("f04_contrato.json", resultado)
