# Laboratorio 4 — Auditoría Backend IA · Kohem Chemicals

Material del laboratorio adaptado desde la guía de calculadora FastAPI al backend
del MVP de Kohem Chemicals, con **RAG y MCP reales**, **DeepSeek opcional** y
**modo conversacional** para que P06, P07, P11 y P12 auditen componentes reales.

## Contenido

| Archivo | Descripción |
|---|---|
| `GUIA_LABORATORIO_4_KOHEM.docx` / `.pdf` | Guía adaptada con la plantilla institucional |
| `INFORME_LABORATORIO_4_KOHEM.docx` / `.pdf` | Informe final de auditoría (P01–P12) |
| `RESULTADOS_LAB4.md` | Resumen, hallazgos, correcciones y configuración |
| `f01_operaciones.py` … `f12_conversacional.py` | Scripts de cada caso |
| `_common.py` | Utilidades: tokens, HTTP y guardado de evidencia |
| `_build_guia.py` | Generador del `.docx` desde la plantilla del profesor |
| `evidencias/` | Ejecución actual (P01–P12) |
| `_historico/antes/` | Archivo interno, no se entrega |

## Requisitos

- Backend levantado en `http://127.0.0.1:8000`.
- Dependencias instaladas (`mcp>=2.3.0` incluido):

```powershell
cd "C:\Auditoria\KohemChemicals\1. Diagnostico Auditoria\MVP"
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn app.presentation.main:app --reload
```

## Modos de IA

| `AI_MODE` | Comportamiento |
|---|---|
| `asistente` (defecto) | Plantilla fija; DeepSeek solo interpreta. Auditable. |
| `conversacional` | DeepSeek redacta con las cifras del dominio y acepta historial. |

Sin `DEEPSEEK_API_KEY`, ambos modos funcionan con el motor de reglas y devuelven
la plantilla.

Para ejecutar **f01–f11**, el backend debe estar en `AI_MODE=asistente`.
**f12** levanta su propia instancia en el puerto 8001 con
`AI_MODE=conversacional`, así que la auditoría no depende del modo del servicio
principal.

## Configurar DeepSeek

```powershell
Copy-Item .env.example .env
# Editar .env:
#   DEEPSEEK_API_KEY=sk-...
#   AI_MODE=conversacional
```

| Variable | Valor |
|---|---|
| `DEEPSEEK_API_KEY` | clave de <https://platform.deepseek.com> |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | `deepseek-chat` |
| `LLM_TIMEOUT_SECONDS` | `20` |
| `LLM_TEMPERATURE` | `0.3` |
| `AI_MODE` | `asistente` o `conversacional` |
| `AI_HISTORY_MAX` | `8` |

`.env` está ignorado por Git. No subir la clave ni incluirla en evidencias.

## Ejecución

Desde `docs\laboratorio4`, con el backend en el puerto 8000:

```powershell
..\..\venv\Scripts\python.exe f01_operaciones.py
# …
..\..\venv\Scripts\python.exe f11_deepseek.py
..\..\venv\Scripts\python.exe f12_conversacional.py
```

`f12` levanta su propia instancia en el puerto 8001 con
`AI_MODE=conversacional`, ejecuta el diálogo y la apaga.

Para guardar en otra carpeta:

```powershell
$env:LAB4_EVID = "evidencias"
```

## Notas

- `f07_mcp.py` abre una sesión MCP real por stdio y tarda ~2 s porque arranca el
  servidor como subproceso.
- Los scripts crean datos temporales y los eliminan o cancelan al final; si se
  interrumpe uno, revisar `GET /api/v1/materials` y `GET /api/v1/orders`.
- Las evidencias no contienen tokens ni la clave de DeepSeek.
- Para volver al estado sin modo conversacional: `git checkout lab4-asistente-estable`.
