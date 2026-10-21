# Análisis del backend real — Kohem Chemicals MVP

Fuente de verdad: código ubicado en `../app` (no se modificó el backend). Se contrastó con
`/openapi.json` ejecutando `uvicorn app.presentation.main:app` sobre una base SQLite temporal.

- Backend: FastAPI, SQLAlchemy async, SQLite, JWT con HS256, bcrypt.
- Prefijo de negocio: `/api/v1`.
- El prompt de referencia hablaba de `backend/api/v1`, `users`, `geography`, `appointments` y
  refresh tokens. **Nada de eso existe en este repositorio.** Las rutas reales viven en
  `app/presentation/routers/`.
- Roles reales: `admin`, `analista`, `cliente` (no `ADMIN`, `EMPLEADO`, `CLIENTE`).

## 1. Endpoints

| Método | Ruta | Descripción | Auth | Roles | Archivo fuente |
|---|---|---|---|---|---|
| GET | `/` | Estado de la API | No | Público | `app/presentation/main.py` |
| POST | `/api/v1/auth/register` | Registro de usuario | No | Público | `app/presentation/routers/auth_router.py` |
| POST | `/api/v1/auth/token` | Login y emisión de JWT | No | Público | `app/presentation/routers/auth_router.py` |
| GET | `/api/v1/materials` | Lista materias primas | No | Público | `app/presentation/routers/material_router.py` |
| GET | `/api/v1/materials/{material_id}` | Consulta una materia prima | No | Público | `app/presentation/routers/material_router.py` |
| POST | `/api/v1/materials` | Crea materia prima | Sí | `admin` | `app/presentation/routers/material_router.py` |
| PUT | `/api/v1/materials/{material_id}` | Actualiza materia prima | Sí | `admin`, `analista` | `app/presentation/routers/material_router.py` |
| DELETE | `/api/v1/materials/{material_id}` | Elimina físicamente | Sí | `admin` | `app/presentation/routers/material_router.py` |
| POST | `/api/v1/orders` | Registra pedido | Sí | `cliente` | `app/presentation/routers/order_router.py` |
| GET | `/api/v1/orders` | Lista pedidos | Sí | `cliente` (propios), `admin`, `analista` (todos) | `app/presentation/routers/order_router.py` |
| GET | `/api/v1/orders/{order_id}` | Consulta pedido | Sí | Propietario o staff | `app/presentation/routers/order_router.py` |
| PATCH | `/api/v1/orders/{order_id}/status` | Cambia estado | Sí | `cliente` solo a `cancelado`; staff cualquier estado | `app/presentation/routers/order_router.py` |
| POST | `/api/v1/ai/chat` | Agente IA simulado | Sí | Cualquier rol autenticado | `app/presentation/routers/ai_router.py` |
| GET | `/api/v1/audit-logs` | Logs de auditoría | Sí | `admin`, `analista` | `app/presentation/routers/audit_router.py` |
| GET | `/docs`, `/openapi.json` | Swagger / OpenAPI | No | Público | FastAPI |

### No soportado por el backend

- Usuarios: no hay `GET/POST/PUT/DELETE /users`.
- Perfil propio: no hay `/users/me` ni edición de perfil.
- Geografía: no hay países, departamentos, ciudades ni sectores.
- Citas: no hay `appointments` ni bloqueo de solapamientos.
- Refresh token: no hay `/auth/refresh`, ni rotación, ni revocación.
- Rate limit / lockout: no implementado.
- Soft delete: no existe; `DELETE /materials/{id}` borra físicamente.
- Filtros tipo `?incluir_inactivos=true`: no existen.
- Totales paginados: no existen.

## 2. Payloads de entrada

### Convenciones generales

- **Login y registro aceptan JSON y `application/x-www-form-urlencoded`** (también
  `multipart/form-data`). El frontend usa **JSON**.
