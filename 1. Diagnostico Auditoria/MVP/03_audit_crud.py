import requests
from config import FULL_API_URL, ADMIN_CREDS


def run_test():
    print("[*] SCRIPT 03: Auditoría de Operaciones CRUD")
    print("-------------------------------------------")

    # Obtener token de administración
    auth_resp = requests.post(
        f"{FULL_API_URL}/auth/token",
        data=ADMIN_CREDS
    )

    assert auth_resp.status_code == 200, "Error al autenticar administrador"

    auth = auth_resp.json()
    headers = {
        "Authorization": f"Bearer {auth.get('access_token')}"
    }

    # Ruta base de materiales
    materials_url = f"{FULL_API_URL}/materials"

    # 1. CREATE
    payload = {
        "name": "Niacinamida Prueba CRUD",
        "category": "Humectantes",
        "unit": "kg",
        "price": 100000.0,
        "stock": 10.0,
        "description": "Materia prima para formulaciones cosméticas.",
        "is_active": True
    }

    c_resp = requests.post(
        materials_url,
        json=payload,
        headers=headers
    )

    print(f"CREATE Status: {c_resp.status_code}")
    print(f"CREATE Respuesta: {c_resp.text}")

    assert c_resp.status_code == 201, "Error al crear material"

    item_id = c_resp.json()["id"]
    print(f"[+] CREATE: Material creado con ID {item_id}")

    # 2. READ
    r_resp = requests.get(
        f"{materials_url}/{item_id}",
        headers=headers
    )

    assert r_resp.status_code == 200, "Error al consultar material"

    print(
        f"[+] READ: Obtenido correctamente "
        f"'{r_resp.json()['name']}'"
    )

    # 3. UPDATE
    u_resp = requests.put(
        f"{materials_url}/{item_id}",
        json={"price": 89999.0},
        headers=headers
    )

    assert u_resp.status_code == 200, "Error al actualizar material"

    print(
        f"[+] UPDATE: Precio actualizado a "
        f"{u_resp.json()['price']}"
    )

    # 4. DELETE
    d_resp = requests.delete(
        f"{materials_url}/{item_id}",
        headers=headers
    )

    assert d_resp.status_code == 204, "Error al eliminar material"

    print("[+] DELETE: Material eliminado exitosamente.")
    print("\n[+] Prueba CRUD finalizada correctamente.")


if __name__ == "__main__":
    run_test()