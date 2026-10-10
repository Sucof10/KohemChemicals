import requests
from config import FULL_API_URL, ADMIN_CREDS

def run_test():
    print("[*] SCRIPT 02: Auditoría de Autenticación")
    print("-----------------------------------------")
    
    # 1. Autenticación válida
    resp = requests.post(f"{FULL_API_URL}/auth/token", data=ADMIN_CREDS)
    if resp.status_code == 200:
        data = resp.json()
        print("[+] Autenticación exitosa. Se obtuvo el token JWT.")
        token = data.get("access_token")
        
        # Analizar estructura básica de JWT sin verificar firma
        parts = token.split(".")
        if len(parts) == 3:
            print("[+] Formato de Token JWT estructuralmente válido (Header.Payload.Signature).")
    else:
        print(f"[-] Fallo en autenticación legítima: {resp.status_code}")

    # 2. Intento con credenciales inválidas
    bad_resp = requests.post(f"{FULL_API_URL}/auth/token", data={"username": "admin", "password": "WrongPassword!"})
    if bad_resp.status_code == 401:
        print("[SUCCESS] Rechazo correcto de contraseña errónea (401 Unauthorized).")
    else:
        print(f"[!] ADVERTENCIA: Status inesperado para login fallido ({bad_resp.status_code}).")
    print()

if __name__ == "__main__":
    run_test()