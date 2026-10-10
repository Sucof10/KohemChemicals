import requests
from config import FULL_API_URL, ADMIN_CREDS


def run_test():
    print("[*] SCRIPT 05: Auditoría de Mass Assignment (Asignación Masiva)")
    print("----------------------------------------------------------------")

    # URL correcta de la API
    materials_url = f"{FULL_API_URL}/materials"
    target_id = None
    headers = {}

    try:
        # 1. Autenticación como administrador
        auth_resp = requests.post(
            f"{FULL_API_URL}/auth/token",
            data=ADMIN_CREDS
        )

        if auth_resp.status_code != 200:
            print("[ERROR] No se pudo autenticar el administrador.")
            print(f"Status: {auth_resp.status_code}")
            print(f"Respuesta: {auth_resp.text}")
            return

        auth = auth_resp.json()
        headers = {
            "Authorization": f"Bearer {auth['access_token']}"
        }

        print("[+] Autenticación exitosa.")

        # 2. Crear material con campos adicionales
        payload_extra_fields = {
            "name": "Material Test Mass Assignment",
            "category": "Humectantes",
            "unit": "kg",
            "price": 120.0,
            "stock": 5.0,
            "description": "Material temporal para auditoría",
            "is_active": True,

            # Campos adicionales para la prueba
            "is_admin": True,
            "internal_discount": 100.0,
            "role": "superuser"
        }

        resp = requests.post(
            materials_url,
            json=payload_extra_fields,
            headers=headers
        )

        print(f"\n[*] Endpoint evaluado: POST {materials_url}")
        print(f"[*] Código HTTP: {resp.status_code}")
        print(f"[*] Respuesta de la API: {resp.text}")

        # 3. Evaluar la respuesta
        if resp.status_code in (200, 201):
            data = resp.json()
            target_id = data.get("id")

            campos_protegidos = [
                "is_admin",
                "internal_discount",
                "role"
            ]

            campos_aceptados = [
                campo
                for campo in campos_protegidos
                if campo in data
            ]

            if campos_aceptados:
                print(
                    "\n[ALERTA] La respuesta contiene campos adicionales: "
                    f"{campos_aceptados}"
                )
                print(
                    "[!] Es necesario verificar si esos campos "
                    "se guardaron o modificaron datos."
                )
            else:
                print(
                    "\n[INFO] Los campos adicionales no aparecen "
                    "en la respuesta."
                )
                print(
                    "[INFO] Verifica también la base de datos para "
                    "confirmar que no fueron almacenados."
                )

        else:
            print(
                "\n[INFO] La API rechazó la solicitud o devolvió un error."
            )
            print(
                "[INFO] Revisa el código HTTP y el mensaje "
                "para determinar la causa."
            )

    except requests.RequestException as error:
        print(f"[ERROR] Problema de conexión con la API: {error}")

    except (ValueError, KeyError) as error:
        print(f"[ERROR] No se pudo procesar la respuesta: {error}")

    finally:
        # 4. Eliminar el material temporal, si fue creado
        if target_id is not None:
            try:
                delete_resp = requests.delete(
                    f"{materials_url}/{target_id}",
                    headers=headers
                )

                if delete_resp.status_code in (200, 204):
                    print("\n[+] Material de prueba eliminado.")
                else:
                    print(
                        "\n[INFO] No se pudo eliminar el material: "
                        f"{delete_resp.status_code} - {delete_resp.text}"
                    )

            except requests.RequestException as error:
                print(f"[ERROR] Falló la limpieza del recurso: {error}")

    print("\n[*] Auditoría de Mass Assignment finalizada.")


if __name__ == "__main__":
    run_test()