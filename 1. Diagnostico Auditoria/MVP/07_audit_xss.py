import requests
from config import FULL_API_URL, ADMIN_CREDS


def run_test():
    print("[*] SCRIPT 07: Auditoría de Cross-Site Scripting (XSS)")
    print("------------------------------------------------------")

    materials_url = f"{FULL_API_URL}/materials"
    item_id = None
    headers = {}

    xss_payload = "<script>alert('XSS_AUDIT_TEST')</script>"

    payload = {
        "name": xss_payload,
        "category": "Material de prueba",
        "unit": "kg",
        "price": 50.0,
        "stock": 5.0,
        "description": "Material temporal para auditoría XSS",
        "is_active": True
    }

    try:
        # 1. Autenticación como administrador
        auth_resp = requests.post(
            f"{FULL_API_URL}/auth/token",
            data=ADMIN_CREDS,
            timeout=10
        )

        if auth_resp.status_code != 200:
            print("[ERROR] No se pudo autenticar el administrador.")
            print(auth_resp.text)
            return

        auth = auth_resp.json()
        headers = {
            "Authorization": f"Bearer {auth['access_token']}"
        }

        print("[+] Autenticación exitosa.")

        # 2. Crear material con el payload de XSS
        create_resp = requests.post(
            materials_url,
            json=payload,
            headers=headers,
            timeout=10
        )

        print(f"[*] Código HTTP al crear: {create_resp.status_code}")

        if create_resp.status_code not in (200, 201):
            print("[INFO] No se pudo crear el material de prueba.")
            print(create_resp.text)
            return

        item_id = create_resp.json().get("id")

        if item_id is None:
            print("[ERROR] La respuesta no contiene el ID del material.")
            print(create_resp.text)
            return

        print(f"[+] Material de prueba creado. ID: {item_id}")

        # 3. Consultar el material almacenado
        get_resp = requests.get(
            f"{materials_url}/{item_id}",
            timeout=10
        )

        print(f"[*] Código HTTP al consultar: {get_resp.status_code}")

        if get_resp.status_code == 200:
            stored_name = get_resp.json().get("name")

            if stored_name == xss_payload:
                print(
                    "[ADVERTENCIA] El payload se almacena y devuelve "
                    "sin modificar."
                )
                print(
                    "[INFO] Esto no confirma por sí solo una vulnerabilidad "
                    "XSS ejecutable. El frontend debe mostrar el valor "
                    "como texto y evitar ejecutarlo como HTML."
                )
            else:
                print(
                    "[INFO] El nombre devuelto es diferente del payload "
                    "original o fue procesado por la API."
                )
        else:
            print("[INFO] No fue posible consultar el material.")
            print(get_resp.text)

    except requests.RequestException as error:
        print(f"[ERROR] Problema de conexión: {error}")

    except (ValueError, KeyError) as error:
        print(f"[ERROR] No se pudo procesar la respuesta: {error}")

    finally:
        # 4. Eliminar el material temporal
        if item_id is not None and headers:
            try:
                delete_resp = requests.delete(
                    f"{materials_url}/{item_id}",
                    headers=headers,
                    timeout=10
                )

                if delete_resp.status_code in (200, 204):
                    print("[+] Material de prueba eliminado.")
                else:
                    print(
                        "[INFO] No se pudo eliminar el material: "
                        f"{delete_resp.status_code} - {delete_resp.text}"
                    )

            except requests.RequestException as error:
                print(f"[ERROR] Falló la limpieza: {error}")

    print("\n[*] Auditoría de XSS finalizada.")


if __name__ == "__main__":
    run_test()