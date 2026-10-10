import os

# Configuración de red para auditoría dinámica (DAST)
BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"
FULL_API_URL = f"{BASE_URL}{API_PREFIX}"

ADMIN_CREDS = {"username": "admin", "password": "AdminPass123!"}
CLIENT_CREDS = {"username": "cliente", "password": "ClientPass123!"}

# Rutas locales para auditoría de código fuente y archivos (SAST)
PROJECT_ROOT_DIR = "."  # Ruta raíz del proyecto FastAPI
REQUIREMENTS_FILE = "requirements.txt"
ENV_FILE = ".env"