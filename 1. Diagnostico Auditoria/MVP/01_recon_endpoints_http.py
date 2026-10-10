import requests
from config import BASE_URL, FULL_API_URL

def run_test():
    print("[*] SCRIPT 01: Reconocimiento de Endpoints y Métodos HTTP")
    print("-------------------------------------------------------")
    
    # 1. Comprobación del estado base de la API
    try:
        r = requests.get(f"{BASE_URL}/")
        print(f"[+] Endpoint Raíz ('/'): Status {r.status_code}")
    except requests.exceptions.ConnectionError:
        print("[!] ERROR: No se puede conectar al servidor FastAPI. Asegúrate de que está ejecutándose.")
        return

    # 2. Descubrimiento de documentación OpenAPI / Swagger
    docs_r = requests.get(f"{BASE_URL}/docs")
    if docs_r.status_code == 200:
        print("[!] NOTA DE SEGURIDAD: La documentación Swagger UI (/docs) está activa y accesible publicamente.")
    
    openapi_r = requests.get(f"{BASE_URL}/openapi.json")
    if openapi_r.status_code == 200:
        print("[+] Esquema OpenAPI expuesto en '/openapi.json'.")

    # 3. Mapeo de métodos HTTP en endpoints de negocio
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
    for m in methods:
        resp = requests.request(m, f"{FULL_API_URL}/products")
        print(f"    - Método {m:<7} en /products -> Status {resp.status_code}")
    print()

if __name__ == "__main__":
    run_test()