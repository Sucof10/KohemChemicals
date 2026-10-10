import requests
from config import FULL_API_URL


def run_test():
    print("[*] SCRIPT 08: Auditoría de Limitación de Tasa (Rate Limiting)")
    print("--------------------------------------------------------------")

    # Endpoint correcto de materiales
    materials_url = f"{FULL_API_URL}/materials"

    print("[*] Enviando 30 peticiones consecutivas...")
    statuses = []

    try:
        for i in range(30):
            response = requests.get(
                materials_url,
                timeout=10
            )

            statuses.append(response.status_code)

            print(
                f"Petición {i + 1}: "
                f"HTTP {response.status_code}"
            )

        # Analizar las respuestas
        if 429 in statuses:
            print(
                "\n[SUCCESS] Se detectó Rate Limiting: "
                "el servidor devolvió HTTP 429 "
                "(Too Many Requests)."
            )
        else:
            print(
                "\n[AVISO] No se detectó limitación de tasa "
                "en las 30 peticiones realizadas."
            )
            print(
                "Se recomienda evaluar la configuración de "
                "Rate Limiting para prevenir abusos de la API."
            )

        print(f"[*] Total de peticiones: {len(statuses)}")
        print(f"[*] Respuestas HTTP 429: {statuses.count(429)}")

    except requests.RequestException as error:
        print(f"[ERROR] No se pudo completar la prueba: {error}")

    print("\n[*] Auditoría de Rate Limiting finalizada.")


if __name__ == "__main__":
    run_test()