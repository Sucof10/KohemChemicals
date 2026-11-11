"""P09 — Manejo de errores y robustez del contrato.

Compara el comportamiento del módulo de IA (nuevo) con los endpoints legados
que aún validan con ``model_validate`` dentro del router.
"""

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

import httpx

from _common import API, guardar, imprimir, token

_SENALES_FUGA = ("Traceback", "pydantic_core", "File \"", "site-packages")


def _llamar(metodo: str, ruta: str, **kwargs) -> dict:
    respuesta = httpx.request(metodo, f"{API}{ruta}", timeout=20, **kwargs)
    try:
        cuerpo = respuesta.json()
    except ValueError:
        cuerpo = respuesta.text
    texto = str(cuerpo)
    return {
        "metodo": metodo,
        "ruta": ruta,
        "status": respuesta.status_code,
        "cuerpo": cuerpo,
        "fuya_internos": any(senal in texto for senal in _SENALES_FUGA),
    }


def ejecutar() -> dict:
    cliente = {"Authorization": f"Bearer {token('cliente', 'ClientPass123!')}"}
    admin = {"Authorization": f"Bearer {token('admin', 'AdminPass123!')}"}

    casos = {
        "prompt_no_reconocido": _llamar("POST", "/ai/chat", json={"message": "xyz"}, headers=cliente),
        "prompt_vacio": _llamar("POST", "/ai/chat", json={"message": ""}, headers=cliente),
        "json_mal_formado": _llamar(
            "POST", "/ai/chat", content=b"{", headers={**cliente, "Content-Type": "application/json"}
        ),
        "content_type_invalido": _llamar(
            "POST", "/ai/chat", content=b"x", headers={**cliente, "Content-Type": "text/plain"}
        ),
        "campos_adicionales": _llamar(
            "POST", "/ai/chat", json={"message": "Hola", "admin": True}, headers=cliente
        ),
        "legado_pedido_invalido": _llamar(
            "POST", "/orders", json={"items": [{"raw_material_id": 1, "quantity": -1}]}, headers=cliente
        ),
        "legado_material_invalido": _llamar(
            "POST",
            "/materials",
            json={"name": "X", "category": "Y", "unit": "kg", "price": 0, "stock": 1},
            headers=admin,
        ),
        "sin_token": _llamar("POST", "/ai/chat", json={"message": "Hola"}),
        "rol_no_autorizado_en_auditoria": _llamar("GET", "/audit-logs", headers=cliente),
    }

    evidencia = {
        "casos": casos,
        "resumen": {
            "errores_controlados": sum(
                1 for c in casos.values() if 400 <= c["status"] < 500
            ),
            "errores_500": [nombre for nombre, c in casos.items() if c["status"] >= 500],
            "fugas_de_internos": [nombre for nombre, c in casos.items() if c["fuya_internos"]],
        },
    }
    return evidencia


if __name__ == "__main__":
    resultado = ejecutar()
    imprimir("P09 — Errores y robustez", resultado)
    guardar("f09_errores.json", resultado)
