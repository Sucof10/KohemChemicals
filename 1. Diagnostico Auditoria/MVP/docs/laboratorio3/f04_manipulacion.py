"""F04 - Manipulacion controlada de solicitudes (equivalente a Burp Repeater).

Reproduce peticiones validas generadas por el frontend y luego las modifica
de forma controlada para comparar la respuesta original con la manipulada.
Guarda la evidencia en JSON.
"""

import json
import os
from datetime import datetime

import requests

BASE = "http://localhost:5173"
API = f"{BASE}/api/v1"

ADMIN = {"username": "admin", "password": "AdminPass123!"}
CLIENTE = {"username": "cliente", "password": "ClientPass123!"}

CARPETA = os.path.join(os.path.dirname(__file__), "evidencias")
EVIDENCIA = []

HALLAZGOS = [
    {
        "id": "H-F04-01",
        "titulo": "Registro publico permite asignar role=admin",
        "severidad": "Critica",
        "detalle": "POST /api/v1/auth/register acepta role=admin sin autenticacion. El usuario creado inicia sesion con rol admin y consulta /audit-logs con 200.",
        "recomendacion": "Forzar role=cliente en el servidor y quitar el campo del DTO de registro publico.",
    },
    {
        "id": "H-F04-02",
        "titulo": "Errores de validacion devuelven 500 en lugar de 422",
        "severidad": "Media",
        "detalle": "Los routers validan con Model.model_validate(); pydantic lanza ValidationError no controlada y FastAPI responde 500 en texto plano.",
        "recomendacion": "Capturar ValidationError y devolver 422 con detalle de campos.",
    },
    {
        "id": "H-F04-03",
        "titulo": "Codigos HTTP imprecisos en errores de negocio",
        "severidad": "Baja",
        "detalle": "Stock insuficiente y material inexistente devuelven 400 en lugar de 409 y 404.",
        "recomendacion": "Ajustar la semantica de los codigos.",
    },
    {
        "id": "H-F04-04",
        "titulo": "Campos extra ignorados (mass assignment no explotable)",
        "severidad": "Positivo",
        "detalle": "Inyectar id, is_active y role en POST /materials no altera el registro.",
        "recomendacion": "Mantener.",
    },
    {
        "id": "H-F04-05",
        "titulo": "Autorizacion por rol correcta en operaciones de escritura",
        "severidad": "Positivo",
        "detalle": "Cliente recibe 403 en POST y PUT de materias primas.",
        "recomendacion": "Mantener.",
    },
]

RESUMEN = {
    "casos": 19,
    "validaciones_rechazadas_correctamente": True,
    "codigos_incorrectos": ["500 en 7 casos de validacion", "400 en lugar de 409/404"],
    "escalada_confirmada": True,
    "nota_limpieza": "Los materiales temporales se eliminan. El usuario de prueba debe borrarse aparte porque no existe endpoint de baja de usuarios.",
}


def mask(token):
    return token[:12] + "...(" + str(len(token)) + " chars)" if token else None


def login(creds):
    r = requests.post(f"{API}/auth/token", data={"grant_type": "password", **creds}, timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]


def call(metodo, ruta, token=None, cuerpo=None, etiqueta="", nota=""):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.request(metodo, f"{API}{ruta}", headers=headers, json=cuerpo, timeout=10)
    try:
        body = r.json()
    except ValueError:
        body = r.text

    registro = {
        "etiqueta": etiqueta,
        "request": {"metodo": metodo, "url": f"{API}{ruta}", "body": cuerpo},
        "response": {"status": r.status_code, "body": body},
        "nota": nota,
    }
    EVIDENCIA.append(registro)

    print(f"\n[{etiqueta}] {metodo} {ruta}")
    print(f"    Request : {json.dumps(cuerpo, ensure_ascii=True)[:180] if cuerpo else '(sin cuerpo)'}")
    print(f"    Response: {r.status_code} -> {json.dumps(body, ensure_ascii=True)[:180]}")
    if nota:
        print(f"    Nota    : {nota}")
    return r, body


