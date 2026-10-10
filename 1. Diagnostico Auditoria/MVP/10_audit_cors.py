import requests
from config import FULL_API_URL


def run_test():
    print(
        "[*] SCRIPT 10: Verificación de Políticas CORS "
        "(Cross-Origin Resource Sharing)"
    )
    print("------------------------------------------------------------")

    # Endpoint correcto de materiales
    materials_url = f"{FULL_API_URL}/materials"

    # Simular una solicitud desde un origen externo no confiable
    headers = {
        "Origin": "http://sitio-malicioso-ejemplo.com",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type"
    }

    try:
        # Enviar solicitud OPTIONS para revisar la política CORS
        response = requests.options(
            materials_url,
            headers=headers,
            timeout=10
        )

        allow_origin = response.headers.get(
            "Access-Control-Allow-Origin"
        )
        allow_methods = response.headers.get(
            "Access-Control-Allow-Methods"
        )
        allow_credentials = response.headers.get(
            "Access-Control-Allow-Credentials"
        )

        print(f"[*] Endpoint evaluado: {materials_url}")
        print(f"[*] Código HTTP: {response.status_code}")
        print(
            f"[*] Access-Control-Allow-Origin: {allow_origin}"
        )
        print(
            f"[*] Access-Control-Allow-Methods: {allow_methods}"
        )
        print(
            f"[*] Access-Control-Allow-Credentials: {allow_credentials}"
        )

        # Evaluar la respuesta CORS
        if allow_origin == "*":
            print(
                "\n[AVISO] CORS permite cualquier origen mediante '*'."
            )
            print(
                "Revisa si esta política es apropiada para los recursos "
                "y credenciales que utiliza la API."
            )

        elif allow_origin == headers["Origin"]:
            print(
                "\n[AVISO] La API permite el origen de prueba no confiable."
            )
            print(
                "Verifica si el servidor refleja orígenes arbitrarios "
                "o si ese origen está autorizado explícitamente."
            )

        elif allow_origin is None:
            print(
                "\n[INFO] No se encontró la cabecera "
                "Access-Control-Allow-Origin."
            )
            print(
                "La respuesta no demuestra por sí sola que CORS esté "
                "configurado correctamente; revisa también el preflight."
            )

        else:
            print(
                "\n[INFO] La API devolvió un origen diferente al "
                "origen de prueba."
            )

        if allow_credentials == "true" and allow_origin == "*":
            print(
                "[ALERTA] Revisa la combinación de origen comodín "
                "y credenciales. Los navegadores no permiten usar "
                "Access-Control-Allow-Origin: * con credenciales."
            )

    except requests.RequestException as error:
        print(f"[ERROR] No se pudo completar la prueba: {error}")

    print("\n[*] Auditoría de CORS finalizada.")


if __name__ == "__main__":
    run_test()