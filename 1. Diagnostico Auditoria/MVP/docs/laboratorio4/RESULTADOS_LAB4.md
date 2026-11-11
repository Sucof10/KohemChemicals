# Laboratorio 4 — Auditoría Backend IA · Kohem Chemicals

Resumen del estado actual del backend tras la ejecución de los casos P01–P12.

- **Fecha:** 10/11/2026
- **Rama:** `lab4-conversacional`
- **API:** `http://127.0.0.1:8000`
- **Suite:** 75 pruebas aprobadas, 0 fallos
- **Evidencias:** `evidencias/`

## 1. Resultados por caso

| ID | Caso | Resultado |
|---|---|---|
| P01 | Operaciones y cálculo | Cumple |
| P02 | Stock y atomicidad | Cumple |
| P03 | Límites y precisión | Cumple |
| P04 | Contrato HTTP | Cumple |
| P05 | Interpretación | 10/10 |
| P06 | Reglas RAG | Cumple |
| P07 | Adaptador MCP | Cumple |
| P08 | Extremo a extremo | Cumple |
| P09 | Errores | Sin HTTP 500 |
| P10 | Regresión y arquitectura | Cumple |
| P11 | Motor DeepSeek / reglas | Cumple |
| P12 | Modo conversacional | Cumple |

## 2. Cómo funciona la IA

```
POST /ai/chat → AIAssistantUseCase
  1. RAG: políticas de IVA, tope y stock por palabras clave.
  2. Interpretación: DeepSeek si hay clave; si no, reglas.
  3. Acción: MCP (listar_materiales, consultar_stock, calcular_pedido).
  4. Dominio: PricingDomainService + SQLite.
  5. Motor asistente: plantilla. Conversacional: DeepSeek redacta como asesor.
  6. Respuesta: {response, transfer_to_employee, reason, motor, datos}
```

| Modo | Comportamiento |
|---|---|
| `asistente` (defecto) | Plantilla fija con cifras calculadas. Auditable. |
| `conversacional` | Asesor con catálogo, políticas e historial. |

Sin clave de DeepSeek, ambos modos funcionan con reglas y devuelven la plantilla.

## 3. Controles del estado actual

- Validación centralizada: 422 para Pydantic, 400 para JSON inválido, 415 para tipo no soportado.
- Cifras de precio, IVA y total calculadas por el dominio, no por el modelo.
- RAG por palabra completa; el tope exige términos explícitos.
- MCP con tres herramientas, esquema y errores controlados.
- Respaldo automático a reglas si el modelo falla o no hay clave.
- Historial limitado a 8 mensajes enviados por el cliente; no se almacena.
- 75 pruebas automatizadas.

## 4. Hallazgos abiertos

| ID | Hallazgo | Severidad | Estado |
|---|---|---|---|
| H-L4-01 | La ruta de SQLite depende del directorio de trabajo. | Baja | Abierto |
| H-L4-02 | `SECRET_KEY` por defecto sin validación al arrancar. | Media | Abierto |
| H-L4-03 | El servidor MCP no aplica autenticación. | Baja | Abierto |
| H-L4-04 | El asistente no registra pedidos ni consulta por ID. | Informativa | Aceptado |

## 5. Configurar DeepSeek

```powershell
cd "C:\Auditoria\KohemChemicals\1. Diagnostico Auditoria\MVP"
Copy-Item .env.example .env
# Editar .env y completar DEEPSEEK_API_KEY
```

| Variable | Valor |
|---|---|
| `DEEPSEEK_API_KEY` | clave de platform.deepseek.com |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | `deepseek-chat` |
| `AI_MODE` | `asistente` o `conversacional` |
| `AI_HISTORY_MAX` | `8` |

`.env` está ignorado por Git. No subir la clave ni incluirla en evidencias.

## 6. Evidencias

| Archivo | Contenido |
|---|---|
| `f01_operaciones.json` | Dominio y cotización |
| `f02_stock.json` | Sobreventa y atomicidad |
| `f03_limites.json` | Negativos, decimales y redondeo |
| `f04_contrato.json` | Contrato HTTP |
| `f05_prompt.json` | Diez variantes de lenguaje |
| `f06_rag.json` | Contexto y reglas |
| `f07_mcp.json` | Esquema y stdio |
| `f08_e2e.json` | Chat, pedido y auditoría |
| `f09_errores.json` | Errores y fugas |
| `f10_regresion.json` / `f10_pytest.txt` | Suite y capas |
| `f11_deepseek.json` | Motor usado |
| `f12_conversacional.json` | Modo conversacional |

## 7. Volver al modo no conversacional

```powershell
git checkout lab4-asistente-estable
```

O poner `AI_MODE=asistente` en `.env` y reiniciar.

## 8. Nota de adaptación

La guía original auditaba una calculadora con operandos constantes. En Kohem el
equivalente es el cálculo de pedidos (subtotal, IVA, tope y stock). RAG y MCP se
implementaron de forma real para que P06 y P07 auditen componentes existentes.
