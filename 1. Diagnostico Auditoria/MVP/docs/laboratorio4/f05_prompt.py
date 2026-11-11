"""P05 — Interpretación del mensaje y extracción de cantidades.

Compara lo que el usuario escribe con lo que el asistente entiende. Se evalúa
tanto el contenido de la respuesta como la decisión de transferir a un asesor.
"""

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from _common import guardar, imprimir, solicitud, token


CASOS = [
    {
        "prompt": "Cotiza 2 kg de glicerina",
        "esperado": "cotiza 2 kg a precio de catálogo",
        "marcador": "Glicerina vegetal",
        "transfer_esperado": False,
    },
    {
        "prompt": "COTIZA 2 KG DE GLICERINA",
        "esperado": "misma cotización en mayúsculas",
        "marcador": "Glicerina vegetal",
        "transfer_esperado": False,
    },
    {
        "prompt": "cotiza 2kg de glicerina",
        "esperado": "tolera ausencia de espacio entre número y unidad",
        "marcador": "Glicerina vegetal",
        "transfer_esperado": False,
    },
    {
        "prompt": "Necesito 2 kg de glicerina",
        "esperado": "cotiza aunque no diga 'cotiza'",
        "marcador": "Glicerina vegetal",
        "transfer_esperado": False,
    },
    {
        "prompt": "Cotiza 2 kilos de glicerina",
        "esperado": "entiende 'kilos' como unidad",
        "marcador": "Glicerina vegetal",
        "transfer_esperado": False,
    },
    {
        "prompt": "Cotiza dos kg de glicerina",
        "esperado": "entiende números escritos con palabras",
        "marcador": "Glicerina vegetal",
        "transfer_esperado": False,
    },
    {
        "prompt": "Cotiza 2 kg de glicerina y 3 kg de ácido cítrico",
        "esperado": "extrae dos ítems en una sola frase",
        "marcador": "Ácido cítrico",
        "transfer_esperado": False,
    },
    {
        "prompt": "Cotiza 2 kg de mercurio",
        "esperado": "informa que el material no existe y deriva a un asesor",
        "marcador": "No encontré",
        "transfer_esperado": True,
    },
    {
        "prompt": "No tengo problemas con mi pedido",
        "esperado": "no transfiere: no hay consulta técnica",
        "marcador": "Puedes crear un pedido",
        "transfer_esperado": False,
    },
    {
        "prompt": "Quiero 5 kg de glicerina para mi formulación",
        "esperado": "cotiza y marca revisión técnica",
        "marcador": "Glicerina vegetal",
        "transfer_esperado": True,
    },
]


def ejecutar() -> dict:
    cabecera = {"Authorization": f"Bearer {token('cliente', 'ClientPass123!')}"}
    resultados = []
    for caso in CASOS:
        respuesta = solicitud("POST", "/ai/chat", json={"message": caso["prompt"]}, headers=cabecera)
        cuerpo = respuesta["cuerpo"] if isinstance(respuesta["cuerpo"], dict) else {}
        texto = cuerpo.get("response", "")
        transfer = cuerpo.get("transfer_to_employee")
        resultados.append(
            {
                "prompt": caso["prompt"],
                "esperado": caso["esperado"],
                "status": respuesta["status"],
                "respuesta": texto,
                "transfer": transfer,
                "motivo": cuerpo.get("reason"),
                "motor": cuerpo.get("motor"),
                "coincide": caso["marcador"] in texto and transfer == caso["transfer_esperado"],
            }
        )

    evidencia = {
        "casos": resultados,
        "coinciden": sum(1 for r in resultados if r["coincide"]),
        "total": len(resultados),
        "hallazgos": [r["prompt"] for r in resultados if not r["coincide"]],
    }
    return evidencia


if __name__ == "__main__":
    resultado = ejecutar()
    imprimir("P05 — Prompt y extracción de cantidades", resultado)
    guardar("f05_prompt.json", resultado)
