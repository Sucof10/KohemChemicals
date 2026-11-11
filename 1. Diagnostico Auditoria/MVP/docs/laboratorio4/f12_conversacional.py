"""P12 — Modo conversacional.

Levanta una segunda instancia del backend en el puerto 8001 con
AI_MODE=conversacional, mantiene un diálogo de varios turnos y verifica que:

* la respuesta llega con el motor configurado;
* los datos de la cotización viajan estructurados en el campo ``datos``;
* el historial se acepta sin romper el contrato;
* sin clave de DeepSeek el sistema sigue respondiendo (plantilla + reglas).
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx

RAIZ_MVP = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_MVP))
# Leer el .env del MVP aunque el script se ejecute desde docs/laboratorio4.
os.chdir(RAIZ_MVP)

from _common import guardar, imprimir
from app.infrastructure.config import settings

PUERTO = 8001
BASE_LOCAL = f"http://127.0.0.1:{PUERTO}/api/v1"


def _esperar_servidor(intentos: int = 40) -> bool:
    for _ in range(intentos):
        try:
            if httpx.get(f"http://127.0.0.1:{PUERTO}/", timeout=2).status_code == 200:
                return True
        except httpx.HTTPError:
            pass
        time.sleep(0.5)
    return False


def _token() -> str:
    respuesta = httpx.post(
        f"{BASE_LOCAL}/auth/token",
        data={"grant_type": "password", "username": "cliente", "password": "ClientPass123!"},
        timeout=10,
    )
    respuesta.raise_for_status()
    return respuesta.json()["access_token"]


def _chat(mensaje: str, cabecera: dict, historial: list[dict] | None = None) -> dict:
    cuerpo = {"message": mensaje}
    if historial:
        cuerpo["historial"] = historial
    respuesta = httpx.post(f"{BASE_LOCAL}/ai/chat", json=cuerpo, headers=cabecera, timeout=60)
    datos = respuesta.json() if respuesta.headers.get("content-type", "").startswith("application/json") else {}
    return {
        "mensaje": mensaje,
        "status": respuesta.status_code,
        "respuesta": datos.get("response"),
        "motor": datos.get("motor"),
        "transfer": datos.get("transfer_to_employee"),
        "datos": datos.get("datos"),
    }


def ejecutar() -> dict:
    entorno = {**os.environ, "AI_MODE": "conversacional", "PYTHONIOENCODING": "utf-8"}
    registro = Path(os.environ.get("TEMP", ".")) / "kohem_conv_8001.log"
    with open(registro, "w", encoding="utf-8") as log:
        proceso = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.presentation.main:app", "--port", str(PUERTO)],
            cwd=RAIZ_MVP,
            env=entorno,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            if not _esperar_servidor():
                return {"error": "El servidor conversacional no inició", "log": str(registro)}
            cabecera = {"Authorization": f"Bearer {_token()}"}

            saludo = _chat("Buenas tardes", cabecera)
            cotizacion = _chat("Quiero dos kilos de glicerina", cabecera)
            historial = [
                {"role": "user", "content": "Quiero dos kilos de glicerina"},
                {"role": "assistant", "content": cotizacion["respuesta"] or ""},
            ]
            seguimiento = _chat("¿Y cuánto hay de ese material?", cabecera, historial)
        finally:
            proceso.terminate()
            try:
                proceso.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proceso.kill()

    configurado = bool(settings.DEEPSEEK_API_KEY.strip())
    esperado = "deepseek-conversacional" if configurado else "reglas"
    casos = [saludo, cotizacion, seguimiento]
    evidencia = {
        "modo": "conversacional",
        "proveedor": "DeepSeek",
        "configurado": configurado,
        "motor_esperado": esperado,
        "casos": casos,
        "criterios": {
            "responde_sin_error": all(c["status"] == 200 for c in casos),
            "motor_correcto": all(c["motor"] == esperado for c in casos),
            "datos_estructurados": cotizacion.get("datos", {}).get("tipo") == "cotizacion",
            "datos_calculados_por_dominio": cotizacion.get("datos", {}).get("total") == 36000.0,
            "acepta_historial": seguimiento["status"] == 200,
        },
    }
    evidencia["criterios"]["cumple_todos"] = all(evidencia["criterios"].values())
    return evidencia


if __name__ == "__main__":
    resultado = ejecutar()
    imprimir("P12 — Modo conversacional", resultado)
    guardar("f12_conversacional.json", resultado)
