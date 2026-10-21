# Evaluación de seguridad del frontend

Alcance: SPA `MVP/frontend` y su interacción con el backend FastAPI existente. No se modificó
el backend. La evaluación se basa en el código real y en pruebas de humo contra una base
temporal.

| Control | Estado | Evidencia | Recomendación |
|---|---|---|---|
| Autenticación con JWT | Parcial | `src/auth/AuthProvider.tsx`, `src/api/services/auth.service.ts`, `POST /api/v1/auth/token` | Añadir refresh token con rotación y revocación; implementar lockout/rate-limit en el backend. |
| Almacenamiento seguro del token | Parcial | `src/auth/tokenStorage.ts` usa `sessionStorage` por pestaña | Migrar a cookie `HttpOnly` + `Secure` + `SameSite` cuando el backend lo soporte; el contrato actual solo permite Bearer en JSON. |
| Expiración de sesión | Cumple (parcial) | `decodeSessionToken`, `isExpired`, interceptor 401 en `src/api/client.ts` | El token expira a los 60 min y la sesión local se cierra; no hay revocación del lado servidor. |
| Logout | Parcial | `AuthProvider.logout`, `SessionPage`, `AppLayout` | Limpia el token local. No existe endpoint de logout ni invalidación de JWT. |
| Autorización por rol en UI | Cumple | `src/utils/permissions.ts`, `src/auth/guards.tsx`, menú en `AppLayout` | Mantener el backend como autoridad; la UI solo oculta/deshabilita. |
| Autorización en el backend | Parcial | Roles en `app/application/*_use_cases.py` y routers | Corregir la escalada de rol del registro público (ver hallazgo crítico). |
| Escalada de privilegios en registro | **No cumple (backend)** | `POST /api/v1/auth/register` acepta `role`; verificado en smoke test: registro con `role=admin` devolvió `201` y `role=admin` | Restringir `role` a `cliente` para registro público; crear usuarios internos solo desde un endpoint admin. |
| Validación de entrada en cliente | Cumple | `src/schemas/*.ts` espeja las restricciones Pydantic | Mantener sincronizado si cambian los DTOs. |
| Validación de entrada en servidor | Cumple | DTOs en `app/application/dtos.py` | Añadir `extra="forbid"` si se desea rechazar campos inesperados. |
| Manejo de 401/403/404/409/422/429/red/500 | Cumple | `src/api/errors.ts`, `src/api/client.ts` | 429 no lo emite el backend actualmente; la UI ya lo contempla. |
| Mensajes de error sin detalles técnicos | Cumple (parcial) | `normalizeApiError` reemplaza mensajes 422 y usa mensajes genéricos | No existe `request_id`; añadirlo en el backend para soporte y trazabilidad. |
| CORS | **No cumple (backend)** | Verificado: sin `Access-Control-Allow-Origin` | Añadir `CORSMiddleware` con el origen exacto del frontend. El proxy de Vite es solo desarrollo. |
| Exposición de datos sensibles | Parcial | `OrderDetailPage` muestra `customer_id` solo a staff; no hay usuarios/nombres | Añadir endpoint de usuarios si se requiere mostrar nombres; no exponer datos innecesarios. |
| XSS | Cumple | Sin `dangerouslySetInnerHTML`; React escapa el contenido | Mantener la regla y considerar CSP en el despliegue. |
| Secretos en el frontend | Cumple | `.env` ignorado, `.env.example` sin secretos, solo `VITE_API_BASE_URL` | No incluir claves privadas en variables `VITE_*`; son públicas por diseño. |
| Secretos en el backend | **No cumple (backend)** | `app/infrastructure/config.py` usa `CHANGE_ME_IN_PRODUCTION` si falta `.env` | Definir `SECRET_KEY` fuerte por entorno y fallar al arrancar si no existe. |
| Rate limit / lockout | **No cumple (backend)** | `auth_router.py` no limita intentos | Implementar rate-limit por IP/usuario y bloqueo temporal. |
| Borrado lógico | **No cumple (backend)** | `DELETE /api/v1/materials/{id}` borra físicamente | Implementar desactivación (`is_active`) y conservar historial. |
| Integridad de stock | Parcial | `OrderUseCases.create_order` valida y descuenta en dos pasos | Usar transacción/bloqueo y agregar cantidades por material. |
| Auditoría | Parcial | Solo creación/cambio de estado de pedidos (`order_use_cases.py`) | Auditar materiales, usuarios, login y accesos denegados. |
| HTTPS y cabeceras de seguridad | No verificable | El backend se ejecuta en HTTP local y no configura cabeceras | Terminar TLS en el despliegue y añadir HSTS, CSP, X-Content-Type-Options, etc. |
| Protección CSRF | Cumple | Se usa `Authorization: Bearer`, no cookies de sesión | Si se migra a cookies, añadir CSRF token y `SameSite`. |
| Documentación expuesta | Parcial | `/docs` y `/openapi.json` públicos | Restringir o deshabilitar en producción. |

## Conclusión

Los controles **propios del frontend** son razonables para un MVP: guards de ruta, menú por
rol, validación Zod, manejo centralizado de errores, ausencia de `dangerouslySetInnerHTML`,
token en `sessionStorage`, sin secretos y con el backend como autoridad de autorización.

Sin embargo, **los controles no son suficientes** para afirmar que el sistema cumple ISO/IEC
27001 ni para superar una prueba de seguridad técnica, debido a debilidades del backend:

1. Registro público con `role` permite crear administradores.
2. Ausencia de CORS impide un despliegue separado sin cambio de backend.
3. Sin rate-limit/lockout en login.
4. `SECRET_KEY` con valor por defecto si no hay `.env`.
5. Sin refresh/revocación de tokens.
6. Borrado físico y auditoría incompleta.
7. Riesgo de sobreventa por concurrencia y por líneas duplicadas.

El proxy de Vite `/api` → `http://127.0.0.1:8000` es **solo para desarrollo** y no sustituye
la configuración CORS de producción.