- El resto de POST/PUT/PATCH de negocio acepta JSON o formulario, pero el frontend usa JSON.
- `HEAD`/`GET` no requieren `Content-Type`.
- Los DTOs Pydantic **no usan `extra="forbid"`**: los campos desconocidos se ignoran.
- Header de autenticación: `Authorization: Bearer <access_token>`.

### `POST /api/v1/auth/register`

| Campo | Tipo | Obligatorio | Validación |
|---|---|---|---|
| `username` | string | Sí | 3–50 caracteres; único |
| `email` | string (email) | Sí | Formato de correo; no es único |
| `password` | string | Sí | Mínimo 8 caracteres; sin política de complejidad |
| `role` | enum | No | `admin`, `analista`, `cliente`; por defecto `cliente` |

> **Riesgo crítico:** el registro público acepta `role`. Un atacante puede crear un `admin`.
> El frontend omite el campo y siempre crea `cliente`, pero la API sigue siendo vulnerable.

### `POST /api/v1/auth/token`

| Campo | Tipo | Obligatorio | Validación |
|---|---|---|---|
| `username` | string | Sí | No vacío |
| `password` | string | Sí | No vacío |
| `grant_type`, `scope`, `client_id`, `client_secret` | — | No | Se ignoran; el router lee solo `username` y `password` |

Respuesta: `200` con `{"access_token": "...", "token_type": "bearer"}`.

### `GET /api/v1/materials` y `GET /api/v1/materials/{material_id}`

| Parámetro | Tipo | Obligatorio | Validación |
|---|---|---|---|
| `skip` | int (query) | No | Por defecto `0`; sin validación de rango |
| `limit` | int (query) | No | Por defecto `100`; sin validación de rango |
| `material_id` | int (path) | Sí | Entero; inexistente → `404` |

### `POST /api/v1/materials` (admin)

| Campo | Tipo | Obligatorio | Validación |
|---|---|---|---|
| `name` | string | Sí | 2–120 caracteres |
| `category` | string | Sí | 2–80 caracteres |
| `unit` | string | Sí | 1–20 caracteres |
| `price` | float | Sí | `> 0` |
| `stock` | float | Sí | `>= 0` |
| `description` | string o null | No | Máximo 500 caracteres |

### `PUT /api/v1/materials/{material_id}` (admin/analista)

Todos los campos son opcionales, con las mismas validaciones que la creación. El frontend
envía el objeto completo para evitar ambigüedad.

### `POST /api/v1/orders` (cliente)

| Campo | Tipo | Obligatorio | Validación |
|---|---|---|---|
| `items` | array | Sí | Mínimo 1 elemento |
| `items[].raw_material_id` | int | Sí | `> 0` |
| `items[].quantity` | float | Sí | `> 0` |
| `notes` | string o null | No | Máximo 500 caracteres |

### `PATCH /api/v1/orders/{order_id}/status`

| Campo | Tipo | Obligatorio | Validación |
|---|---|---|---|
| `status` | enum | Sí | `pendiente`, `confirmado`, `preparando`, `enviado`, `entregado`, `cancelado` |

### `POST /api/v1/ai/chat`

| Campo | Tipo | Obligatorio | Validación |
|---|---|---|---|
| `message` | string | Sí | 1–1000 caracteres |

### `GET /api/v1/audit-logs`

| Parámetro | Tipo | Obligatorio | Validación |
|---|---|---|---|
| `limit` | int (query) | No | Por defecto `100`; sin validación de rango |

## 3. Payloads de salida y errores

### Respuestas de éxito

- Registro: `201` → `UserResponseDTO` (`id`, `username`, `email`, `role`, `is_active`).
- Login: `200` → `Token` (`access_token`, `token_type`).
- Material: `200`/`201` → `RawMaterialResponseDTO` (`id`, `name`, `category`, `unit`,
  `price`, `stock`, `description`, `is_active`).
- Pedido: `200`/`201` → `OrderResponseDTO`:
  - `id`, `customer_id`, `status`, `total`, `notes`, `created_at`, `updated_at`
  - `items[]`: `id`, `raw_material_id`, `quantity`, `unit_price`, `subtotal`
