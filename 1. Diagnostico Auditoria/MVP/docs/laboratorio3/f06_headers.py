"""F06 - Auditoria automatizada de cabeceras de seguridad del Frontend.

Version adaptada del script del laboratorio:
  - usa el puerto real del proyecto (5173, no 3000)
  - revisa las cabeceras que pide la guia y algunas adicionales
  - compara dev server, build de produccion y API

Uso:
    python f06_headers.py [url1 url2 ...]
"""

import json
import os
import sys
from datetime import datetime

import requests

CARPETA = os.path.join(os.path.dirname(__file__), "evidencias")

CABECERAS = {
    "Content-Security-Policy": "Mitiga XSS e inyeccion de contenido",
    "X-Content-Type-Options": "Evita el sniffing de tipos MIME",
    "X-Frame-Options": "Mitiga clickjacking",
    "Referrer-Policy": "Controla la fuga de URL de origen",
    "Permissions-Policy": "Restringe APIs del navegador",
    "Strict-Transport-Security": "Fuerza HTTPS (solo en produccion)",
}

OBJETIVOS = sys.argv[1:] or ["http://localhost:5173/"]


def analizar(url):
    print("=" * 72)
    print(f"OBJETIVO: {url}")
    print("=" * 72)

    try:
        r = requests.get(url, timeout=8)
    except requests.RequestException as error:
        print(f"[ERROR] {error}")
        return {"url": url, "error": str(error)}

    print(f"URL final : {r.url}")
    print(f"STATUS    : {r.status_code}")
    print(f"SERVER    : {r.headers.get('Server', '(sin cabecera)')}")
    print(f"POWERED-BY: {r.headers.get('X-Powered-By', '(sin cabecera)')}")

    print("\nCABECERAS RECIBIDAS")
    print("-" * 72)
    for nombre, valor in r.headers.items():
        print(f"{nombre}: {valor}")

    print("\nCABECERAS DE SEGURIDAD")
    print("-" * 72)
    resultado = {}
    for cabecera, descripcion in CABECERAS.items():
        presente = cabecera in r.headers
        estado = "[OK]     " if presente else "[REVISAR]"
        print(f"{estado} {cabecera}")
        print(f"           {descripcion}")
        resultado[cabecera] = {
            "presente": presente,
            "valor": r.headers.get(cabecera),
        }

    faltantes = [c for c, v in resultado.items() if not v["presente"]]
    print("\nRESUMEN")
    print("-" * 72)
    print(f"Presentes: {len(CABECERAS) - len(faltantes)}/{len(CABECERAS)}")
    print(f"Faltantes: {', '.join(faltantes) if faltantes else 'ninguna'}")

    return {
        "url": url,
        "url_final": r.url,
        "status": r.status_code,
        "server": r.headers.get("Server"),
        "headers": dict(r.headers),
        "seguridad": resultado,
        "faltantes": faltantes,
    }


def main():
    print(f"Fecha: {datetime.now().isoformat(timespec='seconds')}\n")
    salidas = [analizar(u) for u in OBJETIVOS]

    os.makedirs(CARPETA, exist_ok=True)
    ruta = os.path.join(CARPETA, "f06_headers.json")
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump({"caso": "F06", "fecha": datetime.now().isoformat(timespec="seconds"),
                   "objetivos": salidas}, fh, ensure_ascii=False, indent=2)
    print(f"\nEvidencia guardada en: {ruta}")


if __name__ == "__main__":
    main()
