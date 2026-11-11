"""Utilidades comunes de los scripts del Laboratorio 4.

Todos los scripts hablan con la API levantada en KOHEM_API (por defecto
http://127.0.0.1:8000) y guardan la evidencia cruda en ``evidencias/``.
"""

import json
import os
from pathlib import Path

import httpx

BASE = os.environ.get("KOHEM_API", "http://127.0.0.1:8000")
API = f"{BASE}/api/v1"
_evidencias = os.environ.get("LAB4_EVID", "evidencias")
EVIDENCIAS = Path(_evidencias)
if not EVIDENCIAS.is_absolute():
    EVIDENCIAS = Path(__file__).resolve().parent / EVIDENCIAS
EVIDENCIAS.mkdir(parents=True, exist_ok=True)
RAIZ_MVP = Path(__file__).resolve().parents[2]


def token(usuario: str, clave: str) -> str:
    respuesta = httpx.post(
        f"{API}/auth/token",
        data={"grant_type": "password", "username": usuario, "password": clave},
        timeout=10,
    )
    respuesta.raise_for_status()
    return respuesta.json()["access_token"]


def cabeceras(usuario: str = "cliente") -> dict:
    claves = {
        "admin": ("admin", "AdminPass123!"),
        "cliente": ("cliente", "ClientPass123!"),
    }
    usuario_api, clave = claves[usuario]
    return {"Authorization": f"Bearer {token(usuario_api, clave)}"}


def solicitud(metodo: str, ruta: str, **kwargs) -> dict:
    respuesta = httpx.request(metodo, f"{API}{ruta}", timeout=30, **kwargs)
    try:
        cuerpo = respuesta.json()
    except ValueError:
        cuerpo = respuesta.text
    return {
        "metodo": metodo.upper(),
        "ruta": ruta,
        "status": respuesta.status_code,
        "cuerpo": cuerpo,
    }


def guardar(nombre: str, datos: dict) -> Path:
    destino = EVIDENCIAS / nombre
    destino.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    return destino


def imprimir(titulo: str, datos: dict) -> None:
    print(f"\n=== {titulo} ===")
    print(json.dumps(datos, ensure_ascii=False, indent=2))