- IA: `200` → `response`, `transfer_to_employee`, `reason`.
- Auditoría: `200` → lista de `id`, `user_id`, `action`, `entity`, `entity_id`, `detail`,
  `created_at`.
- `DELETE /materials/{id}`: `204` sin cuerpo.

### Códigos y formato de error

| Código | Cuándo | Formato real |
|---|---|---|
| `400` | Usuario duplicado; materia inexistente o stock insuficiente al crear pedido | `{"detail": "texto"}` |
| `401` | Credenciales inválidas o JWT ausente/expirado | `{"detail": "..."}` + `WWW-Authenticate` en login |
| `403` | Rol sin permiso | `{"detail": "..."}` |
| `404` | Recurso inexistente | `{"detail": "..."}` |
| `409` | Pedido en estado final | `{"detail": "..."}` |
| `415` | `Content-Type` no soportado en endpoints con parseo manual | `{"detail": "..."}` |
| `422` | Fallo de validación Pydantic o campos faltantes en login | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` (login sin usuario/clave devuelve `detail` string) |
| `500` | Error no controlado | HTML/JSON por defecto de Starlette; no hay handler propio |
| `429` | **No implementado** | — |

- **No existe `request_id`** en respuestas ni en errores. No hay cabecera de correlación.
- Los mensajes de `400/409` son de negocio y están en español; los de `422` son técnicos de
  Pydantic y pueden estar en inglés. El frontend no los muestra literalmente.

## 4. Autenticación

- Endpoint de login: `POST /api/v1/auth/token`.
- Formato: JSON o form-urlencoded. El frontend envía JSON.
- Access token: JWT firmado con HS256.
- Expiración: `ACCESS_TOKEN_EXPIRE_MINUTES`, por defecto **60 minutos**.
- Claims reales: `sub` (username), `role`, `user_id`, `exp`.
- **No incluye** `iss`, `aud`, `jti`.
- **No hay refresh token ni endpoint de refresh.**
- **No hay logout del servidor ni revocación**; el logout es local.
- Envío: `Authorization: Bearer <token>`.
- `OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")` se usa solo para dependencias; el
  router acepta JSON además del formulario OAuth2.
- Rate limit/lockout: **no implementado**. No hay `429`.
- Contraseñas: bcrypt vía `passlib`; solo mínimo 8 caracteres.

## 5. Matriz de roles

| Operación | admin | analista | cliente |
|---|:---:|:---:|:---:|
| Registrarse / login | Sí | Sí | Sí |
| Ver materiales | Sí | Sí | Sí |
| Crear material | Sí | No | No |
| Editar material | Sí | Sí | No |
| Eliminar material | Sí | No | No |
| Crear pedido | No | No | Sí |
| Ver todos los pedidos | Sí | Sí | No |
| Ver pedidos propios | — | — | Sí |
| Ver pedido ajeno | Sí | Sí | No (`403`) |
| Cambiar estado a cualquier valor | Sí | Sí | No |
| Cancelar pedido | Sí | Sí | Sí (propio, si no es final) |
| Chat IA | Sí | Sí | Sí |
| Ver auditoría | Sí | Sí | No |

## 6. Convenciones

- **snake_case** en todos los payloads.
- Fechas: `datetime.utcnow().isoformat()` → ISO 8601 **sin zona horaria** (naive UTC). El
  frontend las interpreta como UTC y las formatea localmente.
- Paginación: solo `skip` y `limit`; sin total, sin `next`/`previous`.
- Filtros: no existen.
- Ordenamiento: materiales por id ascendente (inserción); pedidos por id descendente;
  auditoría por id descendente.
- No hay soporte de búsqueda ni ordenamiento configurable en el servidor.
- El total del pedido se calcula en el servidor con el precio del momento de creación.
- Los campos de auditoría son de solo lectura.

## 7. Reglas de negocio que impactan la UI

