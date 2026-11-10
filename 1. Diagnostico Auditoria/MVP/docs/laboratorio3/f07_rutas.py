"""F07 - Auditoria automatizada de rutas del Frontend.

ADVERTENCIA METODOLOGICA
------------------------
Esta aplicacion es una SPA (React + BrowserRouter). El servidor de Vite
devuelve SIEMPRE el mismo index.html con HTTP 200, incluso para rutas que no
existen. Por eso, en este proyecto el codigo HTTP NO sirve para determinar:

  - si una ruta existe
  - si redirige
  - si requiere autenticacion

Este script demuestra esa limitacion con evidencia. La verificacion real de
rutas se hace en el navegador comprobando el contenido renderizado
(ver f07_rutas.json).

Uso:
    python f07_rutas.py [url_base]
"""

import hashlib
import sys

import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173"

RUTAS = [
    "/",
    "/login",
    "/materials",
    "/orders",
    "/audit-logs",
    "/ruta-inexistente-xyz",
]

CABECERAS_NAVEGADOR = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def main():
    print("=" * 72)
    print("F07 - RUTAS DEL FRONTEND (verificacion por codigo HTTP)")
    print(f"Base: {BASE}")
    print("=" * 72)

    huellas = {}
    print(f"\n{'RUTA':32} {'HTTP':6} {'BYTES':7} {'CONTENT-TYPE':18} HASH")
    print("-" * 72)
    for ruta in RUTAS:
        try:
            r = requests.get(BASE + ruta, timeout=8, allow_redirects=False,
                             headers=CABECERAS_NAVEGADOR)
        except requests.RequestException as error:
            print(f"{ruta:32} ERROR: {error}")
            continue

        huella = hashlib.md5(r.content).hexdigest()[:12]
        huellas[ruta] = huella
        print(f"{ruta:32} {r.status_code:<6} {len(r.content):<7} "
              f"{r.headers.get('Content-Type',''):18} {huella}")

    unicos = set(huellas.values())
    print("\nRESULTADO")
    print("-" * 72)
    print(f"Rutas probadas      : {len(huellas)}")
    print(f"Documentos distintos: {len(unicos)}")
    print(f"Ruta inexistente    : HTTP {requests.get(BASE + '/ruta-inexistente-xyz', timeout=8, headers=CABECERAS_NAVEGADOR, allow_redirects=False).status_code}")

    if len(unicos) == 1:
        print("\n[CONCLUSION] Todas las rutas devuelven el MISMO documento con HTTP 200.")
        print("             El codigo HTTP no distingue rutas existentes de inexistentes.")
        print("             Esta verificacion NO es suficiente en una SPA.")
        print("             La proteccion real se comprueba en el navegador (ver f07_rutas.json).")
    else:
        print("\n[CONCLUSION] Se detectaron respuestas distintas; revisar manualmente.")


if __name__ == "__main__":
    main()
