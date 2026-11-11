# Laboratorio 4 — Auditoría Backend IA · Kohem Chemicals

Resultados de la ejecución completa (P01–P11) sobre el backend del MVP, con el
módulo de IA reconstruido (RAG + MCP reales + DeepSeek opcional) y las
correcciones aplicadas en la fase Actuar del ciclo PHVA.

- **Fecha:** 10/11/2026
- **Rama:** `lab4-mcp-rag`
- **API auditada:** `http://127.0.0.1:8000` (FastAPI + SQLite)
- **Suite:** **68 pruebas aprobadas, 0 fallos** (`f10_pytest.txt`)
- **Evidencias:** `evidencias/antes/` y `evidencias/despues/`

## 1. Resumen por caso

| ID | Caso | Antes | Después |
|---|---|---|---|
| P01 | Operaciones y cálculo | ✅ | ✅ |
| P02 | Stock y atomicidad | ⚠️ cantidad 0 → 500 | ✅ 422 y stock intacto |
| P03 | Límites y precisión | ⚠️ negativos → 500 | ✅ 422 |
| P04 | Contrato HTTP | ⚠️ legado 500 | ✅ 422 coherente |
| P05 | Interpretación | ⚠️ 6/10 | ✅ 10/10 |
| P06 | Reglas RAG | ⚠️ falso positivo | ✅ |
| P07 | Adaptador MCP | ✅ | ✅ |
| P08 | Extremo a extremo | ✅ | ✅ |
| P09 | Errores y robustez | ⚠️ 2 respuestas 500 | ✅ sin 500 |
| P10 | Regresión y arquitectura | ✅ | ✅ |
| P11 | Motor DeepSeek / reglas | — | ✅ (respaldo por reglas) |

## 2. Cómo funciona el componente de IA

```
POST /ai/chat → AIAssistantUseCase
  1. RAG: políticas de IVA, tope y stock por palabras clave.
  2. Interpretación: DeepSeek si hay clave; si no (o si falla), reglas.
  3. Acción: herramientas MCP (listar_materiales, consultar_stock, calcular_pedido).
  4. Dominio: PricingDomainService y repositorio SQLite.
  5. Respuesta: {response, transfer_to_employee, reason, motor}
```

- **Sin `DEEPSEEK_API_KEY`**: todo funciona offline con reglas léxicas, expresiones
  regulares, números en palabras y comparación difusa de nombres.
- **Con clave**: `app/infrastructure/deepseek_llm.py` envía la consulta a
  `https://api.deepseek.com/chat/completions` pidiendo un JSON estricto. Si la
  red falla, el JSON es inválido o la clave no existe, se usa el motor de reglas.
- **La clave nunca** se escribe en logs, evidencias ni repositorio: va en `.env`
  (ver `.env.example`).

## 3. Correcciones aplicadas

| Área | Cambio | Archivos |
|---|---|---|
| Validación HTTP | Helper único `leer_cuerpo` + `validar_modelo`: 422 para Pydantic y 400 para JSON inválido | `app/presentation/validacion.py`, routers de auth, materials y orders |
| Interpretación | Números en palabras, sinónimos de unidades, negaciones, prioridad de cotización | `app/application/ai_use_cases.py` |
| RAG | Coincidencia por palabra completa; se elimina `max` genérico | `app/infrastructure/mock_vector_db.py` |
| Motor de IA | Puerto `ILLMProvider` + adaptador DeepSeek con *fallback* | `ports.py`, `deepseek_llm.py`, `dependencies.py` |
| Contrato | Campo `motor` en la respuesta | `dtos.py`, `ai_router.py` |
| Pruebas obsoletas | `/auth/login` → `/auth/token`; usuario `c1` → `cli1` | `tests/test_auth.py`, `tests/test_order_permissions.py` |

## 4. Hallazgos y estado

| ID | Hallazgo | Severidad | Estado |
|---|---|---|---|
| H-L4-01 | El «LLM» era un motor de reglas limitado | Media | Mitigado: DeepSeek opcional + reglas ampliadas |
| H-L4-02 | El RAG activaba el tope con «al máximo» | Media | Resuelto |
| H-L4-03 | Endpoints legados devolvían 500 al validar | Media | Resuelto |
| H-L4-04 | Un término técnico anulaba la cotización | Baja | Resuelto |
| H-L4-05 | La ruta de SQLite depende del directorio de trabajo | Baja | Pendiente |
| H-L4-06 | `SECRET_KEY` por defecto sin validación | Media | Pendiente |
| H-L4-07 | El servidor MCP no aplica autenticación | Baja | Pendiente (solo local) |
| H-L4-08 | El asistente no registra pedidos ni consulta por ID | Informativa | Aceptado por alcance |

## 5. Configurar DeepSeek

```powershell
cd "C:\Auditoria\KohemChemicals\1. Diagnostico Auditoria\MVP"
Copy-Item .env.example .env
# Editar .env y completar DEEPSEEK_API_KEY=sk-...
# Reiniciar uvicorn
```

Comprobar con:

```powershell
cd docs\laboratorio4
..\..\venv\Scripts\python.exe f11_deepseek.py
```

`f11_deepseek.json` debe mostrar `"configurado": true`, `"motor": "deepseek"` y la
latencia de cada consulta. Sin clave, el mismo script verifica el respaldo con
`"motor": "reglas"`.

## 6. Índice de evidencias

| Archivo | Contenido |
|---|---|
| `evidencias/antes/*` | Ejecución previa a las correcciones (hallazgos) |
| `evidencias/despues/*` | Ejecución final con P01–P11 en verde |
| `f01_operaciones.json` | Dominio y cotización |
| `f02_stock.json` | Sobreventa y atomicidad |
| `f03_limites.json` | Negativos, decimales y redondeo |
| `f04_contrato.json` | Contrato HTTP del asistente y del legado |
| `f05_prompt.json` | Diez variantes de lenguaje natural |
| `f06_rag.json` | Contexto recuperado y reglas aplicadas |
| `f07_mcp.json` | Esquema de herramientas y transporte stdio |
| `f08_e2e.json` | Chat, pedido, stock y auditoría |
| `f09_errores.json` | Matriz de errores y fugas |
| `f10_regresion.json` / `f10_pytest.txt` | Suite completa y análisis de capas |
| `f11_deepseek.json` | Motor usado y respaldo por reglas |

## 7. Nota de adaptación

La guía original auditaba una calculadora con operandos constantes. En Kohem el
equivalente funcional es el **cálculo de pedidos** (subtotal, IVA, tope, stock),
por lo que P01–P03 se apoyan en `domain/services.py` y en la herramienta MCP
`calcular_pedido`. MCP y RAG se implementaron de forma real para que P06 y P07
auditen componentes existentes y no su ausencia.

