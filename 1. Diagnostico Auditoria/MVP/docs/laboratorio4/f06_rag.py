"""P06 — Recuperación y aplicación de reglas (RAG simulado).

Verifica el adaptador de conocimiento (búsqueda por palabras clave) y cómo el
caso de uso aplica IVA, tope comercial y stock mínimo.
"""

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from _common import guardar, imprimir, solicitud, token
from app.infrastructure.mock_vector_db import MockVectorDbAdapter

RAG = MockVectorDbAdapter()


def _chat(prompt: str, cabecera: dict) -> dict:
    respuesta = solicitud("POST", "/ai/chat", json={"message": prompt}, headers=cabecera)
    cuerpo = respuesta["cuerpo"] if isinstance(respuesta["cuerpo"], dict) else {}
    return {
        "prompt": prompt,
        "status": respuesta["status"],
        "respuesta": cuerpo.get("response", ""),
        "transfer": cuerpo.get("transfer_to_employee"),
    }


def ejecutar() -> dict:
    admin = {"Authorization": f"Bearer {token('admin', 'AdminPass123!')}"}
    cliente = {"Authorization": f"Bearer {token('cliente', 'ClientPass123!')}"}

    recuperacion = {
        prompt: RAG.buscar_contexto(prompt)
        for prompt in (
            "Cotiza 2 kg de glicerina con IVA",
            "Cotiza 2 kg de glicerina con impuesto",
            "Cotiza 2 kg de glicerina con tope máximo",
            "¿Cuál es el stock de glicerina?",
            "Cotiza 2 kg de glicerina",
        )
    }

    material = solicitud(
        "POST",
        "/materials",
        json={
            "name": "Base cosmética P06",
            "category": "Pruebas",
            "unit": "kg",
            "price": 60000,
            "stock": 2000,
            "description": "Material temporal del caso P06",
        },
        headers=admin,
    )
    material_id = material["cuerpo"]["id"] if material["status"] == 201 else None

    casos = {
        "sin_reglas": _chat("Cotiza 2 kg de glicerina", cliente),
        "iva": _chat("Cotiza 2 kg de glicerina con IVA", cliente),
        "impuesto": _chat("Cotiza 2 kg de glicerina con impuesto", cliente),
        "tope": _chat("Cotiza 1000 kg de Base cosmética P06 con tope máximo", cliente),
        "falso_positivo_max": _chat("Cotiza 1000 kg de Base cosmética P06 al máximo", cliente),
    }

    if material_id is not None:
        solicitud("DELETE", f"/materials/{material_id}", headers=admin)

    casos["sin_reglas"]["aplica_iva"] = "IVA 19%" in casos["sin_reglas"]["respuesta"]
    casos["iva"]["aplica_iva"] = "IVA 19%" in casos["iva"]["respuesta"]
    casos["impuesto"]["aplica_iva"] = "IVA 19%" in casos["impuesto"]["respuesta"]
    casos["tope"]["aplica_tope"] = "50.000.000,00" in casos["tope"]["respuesta"]
    casos["falso_positivo_max"]["aplica_tope"] = "tope comercial" in casos["falso_positivo_max"]["respuesta"]

    evidencia = {
        "recuperacion_por_palabras_clave": recuperacion,
        "casos_http": casos,
        "criterios": {
            "sin_reglas_no_aplica_iva": not casos["sin_reglas"]["aplica_iva"],
            "iva_por_sinonimo": casos["iva"]["aplica_iva"] and casos["impuesto"]["aplica_iva"],
            "tope_aplicado": casos["tope"]["aplica_tope"],
            "sin_falso_positivo": not casos["falso_positivo_max"]["aplica_tope"],
        },
    }
    evidencia["criterios"]["cumple_todos"] = all(evidencia["criterios"].values())
    return evidencia


if __name__ == "__main__":
    resultado = ejecutar()
    imprimir("P06 — Reglas RAG", resultado)
    guardar("f06_rag.json", resultado)
