
import requests
from config import FULL_API_URL, CLIENT_CREDS, ADMIN_CREDS


def run_test():
    print("[*] SCRIPT 04: Auditoría IDOR / BOLA")
    print("------------------------------------------------")

    materials_url = f"{FULL_API_URL}/materials"
    target_id = None

    # 1. Autenticar como administrador
    admin_response = requests.post(
        f"{FULL_API_URL}/auth/token",
        data=ADMIN_CREDS
    )
    assert admin_response.status_code == 200, (
        f"Error de autenticación admin: {admin_response.text}"
    )

    admin_auth = admin_response.json()
    admin_headers = {
        "Authorization": f"Bearer {admin_auth['access_token']}"
    }

    # 2. Crear material de prueba como administrador
    payload = {
        "name": "Material Prueba IDOR",
        "category": "Humectantes",
        "unit": "kg",
        "price": 500.0,
        "stock": 1.0,
        "description": "Material temporal para auditoría IDOR/BOLA",
        "is_active": True
    }

    create_response = requests.post(
        materials_url,
        json=payload,
        headers=admin_headers
    )

    print("CREATE Status:", create_response.status_code)
    print("CREATE Respuesta:", create_response.text)

    assert create_response.status_code == 201, (
        "No se pudo crear el material de prueba"
    )

    target_id = create_response.json()["id"]
    print(f"[+] Material de prueba creado: ID {target_id}")

    try:
        # 3. Autenticar como cliente
        client_response = requests.post(
            f"{FULL_API_URL}/auth/token",
            data=CLIENT_CREDS
        )
        assert client_response.status_code == 200, (
            f"Error de autenticación cliente: {client_response.text}"
        )

        client_auth = client_response.json()
        client_headers = {
            "Authorization": f"Bearer {client_auth['access_token']}"
        }

        # 4. Intentar modificar el material con la cuenta cliente
        mod_resp = requests.put(
            f"{materials_url}/{target_id}",
            json={"price": 1.0},
            headers=client_headers
        )

        if mod_resp.status_code == 403:
            print(
                "[SUCCESS] El cliente recibió 403. "
                "La modificación fue denegada."
            )
        elif mod_resp.status_code == 404:
            print(
                "[INFO] Se recibió 404. Verifica si la ruta PUT "
                "o el material existen."
            )
        elif mod_resp.status_code in (200, 204):
            print(
                "[ALERTA] El cliente pudo modificar el material. "
                "Revisa los controles de autorización."
            )
        else:
            print(
                f"[INFO] Respuesta PUT: {mod_resp.status_code} - "
                f"{mod_resp.text}"
            )

    finally:
        # 5. Eliminar el material de prueba como administrador
        if target_id is not None:
            delete_response = requests.delete(
                f"{materials_url}/{target_id}",
                headers=admin_headers
            )

            if delete_response.status_code in (200, 204):
                print("[+] Material de prueba eliminado.")
            else:
                print(
                    "[INFO] No se pudo limpiar el material: "
                    f"{delete_response.status_code} - "
                    f"{delete_response.text}"
                )

    print("[*] Prueba IDOR/BOLA finalizada.\n")


if __name__ == "__main__":
    run_test()
