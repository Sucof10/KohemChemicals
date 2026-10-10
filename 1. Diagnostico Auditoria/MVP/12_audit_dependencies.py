import os
import subprocess
import sys
from config import REQUIREMENTS_FILE


def run_test():
    print("[*] SCRIPT 12: Auditoría de Dependencias Vulnerables (SAST)")
    print("-----------------------------------------------------------")

    # 1. Verificar que exista el archivo requirements.txt
    if not os.path.exists(REQUIREMENTS_FILE):
        print(
            f"[-] No se encontró el archivo "
            f"'{REQUIREMENTS_FILE}' en la ruta especificada."
        )
        print(f"[*] Directorio actual: {os.getcwd()}")
        return

    print(f"[+] Inspeccionando '{REQUIREMENTS_FILE}'...")

    try:
        # 2. Ejecutar pip-audit usando el mismo intérprete de Python
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip_audit",
                "-r",
                REQUIREMENTS_FILE
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        # 3. Analizar el resultado
        if result.returncode == 0:
            print(
                "[SUCCESS] pip-audit no reportó vulnerabilidades "
                "conocidas en las dependencias analizadas."
            )

            if result.stdout.strip():
                print(result.stdout)

        else:
            print("[!] REVISIÓN REQUERIDA EN DEPENDENCIAS:")

            if result.stdout.strip():
                print(result.stdout)

            if result.stderr.strip():
                print(result.stderr)

            print(
                "[INFO] Un código de salida distinto de cero puede "
                "indicar vulnerabilidades o un error de ejecución. "
                "Revisa el mensaje anterior."
            )

    except FileNotFoundError:
        print("[ERROR] No se pudo ejecutar Python para iniciar pip-audit.")

    except subprocess.TimeoutExpired:
        print(
            "[ERROR] El análisis superó los 120 segundos "
            "y fue interrumpido."
        )

    except OSError as error:
        print(f"[ERROR] No se pudo ejecutar la auditoría: {error}")

    # 4. Si pip-audit no está instalado, revisar las dependencias
    except Exception as error:
        print(f"[ERROR] Error inesperado: {error}")

    print("\n[*] Auditoría de dependencias finalizada.")


if __name__ == "__main__":
    run_test()