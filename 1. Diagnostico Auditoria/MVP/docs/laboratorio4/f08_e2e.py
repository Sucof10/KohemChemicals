"""P08 — Flujo de extremo a extremo: presentación → aplicación → MCP → dominio.

Recorre una cotización por HTTP y un pedido real, comprobando el descuento de
stock, el registro de auditoría y la restauración al cancelar.
"""

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from _common import guardar, imprimir, solicitud, token


def _material(nombre: str) -> dict:
    materiales = solicitud("GET", "/materials")["cuerpo"]
    return next(m for m in materiales if nombre in m["name"].lower())


def ejecutar() -> dict:
    cliente = {"Authorization": f"Bearer {token('cliente', 'ClientPass123!')}"}
    admin = {"Authorization": f"Bearer {token('admin', 'AdminPass123!')}"}

    glicerina = _material("glicerina")
    antes = glicerina["stock"]

    chat = solicitud(
        "POST",
        "/ai/chat",
        json={"message": f"Cotiza 2 kg de {glicerina['name']} con IVA"},
        headers=cliente,
    )

    pedido = solicitud(
        "POST",
        "/orders",
        json={"items": [{"raw_material_id": glicerina["id"], "quantity": 2}]},
        headers=cliente,
    )
    despues_pedido = _material("glicerina")["stock"]

    logs_creacion = solicitud("GET", "/audit-logs?limit=50", headers=admin)["cuerpo"]
    log_creacion = next(
        (
            log
            for log in logs_creacion
            if log["action"] == "CREATE" and log["entity"] == "order" and log["entity_id"] == pedido["cuerpo"]["id"]
        ),
        None,
    )

    cancelacion = solicitud(
        "PATCH",
        f"/orders/{pedido['cuerpo']['id']}/status",
        json={"status": "cancelado"},
        headers=cliente,
    )
    despues_cancelacion = _material("glicerina")["stock"]

    logs_cancelacion = solicitud("GET", "/audit-logs?limit=50", headers=admin)["cuerpo"]
    log_cancelacion = next(
        (
            log
            for log in logs_cancelacion
            if log["action"] == "UPDATE_STATUS" and log["entity_id"] == pedido["cuerpo"]["id"]
        ),
        None,
    )

    evidencia = {
        "cotizacion": chat,
        "pedido": pedido,
        "stock": {
            "antes": antes,
            "tras_pedido": despues_pedido,
            "tras_cancelar": despues_cancelacion,
        },
        "auditoria": {
            "creacion": log_creacion,
            "cancelacion": log_cancelacion,
        },
        "cancelacion": cancelacion,
        "criterios": {
            "cotizacion_200": chat["status"] == 200,
            "pedido_201": pedido["status"] == 201,
            "descuenta_stock": despues_pedido == round(antes - 2, 4),
            "registra_creacion": log_creacion is not None,
            "restaura_stock": despues_cancelacion == antes,
            "registra_cancelacion": log_cancelacion is not None,
        },
    }
    evidencia["criterios"]["cumple_todos"] = all(evidencia["criterios"].values())
    return evidencia


if __name__ == "__main__":
    resultado = ejecutar()
    imprimir("P08 — Flujo extremo a extremo", resultado)
    guardar("f08_e2e.json", resultado)
