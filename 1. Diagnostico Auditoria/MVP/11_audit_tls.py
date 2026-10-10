import urllib.parse
from config import BASE_URL


def run_test():
    print("[*] SCRIPT 11: Auditoría de TLS / Cifrado en Transporte")
    print("-------------------------------------------------------")

    # Analizar la URL base de la API
    parsed = urllib.parse.urlparse(BASE_URL)

    if parsed.scheme.lower() != "https":
        print(
            f"[ALERTA] La API utiliza un canal no cifrado: "
            f"'{parsed.scheme}://'."
        )
        print(
            "[!] El tráfico HTTP no cifra los datos durante el transporte."
        )
        print(
            "[!] Las contraseñas y los tokens JWT podrían quedar expuestos "
            "si se transmiten por una red no confiable."
        )
        print(
            "[INFO] Para producción, configura HTTPS mediante TLS."
        )

    else:
        print("[SUCCESS] La URL de la API utiliza HTTPS.")
        print(
            "[INFO] Se recomienda verificar también el certificado TLS, "
            "su validez y la configuración del servidor."
        )

    print(f"\n[*] URL evaluada: {BASE_URL}")
    print("[*] Auditoría de TLS finalizada.\n")


if __name__ == "__main__":
    run_test()