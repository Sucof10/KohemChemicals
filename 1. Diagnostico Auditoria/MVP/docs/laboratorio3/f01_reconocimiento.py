"""F01 - Reconocimiento funcional del Frontend.

Ejecuta el flujo real de la SPA contra el origen del frontend (Vite en :5173),
de modo que las peticiones son identicas a las que genera React en el navegador.
Guarda la evidencia en JSON para el informe.
"""

import json
import os
import time
from datetime import datetime

import requests

BASE = "http://localhost:5173"
API = f"{BASE}/api/v1"

CLIENTE = {"username": "cliente", "password": "ClientPass123!"}
ADMIN = {"username": "admin", "password": "AdminPass123!"}

EVIDENCIAS = []
CARPETA = os.path.join(os.path.dirname(__file__), "evidencias")


def mask(value: str) -> str:
    if not value:
        return ""
    return value[:12] + "...(" + str(len(value)) + " chars)"


def registrar(paso, metodo, url, resp, cuerpo=None, nota=""):
    req_headers = dict(resp.request.headers)
    if "Authorization" in req_headers:
        req_headers["Authorization"] = "Bearer " + mask(
            req_headers["Authorization"].replace("Bearer ", "")
        )

    try:
        respuesta = resp.json()
    except ValueError:
        respuesta = resp.text[:300]

    # Nunca exponer el token completo en la evidencia
    if isinstance(respuesta, dict) and "access_token" in respuesta:
        respuesta = {**respuesta, "access_token": mask(respuesta["access_token"])}

    item = {
        "paso": paso,
        "metodo": metodo,
        "url": url,
        "status": resp.status_code,
        "request_headers": req_headers,
        "request_body": cuerpo,
        "response_content_type": resp.headers.get("Content-Type"),
        "response_body": respuesta,
        "elapsed_ms": round(resp.elapsed.total_seconds() * 1000, 1),
        "nota": nota,
    }
    EVIDENCIAS.append(item)

    print(f"\n[{paso}] {metodo} {url}")
    print(f"    Status: {resp.status_code}  ({item['elapsed_ms']} ms)")
    print(f"    Content-Type respuesta: {resp.headers.get('Content-Type')}")
    print(f"    Authorization: {req_headers.get('Authorization', '(sin cabecera)')}")
    if cuerpo:
        print(f"    Request: {json.dumps(cuerpo, ensure_ascii=True)[:220]}")
    if isinstance(respuesta, list):
        print(f"    Response: lista con {len(respuesta)} elementos")
    else:
        print(f"    Response: {json.dumps(respuesta, ensure_ascii=True)[:220]}")
    if nota:
        print(f"    Nota: {nota}")
    return resp


def login(creds, etiqueta):
    r = requests.post(
        f"{API}/auth/token",
        data={"grant_type": "password", **creds},
        timeout=10,
    )
    registrar(
        etiqueta,
        "POST",
        f"{API}/auth/token",
        r,
        {"grant_type": "password", "username": creds["username"], "password": "***"},
        "Content-Type: application/x-www-form-urlencoded",
    )
    return r.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def main():
    print("=" * 70)
    print("F01 - RECONOCIMIENTO FUNCIONAL DEL FRONTEND")
    print(f"Origen auditado: {BASE}")
    print(f"Fecha: {datetime.now().isoformat(timespec='seconds')}")
    print("=" * 70)

    token_cliente = login(CLIENTE, "1. Login cliente")
    token_admin = login(ADMIN, "2. Login admin")

    r = requests.get(f"{API}/materials", headers=auth(token_cliente), timeout=10)
    registrar("3. Consultar materias primas", "GET", f"{API}/materials", r,
              nota="Pantalla /materials (visible para todos los roles)")

    r = requests.get(f"{API}/materials/1", headers=auth(token_cliente), timeout=10)
    registrar("4. Ver detalle de materia prima", "GET", f"{API}/materials/1", r,
              nota="Seleccion de un registro del catalogo")

    r = requests.get(f"{API}/orders", headers=auth(token_cliente), timeout=10)
    registrar("5. Consultar pedidos (cliente)", "GET", f"{API}/orders", r,
              nota="El cliente solo ve sus propios pedidos")

    r = requests.get(f"{API}/audit-logs", headers=auth(token_cliente), timeout=10)
    registrar("6. Intento de auditoria como cliente", "GET", f"{API}/audit-logs", r,
              nota="Control de acceso por rol: se espera 403")

    r = requests.get(f"{API}/audit-logs", headers=auth(token_admin), timeout=10)
    registrar("7. Auditoria como admin", "GET", f"{API}/audit-logs", r,
              nota="Pantalla /audit-logs (solo admin/analista)")

    nuevo = {
        "name": "Materia prima temporal F01",
        "category": "Pruebas",
        "unit": "kg",
        "price": 1000,
        "stock": 1,
        "description": "Registro creado por el script de auditoria F01.",
    }
    r = requests.post(f"{API}/materials", headers=auth(token_admin), json=nuevo, timeout=10)
    registrar("8. Crear materia prima (admin)", "POST", f"{API}/materials", r, nuevo,
              nota="CREATE del CRUD")
    material_id = r.json().get("id") if r.status_code < 300 else None

    if material_id:
        cambio = {"price": 1200, "stock": 5}
        r = requests.put(
            f"{API}/materials/{material_id}", headers=auth(token_admin), json=cambio, timeout=10
        )
        registrar("9. Actualizar materia prima (admin)", "PUT",
                  f"{API}/materials/{material_id}", r, cambio, "UPDATE del CRUD")

        r = requests.delete(
            f"{API}/materials/{material_id}", headers=auth(token_admin), timeout=10
        )
        registrar("10. Eliminar materia prima (admin)", "DELETE",
                  f"{API}/materials/{material_id}", r, None,
                  "DELETE del CRUD; deja la base como estaba")

    os.makedirs(CARPETA, exist_ok=True)
    salida = os.path.join(CARPETA, "f01_reconocimiento.json")
    with open(salida, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "caso": "F01",
                "origen": BASE,
                "fecha": datetime.now().isoformat(timespec="seconds"),
                "peticiones": EVIDENCIAS,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )

    print("\n" + "=" * 70)
    print(f"Total de peticiones registradas: {len(EVIDENCIAS)}")
    print(f"Evidencia guardada en: {salida}")
    print("=" * 70)


if __name__ == "__main__":
    main()
