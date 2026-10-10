import os
from config import PROJECT_ROOT_DIR

def run_test():
    print("[*] SCRIPT 15: Auditoría de Fuga de Información en Logs")
    print("--------------------------------------------------------")
    
    sensitive_keywords = ["password", "token", "authorization", "secret_key", "credit_card"]
    print("[*] Verificando llamadas de logging que puedan exponer datos sensibles...")

    for root, _, files in os.walk(PROJECT_ROOT_DIR):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        if "print(" in line or "logger." in line or "logging." in line:
                            for kw in sensitive_keywords:
                                if kw in line.lower():
                                    print(f"[!] REVISIÓN DE LOGS: Impresión de variable sensible ('{kw}') en {filepath}:{line_num}")
    print()

if __name__ == "__main__":
    run_test()