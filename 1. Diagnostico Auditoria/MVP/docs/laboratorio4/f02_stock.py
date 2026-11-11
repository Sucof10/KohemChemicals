"""P02 — Regla crítica de inventario y consistencia transaccional.

Comprueba que no se venda por encima del stock, que un pedido fallido no
consuma stock parcialmente y que una cantidad inválida sea rechazada.
"""

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from _common import guardar, imprimir, solicitud, token


def _stock(materiales: list[dict]) -> dict:
    return {m["id"]: m["stock"] for m in materiales}


def ejecutar() -> dict:
    cabecera_cliente = {"Authorization": f"Bearer {token('cliente', 'ClientPass123!')}"}
    cabecera_admin = {"Authorization": f"Bearer {token('admin', 'AdminPass123!')}"}

    materiales = solicitud("GET", "/materials")["cuerpo"]
    glicerina = next(m for m in materiales if "glicerina" in m["name"].lower())
    citrico = next(m for m in materiales if "cítrico" in m["name"].lower())
    antes = _stock(materiales)

    sobreventa = solicitud(
        "POST",
        "/ai/chat",
        json={"message": f"Cotiza 10000 kg de {glicerina['name']}"},
        headers=cabecera_cliente,
    )

    pedido_invalido = solicitud(
        "POST",
        "/orders",
        json={
            "items": [
                {"raw_material_id": glicerina["id"], "quantity": 1},
                {"raw_material_id": citrico["id"], "quantity": 999999},
            ]
        },
        headers=cabecera_cliente,
    )

    despues = _stock(solicitud("GET", "/materials")["cuerpo"])

    cantidad_cero = solicitud(
        "POST",
        "/orders",
        json={"items": [{"raw_material_id": glicerina["id"], "quantity": 0}]},
        headers=cabecera_cliente,
    )

    # Limpieza: si por algún motivo se creó un pedido, se cancela para devolver el stock.
    if pedido_invalido["status"] == 201 and isinstance(pedido_invalido["cuerpo"], dict):
        solicitud(
            "PATCH",
            f"/orders/{pedido_invalido['cuerpo']['id']}/status",
            json={"status": "cancelado"},
            headers=cabecera_cliente,
        )

    evidencias = {
        "stock_antes": antes,
        "stock_despues": despues,
        "stock_sin_cambios": antes == despues,
        "sobreventa_ia": sobreventa,
        "pedido_multitems_con_stock_insuficiente": pedido_invalido,
        "cantidad_cero": cantidad_cero,
        "criterios": {
            "impide_sobreventa": sobreventa["status"] in (400, 422),
            "no_reserva_stock_parcial": antes == despues,
            "rechaza_cantidad_cero": cantidad_cero["status"] in (400, 422),
        },
    }
    evidencias["criterios"]["cumple_todos"] = all(evidencias["criterios"].values())
    return evidencias


if __name__ == "__main__":
    resultado = ejecutar()
    imprimir("P02 — División por cero / stock insuficiente", resultado)
    guardar("f02_stock.json", resultado)
