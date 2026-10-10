import os
import re
from config import PROJECT_ROOT_DIR

def run_test():
    print("[*] SCRIPT 14: Auditoría de Secretos y Variables Hardcodeadas")
    print("-------------------------------------------------------------")
    
    secret_patterns = [
        (r'SECRET_KEY\s*=\s*["\']([^"\']+)["\']', "Clave Secreta Hardcodeada"),
        (r'PASSWORD\s*=\s*["\']([^"\']+)["\']', "Contraseña Hardcodeada"),
        (r'postgres://|mysql://|sqlite://', "Cadena de conexión a Base de Datos expuesta")
    ]

    for root, _, files in os.walk(PROJECT_ROOT_DIR):
        for file in files:
            if file.endswith(".py") or file == ".env":
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern, desc in secret_patterns:
                            if re.search(pattern, line, re.IGNORECASE) and "settings" not in line.lower():
                                print(f"[!] POSIBLE SECRETO EXPUESTO [{desc}] en {filepath}:{line_num}")
    print()

if __name__ == "__main__":
    run_test()