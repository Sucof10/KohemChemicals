# Laboratorio 4 — Auditoría Backend IA · Kohem Chemicals

Material del laboratorio adaptado desde la guía de calculadora FastAPI al backend
del MVP de Kohem Chemicals, con **RAG y MCP reales** y **DeepSeek opcional** para
que los casos P06, P07 y P11 auditen componentes existentes.

## Contenido

| Archivo | Descripción |
|---|---|
| `GUIA_LABORATORIO_4_KOHEM.docx` / `.pdf` | Guía adaptada con la plantilla institucional |
| `RESULTADOS_LAB4.md` | Resumen, hallazgos, correcciones y configuración de DeepSeek |
| `f01_operaciones.py` … `f11_deepseek.py` | Scripts de cada caso |
| `_common.py` | Utilidades: tokens, HTTP y guardado de evidencia |
| `_build_guia.py` | Generador del `.docx` a partir de la plantilla del profesor |
| `evidencias/antes/` | Ejecución previa a las correcciones |
| `evidencias/despues/` | Ejecución final (P01–P11 en verde) |

## Requisitos

- Backend levantado en `http://127.0.0.1:8000`.
- Dependencias instaladas (`mcp>=2.3.0` incluido):

```powershell
cd "C:\Auditoria\KohemChemicals\1. Diagnostico Auditoria\MVP"
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn app.presentation.main:app --reload
```

## Motor de IA

Sin configuración adicional funciona el **motor de reglas**. Para usar DeepSeek:

```powershell
Copy-Item .env.example .env
# Editar .env y completar DEEPSEEK_API_KEY=sk-...
```

| Variable | Valor |
|---|---|
| `DEEPSEEK_API_KEY` | clave del proveedor |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | `deepseek-chat` |
| `LLM_TIMEOUT_SECONDS` | `20` |

La respuesta incluye `motor` (`reglas` o `deepseek`). Si el modelo falla, el
asistente continúa por reglas.

## Ejecución

Desde `docs\laboratorio4`:

```powershell
..\..\venv\Scripts\python.exe f01_operaciones.py
..\..\venv\Scripts\python.exe f02_stock.py
# …
..\..\venv\Scripts\python.exe f11_deepseek.py
```

Para guardar en otra carpeta (por ejemplo, una nueva ejecución):

```powershell
$env:LAB4_EVID = "evidencias/despues"
```

## Notas

- `f07_mcp.py` abre una sesión MCP real por stdio (`initialize → list_tools →
  call_tool`) y tarda ~2 s porque arranca el servidor como subproceso.
- El servidor MCP puede levantarse con `python -m app.infrastructure.mcp_server`
  (transporte stdio, no HTTP).
- Los scripts crean datos temporales y los eliminan o cancelan al final; si se
  interrumpe uno, revisar `GET /api/v1/materials` y `GET /api/v1/orders`.
- Las evidencias no contienen tokens ni la clave de DeepSeek.
