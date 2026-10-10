import requests
from config import FULL_API_URL, ADMIN_CREDS


def run_test():
    print("[*] SCRIPT 09: Protección contra Abuso de Tamaño de Payload")
    print("-----------------------------------------------------------")

    # Endpoint correcto de materiales
    materials_url = f"{FULL_API_URL}/materials"

    try:
        # 1. Autenticación como administrador
        auth_resp = requests.post(
            f"{FULL_API_URL}/auth/token",
            data=ADMIN_CREDS,
            timeout=10
        )

        if auth_resp.status_code != 200:
            print("[ERROR] No se pudo autenticar el administrador.")
            print(f"Status: {auth_resp.status_code}")
            print(auth_resp.text)
            return

        auth = auth_resp.json()
        headers = {
            "Authorization": f"Bearer {auth['access_token']}"
        }

        print("[+] Autenticación exitosa.")

        # 2. Generar un payload de prueba de aproximadamente 5 MB
        large_string = "A" * (5 * 1024 * 1024)

        huge_payload = {
            "name": large_string,
            "category": "Material de prueba",
            "unit": "kg",
            "price": 50.0,
            "stock": 5.0,
            "description": "Prueba de límite de tamaño",
            "is_active": True
        }

        print("[*] Enviando payload de aproximadamente 5 MB...")

        # 3. Enviar la petición al endpoint de materiales
        response = requests.post(
            materials_url,
            json=huge_payload,
            headers=headers,
            timeout=15
        )

        print(f"[*] Código HTTP recibido: {response.status_code}")

        # 4. Analizar la respuesta
        if response.status_code == 413:
            print(
                "[SUCCESS] El servidor rechazó el payload por su tamaño "
                "(HTTP 413 - Content Too Large)."
            )

        elif response.status_code == 422:
            print(
                "[INFO] La API rechazó los datos por validación "
                "(HTTP 422). Esto no confirma por sí solo un límite "
                "de tamaño de petición."
            )

        elif response.status_code in (200, 201):
            print(
                "[AVISO] La API aceptó el payload grande. "
                "Verifica si existe un límite de tamaño configurado."
            )

        else:
            print(
                f"[INFO] Respuesta HTTP {response.status_code}: "
                f"{response.text[:300]}"
            )

    except requests.exceptions.Timeout:
        print(
            "[ADVERTENCIA] La petición superó el tiempo límite. "
            "Esto no demuestra por sí solo que el servidor se haya "
            "congelado."
        )

    except requests.exceptions.RequestException as error:
        print(f"[ERROR] Problema de conexión: {error}")

    except (ValueError, KeyError) as error:
        print(f"[ERROR] No se pudo procesar la respuesta: {error}")

    print("\n[*] Auditoría de tamaño de payload finalizada.")


if __name__ == "__main__":
    run_test()