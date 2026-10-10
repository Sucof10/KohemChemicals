import os
from config import PROJECT_ROOT_DIR


def run_test():
    print("[*] SCRIPT 13: Auditoría de Configuración General de FastAPI")
    print("------------------------------------------------------------")

    found_issues = False
    fastapi_instances = 0

    # 1. Recorrer los archivos del proyecto
    for root, dirs, files in os.walk(PROJECT_ROOT_DIR):
        # Excluir carpetas que no necesitan analizarse
        dirs[:] = [
            directory for directory in dirs
            if directory not in (
                "venv",
                ".venv",
                "__pycache__",
                ".git"
            )
        ]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)

                try:
                    with open(
                        filepath,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as f:
                        content = f.read()

                    # 2. Detectar instancias de FastAPI
                    if "FastAPI(" in content:
                        fastapi_instances += 1

                        print(
                            f"\n[+] Instancia de FastAPI detectada en: "
                            f"'{filepath}'"
                        )

                        # 3. Revisar configuración de documentación
                        docs_disabled = "docs_url=None" in content
                        redoc_disabled = "redoc_url=None" in content

                        if not docs_disabled or not redoc_disabled:
                            print(
                                "[!] ADVERTENCIA: Verifica si la "
                                "documentación de la API debe estar "
                                "deshabilitada en producción."
                            )

                            if not docs_disabled:
                                print(
                                    "    - No se detectó docs_url=None."
                                )

                            if not redoc_disabled:
                                print(
                                    "    - No se detectó redoc_url=None."
                                )

                            found_issues = True

                        else:
                            print(
                                "[SUCCESS] Se detectaron docs_url=None "
                                "y redoc_url=None."
                            )

                except OSError as error:
                    print(
                        f"[ERROR] No se pudo leer '{filepath}': {error}"
                    )

    # 4. Mostrar el resultado final
    print("\n---------------- RESULTADO DE AUDITORÍA ----------------")

    if fastapi_instances == 0:
        print(
            "[-] No se encontraron instancias de FastAPI "
            "en los archivos analizados."
        )

    elif not found_issues:
        print(
            "[+] Revisión básica finalizada. "
            "No se detectaron las advertencias evaluadas."
        )

    else:
        print(
            "[!] Se encontraron configuraciones que requieren revisión."
        )

    print(f"[*] Archivos con instancias detectadas: {fastapi_instances}")
    print("[*] Auditoría de configuración FastAPI finalizada.\n")


if __name__ == "__main__":
    run_test()