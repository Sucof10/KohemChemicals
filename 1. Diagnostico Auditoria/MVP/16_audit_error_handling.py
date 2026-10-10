import requests
from config import FULL_API_URL

def run_test():
    print("[*] SCRIPT 16 [ADICIONAL]: Auditoría de Manejo de Errores y Stack Traces")
    print("------------------------------------------------------------------------")
    
    # Provocar un error de servidor enviando un parámetro con tipo de dato inválido
    r = requests.get(f"{FULL_API_URL}/products/invalid_id_type")
    
    print(f"[*] Petición con parámetro inválido devolvió Status: {r.status_code}")
    if "Traceback (most recent call last)" in r.text or "sqlalchemy.exc" in r.text:
        print("[!] VULNERABILIDAD DE FUGA DE INFORMACIÓN: El servidor devuelve Stack Traces detallados.")
        print("    Deshabilita los detalles de depuración interna en entorno de producción.")
    else:
        print("[SUCCESS] El servidor maneja las excepciones sin filtrar la traza de ejecución.")
    print()

if __name__ == "__main__":
    run_test()