# Guía rápida de demostración del MVP

## 1. Iniciar API

```bash
pip install -r requirements.txt
uvicorn app.presentation.main:app --reload
```

## 2. Mostrar Swagger

Entrar a `/docs`.

## 3. Demostrar flujo principal

1. `POST /auth/token` con `cliente / ClientPass123!`.
2. Copiar el `access_token` y usar **Authorize** en Swagger.
3. `GET /materials` para mostrar disponibilidad.
4. `POST /orders` con una materia prima y cantidad.
5. Mostrar que el pedido queda registrado y el stock disminuye.
6. `GET /orders` para consultar la trazabilidad del cliente.
7. Ingresar con un usuario `admin` o `analista` y consultar `GET /audit-logs`.
8. Probar `POST /ai/chat` con una consulta sobre formulación y evidenciar `transfer_to_employee: true`.

## 4. Relación con el proceso auditado

El flujo implementa el núcleo del diagrama de proceso: autenticación → selección de producto → verificación de disponibilidad → registro del pedido. El MVP agrega control de acceso, reserva/descuento de inventario y logging para facilitar la demostración de controles de seguridad.
