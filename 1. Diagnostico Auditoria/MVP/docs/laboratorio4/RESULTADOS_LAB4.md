# Laboratorio 4 — Auditoría Backend IA · Kohem Chemicals

Resultados de la ejecución completa (P01–P12) sobre el backend del MVP, con el
módulo de IA reconstruido (RAG + MCP reales + DeepSeek opcional) y los modos
`asistente` y `conversacional`.

- **Fecha:** 10/11/2026
- **Ramas:** `lab4-mcp-rag` (base), `lab4-conversacional` (modo conversacional)
- **Etiqueta estable:** `lab4-asistente-estable`
- **API auditada:** `http://127.0.0.1:8000`
- **Suite:** **74 pruebas aprobadas, 0 fallos**
- **Evidencias:** `evidencias/antes/` y `evidencias/despues/`

## 1. Resumen por caso

| ID | Caso | Antes | Después |
|---|---|---|---|
| P01 | Operaciones y cálculo | ✅ | ✅ |
| P02 | Stock y atomicidad | ⚠️ cantidad 0 → 500 | ✅ 422 |
| P03 | Límites y precisión | ⚠️ negativos → 500 | ✅ 422 |
| P04 | Contrato HTTP | ⚠️ legado 500 | ✅ 422 |
| P05 | Interpretación | ⚠️ 6/10 | ✅ 10/10 |
| P06 | Reglas RAG | ⚠️ falso positivo | ✅ |
| P07 | Adaptador MCP | ✅ | ✅ |
| P08 | Extremo a extremo | ✅ | ✅ |
| P09 | Errores y robustez | ⚠️ 2 respuestas 500 | ✅ sin 500 |
| P10 | Regresión y arquitectura | ✅ | ✅ |
| P11 | Motor DeepSeek / reglas | — | ✅ |
| P12 | Modo conversacional | — | ✅ |

## 2. Cómo funciona el componente de IA

```
POST /ai/chat → AIAssistantUseCase.respond(message, historial)
  1. RAG: políticas de IVA, tope y stock por palabras clave.
  2. Interpretación: DeepSeek si hay clave; si no (o si falla), reglas.
  3. Acción: MCP listar_materiales / consultar_stock / calcular_pedido.
  4. Dominio: PricingDomainService + SQLite.
  5. Motor asistente: plantilla. Motor conversacional: DeepSeek redacta.
  6. Respuesta: {response, transfer_to_employee, reason, motor, datos}
```

| Modo | Qué hace | Cuándo usarlo |
|---|---|---|
| `asistente` (defecto) | Plantilla fija con cifras calculadas | Auditoría reproducible (P01–P11) |
| `conversacional` | DeepSeek redacta con los datos del dominio | Atención al cliente (P12) |

**Salvaguardas:** el modelo nunca calcula precios ni stock; recibe un bloque
`datos` ya calculado. Si falla, se devuelve la plantilla. El historial lo envía
el cliente (máximo `AI_HISTORY_MAX` mensajes) y el servidor no almacena
conversaciones. Todo funciona sin clave mediante reglas.

## 3. Correcciones aplicadas

| Área | Cambio | Archivos |
|---|---|---|
| Validación HTTP | 422 para Pydantic y 400 para JSON inválido | `app/presentation/validacion.py` + routers |
| Interpretación | Números en palabras, unidades alternativas, negaciones, prioridad de cotización | `ai_use_cases.py` |
| RAG | Coincidencia por palabra completa; se elimina `max` genérico | `mock_vector_db.py` |
| Motor de IA | Puerto `ILLMProvider` + DeepSeek con respaldo | `ports.py`, `deepseek_llm.py` |
| Modo conversacional | Redacción natural + historial + `datos` | `ai_use_cases.py`, `dtos.py`, `ai_router.py` |
| Pruebas obsoletas | `/auth/login` → `/auth/token`; usuario `c1` → `cli1` | `tests/test_auth.py`, `tests/test_order_permissions.py` |