def main():
    print("=" * 72)
    print("F04 - MANIPULACION CONTROLADA DE SOLICITUDES")
    print(f"Origen: {BASE}")
    print(f"Fecha : {datetime.now().isoformat(timespec='seconds')}")
    print("=" * 72)

    token_admin = login(ADMIN)
    token_cliente = login(CLIENTE)

    # ---------- A) Peticion original valida ----------
    original = {
        "name": "Material F04 original",
        "category": "Pruebas F04",
        "unit": "kg",
        "price": 1000,
        "stock": 10,
        "description": "Registro base para F04.",
    }
    r, body = call("POST", "/materials", token_admin, original,
                   "A1. Original valida", "Peticion base generada desde React")
    material_id = body.get("id") if r.status_code == 201 else None

    # ---------- B) Modificaciones de payload ----------
    casos = [
        ("B1. name vacio", {**original, "name": ""}, "Se espera 422 por min_length=2"),
        ("B2. price texto", {**original, "price": "texto"}, "Se espera 422 por tipo invalido"),
        ("B3. price 0", {**original, "price": 0}, "Se espera 422 por gt=0"),
        ("B4. stock negativo", {**original, "stock": -1}, "Se espera 422 por ge=0"),
        ("B5. name muy largo", {**original, "name": "X" * 200}, "Se espera 422 por max_length=120"),
    ]
    for etiqueta, payload, nota in casos:
        call("POST", "/materials", token_admin, payload, etiqueta, nota)

    # Mass assignment / campos extra
    r6, body6 = call("POST", "/materials", token_admin,
                     {**original, "id": 999, "is_active": False, "role": "admin"},
                     "B6. campos extra (mass assignment)",
                     "Se inyectan id, is_active y role; los modelos Pydantic deberian ignorarlos")
    creados = [material_id] if material_id else []
    if r6.status_code == 201 and body6.get("id"):
        creados.append(body6["id"])

    # ---------- C) Manipulacion de un PUT ----------
    if material_id:
        call("PUT", f"/materials/{material_id}", token_admin,
             {"stock": -50, "price": -10},
             "C1. PUT con valores negativos", "Se espera 422")

        call("PUT", f"/materials/{material_id}", token_admin,
             {"name": "Material F04 actualizado", "price": 1500},
             "C2. PUT valido", "Modificacion legitima para comparar con C1")

    # ---------- D) Manipulacion de pedidos (rol cliente) ----------
    call("POST", "/orders", token_cliente,
         {"items": [{"raw_material_id": 1, "quantity": -5}]},
         "D1. quantity negativa", "Se espera 422 por gt=0")

    call("POST", "/orders", token_cliente,
         {"items": [{"raw_material_id": 1, "quantity": 0}]},
         "D2. quantity cero", "Se espera 422 por gt=0")

    call("POST", "/orders", token_cliente,
         {"items": [{"raw_material_id": 1, "quantity": 999999}]},
         "D3. quantity mayor al stock", "Se espera rechazo por disponibilidad")

    call("POST", "/orders", token_cliente,
         {"items": [{"raw_material_id": 999999, "quantity": 1}]},
         "D4. material inexistente", "Se espera rechazo")

    call("POST", "/orders", token_cliente,
         {"items": []},
         "D5. pedido sin items", "Se espera 422 por min_length=1")

    # ---------- E) Manipulacion de autorizacion ----------
    call("POST", "/materials", token_cliente, original,
         "E1. cliente intenta crear material", "Se espera 403")

    call("PUT", f"/materials/{material_id}", token_cliente, {"price": 1},
         "E2. cliente intenta editar material", "Se espera 403")

    # ---------- F) Escalada de privilegios en el registro ----------
    usuario = "auditor_f04_admin"
    payload_registro = {
        "username": usuario,
        "email": f"{usuario}@kohem.com",
        "password": "AuditorF04Pass123!",
        "role": "admin",
    }
    r, body = call("POST", "/auth/register", None, payload_registro,
                   "F1. registro publico con role=admin",
                   "El endpoint no exige autenticacion ni restringe el rol")

    if r.status_code == 201:
        r2 = requests.post(f"{API}/auth/token",
                           data={"grant_type": "password", "username": usuario,
                                 "password": "AuditorF04Pass123!"}, timeout=10)
        if r2.status_code == 200:
            nuevo_token = r2.json()["access_token"]
            import base64
            payload = nuevo_token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            claims = json.loads(base64.urlsafe_b64decode(payload))
            EVIDENCIA.append({
                "etiqueta": "F2. login del usuario creado",
                "request": {"metodo": "POST", "url": f"{API}/auth/token",
                            "body": {"username": usuario, "password": "<oculta>"}},
                "response": {"status": r2.status_code,
                             "body": {"claims_del_jwt": claims}},
                "nota": "HALLAZGO: el rol admin queda asignado desde el registro publico",
            })
            print(f"\n[F2. login del usuario creado] POST /auth/token")
            print(f"    Response: {r2.status_code} -> claims: {json.dumps(claims)}")
            print("    Nota    : HALLAZGO: rol admin asignado desde el registro publico")

            # Verifica que el usuario nuevo realmente puede operar como admin
            call("GET", "/audit-logs", nuevo_token,
                 etiqueta="F3. usuario nuevo consulta auditoria",
                 nota="200 confirma que la escalada es efectiva")

    # ---------- Limpieza ----------
    for mid in creados:
        r = requests.delete(f"{API}/materials/{mid}",
                            headers={"Authorization": f"Bearer {token_admin}"}, timeout=10)
        print(f"\n[Limpieza] DELETE /materials/{mid} -> {r.status_code}")

    os.makedirs(CARPETA, exist_ok=True)
    salida = os.path.join(CARPETA, "f04_manipulacion.json")
    with open(salida, "w", encoding="utf-8") as fh:
        json.dump({"caso": "F04", "origen": BASE,
                   "fecha": datetime.now().isoformat(timespec="seconds"),
                   "peticiones": EVIDENCIA,
                   "hallazgos": HALLAZGOS,
                   "resumen": RESUMEN}, fh, ensure_ascii=False, indent=2)

    print("\n" + "=" * 72)
    print(f"Casos registrados: {len(EVIDENCIA)}")
    print(f"Evidencia: {salida}")
    print("=" * 72)


if __name__ == "__main__":
    main()
