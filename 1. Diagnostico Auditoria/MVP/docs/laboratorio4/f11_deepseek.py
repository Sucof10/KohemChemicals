"""P11 — Motor de lenguaje (DeepSeek) y respaldo por reglas.

Comprueba qué motor respondió cada consulta. Si DEEPSEEK_API_KEY no está
configurada, el asistente debe seguir funcionando con el motor de reglas; si lo
está, las consultas deben resolverse con DeepSeek y el campo ``motor`` debe
reflejarlo.
"""

import sys
import time

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from _common import guardar, imprimir, solicitud, token
from app.infrastructure.config import settings

CONSULTAS = [
    "Cotiza dos kilos de glicerina",
    "¿Cuántos kilos de glicerina tienen disponibles?",
    "Necesito asesoría para una formulación",
]


def ejecutar() -> dict:
    configurado = bool(settings.DEEPSEEK_API_KEY.strip())
    cabecera = {"Authorization": f"Bearer {token('cliente', 'ClientPass123!')}"}

    casos = []
    for consulta in CONSULTAS:
        inicio = time.perf_counter()
        respuesta = solicitud("POST", "/ai/chat", json={"message": consulta}, headers=cabecera)
        latencia = round((time.perf_counter() - inicio) * 1000, 1)
        cuerpo = respuesta["cuerpo"] if isinstance(respuesta["cuerpo"], dict) else {}
        casos.append(
            {
                "consulta": consulta,
                "status": respuesta["status"],
                "motor": cuerpo.get("motor"),
                "respuesta": cuerpo.get("response"),
                "transfer": cuerpo.get("transfer_to_employee"),
                "latencia_ms": latencia,
            }
        )

    esperado = "deepseek" if configurado else "reglas"
    evidencia = {
        "proveedor": "DeepSeek",
        "modelo": settings.DEEPSEEK_MODEL,
        "base_url": settings.DEEPSEEK_BASE_URL,
        "variable_entorno": "DEEPSEEK_API_KEY",
        "configurado": configurado,
        "motor_esperado": esperado,
        "casos": casos,
        "criterios": {
            "responde_sin_error": all(c["status"] == 200 for c in casos),
            "motor_correcto": all(c["motor"] == esperado for c in casos),
            "respuesta_no_vacia": all(bool(c["respuesta"]) for c in casos),
        },
    }
    evidencia["criterios"]["cumple_todos"] = all(evidencia["criterios"].values())
    return evidencia


if __name__ == "__main__":
    resultado = ejecutar()
    imprimir("P11 — Motor DeepSeek y respaldo por reglas", resultado)
    guardar("f11_deepseek.json", resultado)