- **Stock:** se valida y se descuenta **al crear el pedido**, no al confirmarlo.
- **Cancelación:** devuelve el stock reservado.
- **Estados finales:** `entregado` y `cancelado` no admiten cambios.
- **Transiciones:** no hay matriz de transición en el backend. El staff puede cambiar a
  cualquier estado mientras el actual no sea final. El cliente solo puede cancelar.
- **Líneas duplicadas:** el backend valida cada línea contra el stock sin agregar; dos líneas
  del mismo material podrían pasar la validación y dejar stock negativo. El frontend impide
  duplicados y valida la cantidad agregada.
- **Concurrencia:** no hay bloqueo ni transacción de reserva; dos pedidos simultáneos pueden
  sobrevender.
- **Materiales inactivos:** `GET /materials` los devuelve, pero un pedido con material
  inactivo falla con `400`/`404`.
- **Borrado:** `DELETE` es físico. Un material referenciado por pedidos puede quedar huérfano
  porque SQLite no fuerza FKs por defecto.
- **Citas:** no implementadas. No hay solapamiento, fecha futura ni estados de cita.
- **IA:** reglas por palabras clave (`formulación`, `técnico`, `urgente`, `reclamo`, `asesor`);
  no es un modelo real. Marca `transfer_to_employee` cuando detecta esos términos.
- **Auditoría:** solo registra creación y cambio de estado de pedidos. No audita materiales,
  usuarios ni login.

## 8. Hallazgos de seguridad del backend

1. **Crítico — escalada de rol en registro público:** cualquier persona puede crear un
   `admin` enviando `role`. Verificado en el smoke test: `role=admin` devolvió `201` y el
   usuario quedó con rol `admin`.
2. **Alto — CORS ausente:** no hay `CORSMiddleware`; un frontend en otro origen no puede
   consumir la API en producción. Se verificó que no se devuelve
   `Access-Control-Allow-Origin`.
3. **Alto — sin rate-limit ni lockout:** fuerza bruta ilimitada en login.
4. **Alto — `SECRET_KEY` por defecto:** si no existe `.env`, se usa
   `CHANGE_ME_IN_PRODUCTION`. En este repositorio solo existe `.env.example`.
5. **Medio — sin refresh/revocación:** tokens válidos 60 minutos y no anulables.
6. **Medio — borrado físico:** no hay soft delete ni recuperación.
7. **Medio — concurrencia de stock:** riesgo de sobreventa.
8. **Medio — sin `request_id`:** dificulta trazabilidad y soporte.
9. **Bajo/medio — mensajes 422 técnicos:** pueden filtrar detalles de implementación.
10. **Bajo — Swagger público:** `/docs` y `/openapi.json` quedan expuestos si no se restringen
    en el despliegue.
11. **Bajo — materiales públicos:** el inventario es visible sin autenticación.
12. **Bajo — sin política de contraseñas** más allá de 8 caracteres.
13. **Bajo — correo no único** y sin endpoints de gestión/desactivación de usuarios.

## 9. Supuestos y ambigüedades

- `analista` se muestra como “Analista”; el prompt lo llamaba `EMPLEADO`.
- El prompt decía que el stock se descuenta al confirmar; el código real lo descuenta al crear.
- El prompt pedía usuarios, citas, geografía, refresh y soft delete; **no existen**. No se
  inventaron endpoints ni pantallas funcionales para ellos.
- La moneda no está declarada; la UI formatea precios como COP por el contexto del proyecto.
- La auditoría se muestra a `admin` y `analista` porque el backend lo permite, aunque el
  prompt pedía “solo ADMIN”.
- Los dashboards suman hasta 100 registros devueltos por la API; no son agregados del servidor.
- No se expone el nombre del cliente en pedidos porque la API solo devuelve `customer_id`.
- El registro del frontend no envía `role`; el backend asigna `cliente`.
- El proxy de Vite es exclusivamente para desarrollo. Producción requiere CORS real.
