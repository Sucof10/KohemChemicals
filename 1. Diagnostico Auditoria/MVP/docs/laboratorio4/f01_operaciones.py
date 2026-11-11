"""P01 — Operaciones del dominio y cálculo de pedido.

Verifica la aritmética pura (subtotal, total, IVA) y su reflejo en la
cotización que devuelve el asistente.
"""

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from _common import API, guardar, imprimir, solicitud, token
from app.domain.services import PricingDomainService


def ejecutar() -> dict:
    dominio = PricingDomainService()
    casos_dominio = {
        "subtotal_2kg_glicerina": {
            "esperado": 36000.0,
            "obtenido": dominio.subtotal(18000, 2),
        },
        "subtotal_media_unidad": {
            "esperado": 9000.0,
            "obtenido": dominio.subtotal(18000, 0.5),
        },
        "total_dos_items": {
            "esperado": 48000.0,
            "obtenido": dominio.total([36000.0, 12000.0]),
        },
        "iva_19": {"esperado": 9120.0, "obtenido": dominio.impuesto(48000)},
    }
    for caso in casos_dominio.values():
        caso["correcto"] = caso["esperado"] == caso["obtenido"]

    materiales = solicitud("GET", "/materials")["cuerpo"]
    glicerina = next(m for m in materiales if "glicerina" in m["name"].lower())
    citrico = next(m for m in materiales if "cítrico" in m["name"].lower())

    esperado_subtotal = round(glicerina["price"] * 2 + citrico["price"] * 3, 2)
    chat = solicitud(
        "POST",
        "/ai/chat",
        json={"message": f"Cotiza 2 kg de {glicerina['name']} y 3 kg de {citrico['name']}"},
        headers={"Authorization": f"Bearer {token('cliente', 'ClientPass123!')}"},
    )
    texto = chat["cuerpo"]["response"] if isinstance(chat["cuerpo"], dict) else ""

    evidencia = {
        "dominio": casos_dominio,
        "dominio_correcto": all(c["correcto"] for c in casos_dominio.values()),
        "cotizacion_http": {
            "status": chat["status"],
            "subtotal_esperado": esperado_subtotal,
            "respuesta": texto,
            "contiene_subtotal_esperado": _formato(esperado_subtotal) in texto,
        },
    }
    evidencia["criterios"] = {
        "dominio_correcto": evidencia["dominio_correcto"],
        "cotizacion_coherente": chat["status"] == 200 and evidencia["cotizacion_http"]["contiene_subtotal_esperado"],
    }
    evidencia["criterios"]["cumple_todos"] = all(evidencia["criterios"].values())
    return evidencia


def _formato(valor: float) -> str:
    return f"${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


if __name__ == "__main__":
    resultado = ejecutar()
    print(f"API: {API}")
    imprimir("P01 — Operaciones básicas", resultado)
    guardar("f01_operaciones.json", resultado)
