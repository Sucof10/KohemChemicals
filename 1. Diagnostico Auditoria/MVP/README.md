# Kohem Chemicals — MVP Backend

MVP basado en la estructura del backend de referencia del profesor (`backend_mvp_calzado`), adaptado al proyecto **Sistema Transaccional de Gestión de Pedidos y Asesoría para Distribuidora de Materias Primas**.

## Alcance del MVP

El MVP prioriza el proceso central que será auditado: **registro de pedidos**.

Incluye:

1. Autenticación con JWT y roles: `admin`, `analista`, `cliente`.
2. Catálogo e inventario de materias primas.
3. Registro de pedidos por clientes.
4. Validación de disponibilidad antes de registrar el pedido.
5. Descuento del stock al registrar un pedido.
6. Consulta de pedidos según el rol.
7. Actualización de estado del pedido y cancelación con devolución de stock.
8. Registro de logs de auditoría para operaciones sobre pedidos.
9. Agente IA MVP con transferencia a empleado cuando la consulta requiere intervención humana.
10. Swagger/OpenAPI y pruebas automatizadas con pytest.

## Arquitectura

Se conserva la separación del proyecto de referencia:

- `domain/`: entidades, interfaces y excepciones.
- `application/`: DTOs y casos de uso.
- `infrastructure/`: SQLite, SQLAlchemy, repositorios y seguridad.
- `presentation/`: FastAPI, dependencias y routers.
- `tests/`: pruebas automatizadas.

## Instalación

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/macOS
```

## Ejecución

```bash
uvicorn app.presentation.main:app --reload
```

Abrir:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## Usuarios iniciales

- Admin: `admin` / `AdminPass123!`
- Cliente: `cliente` / `ClientPass123!`

Para producción se deben cambiar estas credenciales y la `SECRET_KEY`.

## Flujo principal del MVP

`Cliente → Autenticación → Consulta materias primas → Verificación de stock → Registro de pedido → Descuento de inventario → Estado del pedido → Log de auditoría`

Si la consulta pasa por el agente IA y requiere intervención humana:

`Cliente → Agente IA → Transferencia a empleado`

## Endpoints principales

### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/token`

### Materias primas
- `GET /api/v1/materials`
- `GET /api/v1/materials/{id}`
- `POST /api/v1/materials` — admin
- `PUT /api/v1/materials/{id}` — admin/analista
- `DELETE /api/v1/materials/{id}` — admin

### Pedidos
- `POST /api/v1/orders` — cliente
- `GET /api/v1/orders` — cliente ve sus pedidos; admin/analista ve todos
- `GET /api/v1/orders/{id}`
- `PATCH /api/v1/orders/{id}/status`

### Agente IA
- `POST /api/v1/ai/chat`

## Pruebas

```bash
pytest -q
```

## Nota académica

Este MVP es una implementación inicial para demostrar el flujo funcional y de seguridad del proceso de registro de pedidos. No reemplaza controles de producción como gestión formal de secretos, HTTPS, base de datos gestionada, monitoreo, pruebas de carga, hardening, gestión de sesiones y despliegue seguro.
- `GET /api/v1/audit-logs` — admin/analista


## Swagger para las pruebas

El Swagger del MVP está preparado para realizar las pruebas directamente desde `http://127.0.0.1:8000/docs`, siguiendo el patrón de la API de referencia:

### 1. Registro — JSON editable
`POST /api/v1/auth/register` usa `application/json`. Al pulsar **Try it out** se puede editar y enviar un cuerpo como:

```json
{
  "username": "analista1",
  "email": "analista1@empresa.com",
  "password": "AnalistaPass123!",
  "role": "analista"
}
```

### 2. Login — formulario editable
`POST /api/v1/auth/token` usa `application/x-www-form-urlencoded`. Swagger muestra los campos `grant_type`, `username`, `password`, `scope`, `client_id` y `client_secret`. La respuesta es JSON con `access_token` y `token_type`.

### 3. Operaciones de negocio — JSON editable
Los POST/PUT/PATCH de materias primas, pedidos, cambio de estado y agente IA usan cuerpos JSON editables desde **Try it out**.

## Flujo recomendado de prueba

1. Ejecutar `POST /api/v1/auth/register`.
2. Ejecutar `POST /api/v1/auth/token` con un usuario existente y guardar el `access_token`.
3. Pulsar **Authorize** y usar el JWT como Bearer.
4. Consultar materias primas.
5. Registrar un pedido como cliente.
6. Consultar el pedido y verificar el descuento de inventario.
7. Consultar los logs con admin/analista.
8. Probar el agente IA y la transferencia a empleado.

