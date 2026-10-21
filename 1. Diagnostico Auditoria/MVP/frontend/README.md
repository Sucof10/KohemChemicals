# Kohem Chemicals — Frontend MVP

SPA para consumir el backend FastAPI de Kohem Chemicals. Implementa autenticación con JWT,
dashboard por rol, catálogo de materias primas, pedidos, asesoría IA y auditoría, usando
**solo los endpoints que existen realmente** en el backend.

## Stack

- Node.js 24 LTS + Vite 8 + React 19 + TypeScript estricto.
- React Router, Axios, React Hook Form + Zod.
- Tailwind CSS 4.
- Vitest + Testing Library + MSW.

## Requisitos

- Node.js 24+ y npm 11+ (probado con Node 24.16.0 y npm 11.13.0).
- Backend ejecutable desde `../` con Python y su entorno virtual.

## Instalación

```bash
cd MVP/frontend
npm install
copy .env.example .env
```

En Linux/macOS:

```bash
cp .env.example .env
```

## Configuración del backend

El frontend usa `VITE_API_BASE_URL` (incluye el prefijo `/api/v1`).

### Desarrollo (sin CORS)

`.env`:

```env
VITE_API_BASE_URL=/api/v1
```

Vite reenvía `/api` a `http://127.0.0.1:8000` mediante el proxy configurado en
`vite.config.ts`. Levanta el backend:

```bash
cd ..   # carpeta MVP
venv\Scripts\python -m uvicorn app.presentation.main:app --reload
# Linux/macOS:
# venv/bin/python -m uvicorn app.presentation.main:app --reload
```

Y el frontend:

```bash
npm run dev
```

Abre `http://localhost:5173`.

En Windows puedes levantar ambos procesos con un solo comando:

```bash
npm run dev:all
```

Este script inicia el backend desde `../venv` si no está corriendo y luego arranca Vite. Al
cerrar Vite, detiene el backend que haya iniciado.

### Producción o backend en otro origen

El backend **no tiene CORS configurado** (verificado). Para usar una URL absoluta:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

es necesario añadir `CORSMiddleware` en el backend. El proxy de Vite es solo para desarrollo.

## Solución de problemas de conexión

Si al iniciar sesión aparece **“El servicio no está disponible. Verifica que el backend esté
en ejecución…”**, el proxy de Vite recibió un `502` porque el backend no está escuchando en
`http://127.0.0.1:8000`. Verifica:

```bash
# Debe responder {"status":"API Online",...}
Invoke-RestMethod http://127.0.0.1:8000/
```

Si no responde, inicia el backend desde `MVP`:

```bash
venv\Scripts\python -m uvicorn app.presentation.main:app --reload
```

o usa `npm run dev:all`. El frontend no puede autenticar sin el backend activo. Si ves un
error de red en lugar de `502`, revisa que `VITE_API_BASE_URL=/api/v1` en `.env` y que el
proxy de `vite.config.ts` apunte a `http://127.0.0.1:8000`.

## Usuarios de prueba

| Rol | Usuario | Contraseña | Origen |
|---|---|---|---|
| Administrador | `admin` | `AdminPass123!` | Seed del backend |
| Cliente | `cliente` | `ClientPass123!` | Seed del backend |
| Analista | — | — | No está seedeado |

El backend permite crear un `analista` con `POST /api/v1/auth/register` enviando
`"role": "analista"` desde Swagger o `curl`. El formulario del frontend **no expone el rol**
por seguridad y siempre crea `cliente`.

> **Hallazgo crítico del backend:** el registro público acepta `role`, incluido `admin`.
> Debe corregirse en el backend. El frontend no lo explota, pero la API sigue expuesta.

## Scripts

```bash
npm run dev            # desarrollo con proxy
npm run build          # typecheck + build de producción
npm run preview        # servir dist
npm run lint           # oxlint
npm run typecheck      # tsc -b
npm run test           # Vitest (35 pruebas)
npm run test:watch     # Vitest en modo watch
npm run test:coverage  # cobertura
```

## Funcionalidades

- Registro, login y logout local; token en `sessionStorage`.
- Dashboard según rol.
- Materiales: consulta para todos; crear/eliminar solo `admin`; editar `admin`/`analista`.
- Pedidos: el `cliente` crea, consulta y cancela los permitidos; `admin`/`analista` ven
  todos y cambian el estado. El total mostrado en el detalle es el del servidor.
- Asesoría IA con marca de transferencia a empleado.
- Auditoría de solo lectura para `admin`/`analista`.
- Guards de ruta y menú por rol; el backend sigue siendo la autoridad.
- Manejo de 401, 403, 404, 409, 422, 429, red y 500.
- Estados de carga, vacío y error en todas las vistas.

## No soportado por el backend (no se inventó)

- CRUD de usuarios y edición de perfil.
- Citas / agendamiento.
- Geografía (país, departamento, ciudad, sector).
- Refresh token, revocación y logout del servidor.
- Rate-limit / lockout de login.
- Soft delete / desactivación de materiales.
- Filtros de inventario y paginación con total.

La vista “Mi sesión” solo muestra los datos del JWT porque no existe `/users/me`.

## Seguridad

- URL de API solo por `VITE_API_BASE_URL`; `.env` está en `.gitignore`.
- Sin `dangerouslySetInnerHTML`.
- No se registran tokens ni datos sensibles en consola.
- El token vive en `sessionStorage` (por pestaña) porque el backend solo emite Bearer JWT;
  riesgo residual de XSS documentado en `docs/EVALUACION_SEGURIDAD.md`.
- El rol del JWT solo controla la UI; cada operación se valida en el backend.

## Documentación

- [`docs/ANALISIS_BACKEND.md`](docs/ANALISIS_BACKEND.md): endpoints, payloads, errores,
  autenticación, reglas y hallazgos.
- [`docs/EVALUACION_SEGURIDAD.md`](docs/EVALUACION_SEGURIDAD.md): controles, estado y
  recomendaciones.

## Cambio requerido en el backend para producción

En `app/presentation/main.py`, después de crear `app`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

No se aplicó porque las reglas de trabajo prohíben modificar el backend. Ajusta el origen al
del frontend desplegado.
