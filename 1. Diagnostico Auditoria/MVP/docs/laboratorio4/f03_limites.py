"""P03 — Valores límite: negativos, decimales y redondeo.

Añade a la suite las verificaciones de signos y precisión sobre el dominio y
sobre el contrato de materias primas y pedidos.
"""

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from _common import guardar, imprimir, solicitud, token
from app.domain.services import PricingDomainService

DOMINIO = PricingDomainService()


def ejecutar() -> dict:
    admin = {"Authorization": f"Bearer {token('admin', 'AdminPass123!')}"}
    cliente = {"Authorization": f"Bearer {token('cliente', 'ClientPass123!')}"}

    precision = {
        "0.1x3": {"esperado": 0.3, "obtenido": DOMINIO.subtotal(0.1, 3)},
        "1234.567x3": {"esperado": 3703.7, "obtenido": DOMINIO.subtotal(1234.567, 3)},
        "media_unidad": {"esperado": 9000.0, "obtenido": DOMINIO.subtotal(18000, 0.5)},
    }
    for caso in precision.values():
        caso["correcto"] = caso["esperado"] == caso["obtenido"]

    precio_negativo = solicitud(
        "POST",
        "/materials",
        json={
            "name": "Material precio negativo",
            "category": "Pruebas",
            "unit": "kg",
            "price": -100,
            "stock": 10,
            "description": "P03",
        },
        headers=admin,
    )

    stock_negativo = solicitud(
        "POST",
        "/materials",
        json={
            "name": "Material stock negativo",
            "category": "Pruebas",
            "unit": "kg",
            "price": 1000,
            "stock": -1,
            "description": "P03",
        },
        headers=admin,
    )

    material = solicitud(
        "POST",
        "/materials",
        json={
            "name": "Material decimal P03",
            "category": "Pruebas",
            "unit": "kg",
            "price": 1234.567,
            "stock": 10,
            "description": "Material temporal del caso P03",
        },
        headers=admin,
    )

    pedido_decimal = {"omitido": True}
    if material["status"] == 201:
        material_id = material["cuerpo"]["id"]
        pedido = solicitud(
            "POST",
            "/orders",
            json={"items": [{"raw_material_id": material_id, "quantity": 3}]},
            headers=cliente,
        )
        pedido_decimal = pedido
        if pedido["status"] == 201:
            solicitud(
                "PATCH",
                f"/orders/{pedido['cuerpo']['id']}/status",
                json={"status": "cancelado"},
                headers=cliente,
            )
        solicitud("DELETE", f"/materials/{material_id}", headers=admin)

    cantidad_negativa = solicitud(
        "POST",
        "/orders",
        json={"items": [{"raw_material_id": 1, "quantity": -2}]},
        headers=cliente,
    )

    evidencia = {
        "precision_dominio": precision,
        "precision_correcta": all(c["correcto"] for c in precision.values()),
        "material_precio_negativo": precio_negativo,
        "material_stock_negativo": stock_negativo,
        "pedido_con_decimales": pedido_decimal,
        "pedido_cantidad_negativa": cantidad_negativa,
        "criterios": {
            "rechaza_precio_negativo": precio_negativo["status"] in (400, 422),
            "rechaza_stock_negativo": stock_negativo["status"] in (400, 422),
            "rechaza_cantidad_negativa": cantidad_negativa["status"] in (400, 422),
            "conserva_precision": pedido_decimal.get("status") == 201
            and pedido_decimal["cuerpo"]["total"] == 3703.7,
        },
    }
    evidencia["criterios"]["cumple_todos"] = all(evidencia["criterios"].values())
    return evidencia


if __name__ == "__main__":
    resultado = ejecutar()
    imprimir("P03 — Negativos y decimales", resultado)
    guardar("f03_limites.json", resultado)
