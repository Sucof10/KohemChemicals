import requests
from config import FULL_API_URL


def run_test():
    print("[*] SCRIPT 06: Detección de Inyección SQL (SQLi)")
    print("------------------------------------------------")

    materials_url = f"{FULL_API_URL}/materials"

    sqli_payloads = [
        "' OR '1'='1",
        "1; DROP TABLE users;--",
        "1' UNION SELECT NULL, NULL, NULL--",
        "admin'--"
    ]

    print("[*] Probando payloads de inyección SQL...\n")

    for payload in sqli_payloads:
        try:
            response = requests.get(
                f"{materials_url}/{requests.utils.quote(payload, safe='')}",
                timeout=10
            )

            response_text = response.text.lower()

            if response.status_code == 500:
                if any(error in response_text for error in [
                    "syntax error",
                    "sqlalchemy",
                    "sql syntax",
                    "sqlite",
                    "psycopg",
                    "mysql"
                ]):
                    print(
                        f"[ALERTA] Posible indicio de SQLi: {payload!r}"
                    )
                    print(f"Status HTTP: {response.status_code}")
                    print(f"Respuesta: {response.text[:300]}")
                else:
                    print(
                        f"[REVISAR] Error 500 con payload {payload!r}"
                    )

            else:
                print(
                    f"[INFO] Payload {payload!r} procesado. "
                    f"Status HTTP: {response.status_code}"
                )

        except requests.RequestException as error:
            print(f"[ERROR] Falló la petición: {error}")

    print("\n[*] Auditoría de SQLi finalizada.")


if __name__ == "__main__":
    run_test()