## 4. Hallazgos y estado

| ID | Hallazgo | Severidad | Estado |
|---|---|---|---|
| H-L4-01 | El «LLM» era un motor de reglas limitado | Media | Mitigado: DeepSeek + modo conversacional |
| H-L4-02 | El RAG activaba el tope con «al máximo» | Media | Resuelto |
| H-L4-03 | Endpoints legados devolvían 500 al validar | Media | Resuelto |
| H-L4-04 | Un término técnico anulaba la cotización | Baja | Resuelto |
| H-L4-05 | La ruta de SQLite depende del directorio de trabajo | Baja | Pendiente |
| H-L4-06 | `SECRET_KEY` por defecto sin validación | Media | Pendiente |
| H-L4-07 | El servidor MCP no aplica autenticación | Baja | Pendiente (solo local) |
| H-L4-08 | El asistente no registra pedidos ni consulta por ID | Informativa | Aceptado por alcance |

## 5. Configurar la clave de DeepSeek

1. Entrar a <https://platform.deepseek.com>, sección **API keys**, y crear una clave.
   Hace falta saldo/crédito en la cuenta.
2. En el proyecto:

```powershell
cd "C:\Auditoria\KohemChemicals\1. Diagnostico Auditoria\MVP"
Copy-Item .env.example .env
```

3. Abrir `.env` y completar:

```ini
DEEPSEEK_API_KEY=sk-tu-clave-real
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
AI_MODE=conversacional
```

4. Reiniciar el backend (sin `--reload` no toma cambios):

```powershell
.\venv\Scripts\python.exe -m uvicorn app.presentation.main:app --reload
```

5. Verificar:

```powershell
cd docs\laboratorio4
..\..\venv\Scripts\python.exe f11_deepseek.py
..\..\venv\Scripts\python.exe f12_conversacional.py
```

En `f11_deepseek.json` debe aparecer `"configurado": true` y un `motor` acorde al
modo: `deepseek` en `asistente` o `deepseek-conversacional` en `conversacional`.
En `f12_conversacional.json` siempre debe ser `deepseek-conversacional`.

**Seguridad:** `.env` está en `.gitignore`; no debe subirse ni pegarse en el chat,
el informe o las evidencias. Si la clave se expone, hay que revocarla y crear otra.

## 6. Índice de evidencias

| Archivo | Contenido |
|---|---|
| `evidencias/antes/*` | Ejecución previa a las correcciones |
| `evidencias/despues/*` | Ejecución final (P01–P12) |
| `f01_operaciones.json` | Dominio y cotización |
| `f02_stock.json` | Sobreventa y atomicidad |
| `f03_limites.json` | Negativos, decimales y redondeo |
| `f04_contrato.json` | Contrato HTTP |
| `f05_prompt.json` | Diez variantes de lenguaje natural |
| `f06_rag.json` | Contexto recuperado y reglas |
| `f07_mcp.json` | Esquema y transporte stdio |
| `f08_e2e.json` | Chat, pedido, stock y auditoría |
| `f09_errores.json` | Matriz de errores y fugas |
| `f10_regresion.json` / `f10_pytest.txt` | Suite y capas |
| `f11_deepseek.json` | Motor usado |
| `f12_conversacional.json` | Modo conversacional e historial |

## 7. Volver al estado no conversacional

```powershell
git checkout lab4-asistente-estable
```

O, sin cambiar de rama, poner `AI_MODE=asistente` en `.env` y reiniciar.

## 8. Nota de adaptación

La guía original auditaba una calculadora con operandos constantes. En Kohem el
equivalente funcional es el **cálculo de pedidos** (subtotal, IVA, tope, stock).
MCP y RAG se implementaron de forma real para que P06 y P07 auditen componentes
existentes. El modo conversacional se añade como P12 sin alterar los casos
P01–P11 ni el contrato del endpoint.
