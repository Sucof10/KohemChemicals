"""Genera la guía del Laboratorio 4 adaptada a Kohem Chemicals.

Reutiliza el .docx del profesor como plantilla para conservar encabezado, pie,
márgenes y estilos institucionales, y reemplaza todo el cuerpo.
"""

import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = Path(__file__).resolve().parent
PLANTILLA = Path(r"D:\Descargas\Laboratorio 4 - Auditoria Backend IA.docx")
SALIDA = BASE / "GUIA_LABORATORIO_4_KOHEM.docx"
AZUL = RGBColor(0x1F, 0x38, 0x64)
GRIS = RGBColor(0x59, 0x59, 0x59)

doc = Document(str(PLANTILLA))

# --- Limpiar cuerpo conservando la sección (encabezado/pie institucionales) ---
cuerpo = doc.element.body
for hijo in list(cuerpo.iterchildren()):
    if hijo.tag == qn("w:sectPr"):
        continue
    cuerpo.remove(hijo)

estilo_normal = doc.styles["Normal"]
# No se modifica «Normal»: el encabezado institucional hereda de ese estilo y se
# desbordaría. El formato del cuerpo se aplica directamente a cada run.

for nombre in ("Heading 1", "Heading 2", "Heading 3"):
    estilo = doc.styles[nombre]
    estilo.font.name = "Arial"
    estilo.font.color.rgb = AZUL
    estilo.font.bold = True
doc.styles["Heading 1"].font.size = Pt(14)
doc.styles["Heading 2"].font.size = Pt(12)
doc.styles["Heading 3"].font.size = Pt(11)


def _formatear_run(run, tamano=11, negrita=False, cursiva=False, color=None, fuente="Arial"):
    run.font.name = fuente
    run.font.size = Pt(tamano)
    run.bold = negrita
    run.italic = cursiva
    if color:
        run.font.color.rgb = color


def parrafo(texto="", negrita=False, cursiva=False, tamano=11, color=None, alineacion=None,
            espacio_despues=6, espacio_antes=0, estilo=None):
    p = doc.add_paragraph(style=estilo)
    if texto:
        run = p.add_run(texto)
        _formatear_run(run, tamano=tamano, negrita=negrita, cursiva=cursiva, color=color)
    p.paragraph_format.space_after = Pt(espacio_despues)
    p.paragraph_format.space_before = Pt(espacio_antes)
    if alineacion is not None:
        p.alignment = alineacion
    return p


def titulo(texto, nivel=1):
    p = doc.add_heading(texto, level=nivel)
    p.paragraph_format.space_before = Pt(12 if nivel == 1 else 8)
    p.paragraph_format.space_after = Pt(6)
    for run in p.runs:
        run.font.name = "Arial"
    return p


def vineta(texto):
    p = doc.add_paragraph(style="List Bullet")
    run = p.add_run(texto)
    _formatear_run(run)
    p.paragraph_format.left_indent = Cm(0.75)
    p.paragraph_format.first_line_indent = Cm(-0.4)
    p.paragraph_format.space_after = Pt(4)
    return p


def paso(indice, texto):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(f"{indice}. ")
    _formatear_run(run, negrita=True)
    run = p.add_run(texto)
    _formatear_run(run)
    return p


def campo(etiqueta, texto):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(f"{etiqueta}: ")
    _formatear_run(run, negrita=True)
    run = p.add_run(texto)
    _formatear_run(run)
    return p


def codigo(texto):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.8)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(texto)
    _formatear_run(run, tamano=9, fuente="Consolas")
    return p


def _sombreado(celda, color="1F3864"):
    propiedades = OxmlElement("w:shd")
    propiedades.set(qn("w:fill"), color)
    celda._tc.get_or_add_tcPr().append(propiedades)


def _repetir_encabezado(fila):
    propiedades = OxmlElement("w:tblHeader")
    fila._tr.get_or_add_trPr().append(propiedades)


def tabla(encabezados, filas, anchos=None, tamano=9):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False

    for i, texto in enumerate(encabezados):
        celda = t.rows[0].cells[i]
        celda.text = ""
        p = celda.paragraphs[0]
        run = p.add_run(texto)
        run.bold = True
        run.font.size = Pt(tamano)
        run.font.name = "Arial"
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        _sombreado(celda)

    for fila in filas:
        celdas = t.add_row().cells
        for i, valor in enumerate(fila):
            celdas[i].text = ""
            p = celdas[i].paragraphs[0]
            run = p.add_run(str(valor))
            run.font.size = Pt(tamano)
            run.font.name = "Arial"
            p.paragraph_format.space_after = Pt(2)

    _repetir_encabezado(t.rows[0])
    if anchos:
        for fila in t.rows:
            for i, ancho in enumerate(anchos):
                fila.cells[i].width = Cm(ancho)

    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


# ======================================================================
# PORTADA
# ======================================================================
for _ in range(3):
    parrafo("")
parrafo("Auditoría Web Backend IA", negrita=True, tamano=24, color=AZUL,
        alineacion=WD_ALIGN_PARAGRAPH.CENTER, espacio_despues=4)
parrafo("Agente conversacional + MCP + RAG", negrita=True, tamano=15, color=GRIS,
        alineacion=WD_ALIGN_PARAGRAPH.CENTER, espacio_despues=18)
parrafo("Laboratorio 4", negrita=True, tamano=14, alineacion=WD_ALIGN_PARAGRAPH.CENTER,
        espacio_despues=4)
parrafo("Proyecto: Kohem Chemicals", tamano=12, alineacion=WD_ALIGN_PARAGRAPH.CENTER,
        espacio_despues=36)

tabla(
    ["Campo", "Valor"],
    [
        ["Estudiante", "Nombre del Estudiante"],
        ["Materia", "Calidad de Software y Auditoría de Sistemas"],
        ["Programa", "Tecnología de Desarrollo de Software"],
        ["Institución", "Institución Universitaria Pascual Bravo"],
        ["Versión auditada", "Kohem Chemicals MVP · rama lab4-mcp-rag"],
        ["Fecha", "10/11/2026"],
    ],
    anchos=[5.0, 10.0],
    tamano=10,
)

for _ in range(4):
    parrafo("")
parrafo("Documento adaptado del laboratorio original de calculadora FastAPI al backend "
        "de Kohem Chemicals. Conserva los diez casos P01–P10 y sustituye los componentes "
        "matemáticos por las reglas de negocio, el adaptador RAG y el servidor MCP del MVP.",
        cursiva=True, tamano=9, color=GRIS, alineacion=WD_ALIGN_PARAGRAPH.CENTER)

doc.add_page_break()

# ======================================================================
# 1. DESCRIPCIÓN
# ======================================================================
titulo("1. Descripción del proyecto")

parrafo("Kohem Chemicals es un Sistema de Información Transaccional para una distribuidora de "
        "materias primas: catálogo e inventario, registro de pedidos, asesoría con agente "
        "conversacional y auditoría de operaciones. El MVP está construido con FastAPI, "
        "SQLAlchemy asíncrono y SQLite en el backend, y React con Vite en el frontend.")
parrafo("El backend incorpora un asistente que recibe un mensaje en lenguaje natural, recupera "
        "políticas comerciales mediante un adaptador RAG, invoca herramientas de catálogo, stock "
        "y cotización a través de un servidor MCP real y devuelve una respuesta estructurada. La "
        "arquitectura es Onion: dominio, aplicación, infraestructura y presentación.")
parrafo("La auditoría se concentra en la corrección de los cálculos de pedido, la validación de "
        "solicitudes, el contrato HTTP, la integración entre capas, el comportamiento del "
        "adaptador MCP y la aplicación de las reglas RAG. No se realizan pruebas destructivas ni "
        "de carga.")

parrafo("Limitaciones declaradas de la versión auditada", negrita=True, espacio_antes=6)
vineta("El asistente funciona sin modelo externo por defecto: la intención se identifica con "
       "reglas léxicas y expresiones regulares. Si se configura DEEPSEEK_API_KEY, un modelo de "
       "lenguaje interpreta la consulta; con AI_MODE=conversacional también redacta la respuesta "
       "usando las cifras calculadas por el dominio.")
vineta("El RAG es un adaptador simulado en memoria que recupera reglas por palabras clave, no una "
       "base vectorial con búsqueda semántica.")
vineta("El asistente cotiza y consulta stock, pero no registra pedidos ni consulta por identificador.")
parrafo("Estas características deben registrarse como limitaciones funcionales de la versión "
        "auditada, no como fallos de un LLM real.", cursiva=True)

# ======================================================================
# 2. OBJETIVO GENERAL
# ======================================================================
titulo("2. Objetivo general")
parrafo("Ejecutar pruebas funcionales y de calidad sobre el backend de Kohem Chemicals, "
        "verificando la corrección de las reglas de negocio y la integración entre presentación, "
        "aplicación, dominio, RAG y MCP.")

titulo("3. Objetivos específicos")
for texto in (
    "Verificar los cálculos de subtotal, IVA, tope comercial y descuento de stock.",
    "Evaluar las validaciones de entrada y el tratamiento de errores, incluido el contraste con "
    "los endpoints legados.",
    "Comprobar el contrato de la API mediante Swagger y solicitudes HTTP.",
    "Verificar la comunicación entre el caso de uso y el adaptador MCP, incluido el transporte stdio.",
    "Evaluar la recuperación y aplicación de reglas del adaptador RAG.",
    "Comprobar la separación de responsabilidades entre las capas Onion.",
    "Ejecutar las pruebas automatizadas existentes y documentar hallazgos y correcciones.",
):
    vineta(texto)

# ======================================================================
# 4. ALCANCE
# ======================================================================
titulo("4. Alcance")
parrafo("Se auditan los siguientes archivos del MVP, ubicados en "
        "«1. Diagnostico Auditoria/MVP»:")

tabla(
    ["Archivo", "Capa", "Qué se audita"],
    [
        ["app/domain/services.py", "Dominio", "Subtotal, IVA, tope comercial y stock mínimo."],
        ["app/domain/entities.py", "Dominio", "Entidades puras, sin frameworks."],
        ["app/application/ports.py", "Aplicación", "Contratos IRagRepository e IMcpToolExecutor."],
        ["app/application/ai_use_cases.py", "Aplicación", "Orquestación RAG → MCP → respuesta."],
        ["app/infrastructure/mock_vector_db.py", "Infraestructura", "Recuperación de políticas por palabras clave."],
        ["app/infrastructure/mcp_server.py", "Infraestructura", "Herramientas MCP y transporte stdio."],
        ["app/infrastructure/deepseek_llm.py", "Infraestructura", "Motor de lenguaje opcional (DeepSeek)."],
        ["app/infrastructure/repositories.py", "Infraestructura", "Acceso a SQLite."],
        ["app/presentation/routers/ai_router.py", "Presentación", "Contrato HTTP y validación del mensaje."],
        ["app/presentation/validacion.py", "Presentación", "Validación centralizada y errores 422/400."],
        ["app/presentation/dependencies.py", "Presentación", "Inyección de dependencias."],
        ["tests/ (5 archivos)", "Pruebas", "Suite automatizada del dominio, MCP, IA y HTTP."],
        ["docs/laboratorio4/", "Evidencias", "Scripts f01–f12, JSON y consolas."],
    ],
    anchos=[6.4, 3.2, 6.0],
)

parrafo("Quedan fuera del alcance: el frontend React, la interfaz de usuario, las pruebas de "
        "carga y cualquier prueba destructiva. Los endpoints de materias primas y pedidos se usan "
        "solo como contraste del manejo de errores.")

# ======================================================================
# 5. ARQUITECTURA
# ======================================================================
titulo("5. Arquitectura auditada")
tabla(
    ["Capa", "Responsabilidad", "Depende de"],
    [
        ["Dominio", "Reglas puras de precio, IVA, tope y stock.", "Nada externo"],
        ["Aplicación", "Caso de uso que orquesta RAG y MCP.", "Puertos (interfaces)"],
        ["Infraestructura", "RAG simulado, servidor MCP y repositorios SQLite.", "Dominio y SDK de MCP"],
        ["Presentación", "Rutas FastAPI, validación y dependencias.", "Aplicación"],
    ],
    anchos=[3.2, 8.4, 4.0],
)
parrafo("Flujo de una solicitud:", negrita=True)
codigo("POST /api/v1/ai/chat\n"
       "  → AIAssistantUseCase.respond()\n"
       "      → IRagRepository.buscar_contexto()        (políticas comerciales)\n"
       "      → ILLMProvider.interpretar()               (opcional: DeepSeek; si falla, reglas)\n"
       "      → IMcpToolExecutor.ejecutar_herramienta()  (listar_materiales / consultar_stock / calcular_pedido)\n"
       "          → MCPServer (protocolo MCP)\n"
       "              → PricingDomainService + SQLiteRawMaterialRepository\n"
       "  → AIChatResponseDTO { response, transfer_to_employee, reason, motor, datos }")

titulo("5.1 Motor de inteligencia", nivel=2)
parrafo("El asistente tiene dos motores intercambiables y siempre deja constancia del usado en el "
        "campo «motor» de la respuesta:")
vineta("Reglas (por defecto): recuperación RAG por palabras clave, expresiones regulares para "
       "cantidades y unidades, y comparación difusa para nombres de materiales. No requiere red.")
vineta("DeepSeek (opcional): si DEEPSEEK_API_KEY está definida, el modelo interpreta la intención "
       "y las entidades y devuelve un JSON validado. Si la red falla, el JSON es inválido o la "
       "clave no existe, el caso de uso continúa con reglas.")
parrafo("Configuración (archivo .env, nunca versionado):", negrita=True, espacio_antes=6)
codigo("DEEPSEEK_API_KEY=sk-...\n"
       "DEEPSEEK_BASE_URL=https://api.deepseek.com\n"
       "DEEPSEEK_MODEL=deepseek-chat\n"
       "LLM_TIMEOUT_SECONDS=20\n"
       "AI_MODE=conversacional\n"
       "AI_HISTORY_MAX=8")
parrafo("El adaptador está en app/infrastructure/deepseek_llm.py y usa el formato JSON de la API "
        "compatible con OpenAI. La clave no se registra en logs ni en evidencias.")

titulo("5.2 Modo conversacional", nivel=2)
parrafo("El comportamiento se controla con la variable AI_MODE:")
tabla(
    ["AI_MODE", "Comportamiento", "Uso recomendado"],
    [
        ["asistente (por defecto)", "Plantilla fija + reglas o DeepSeek para la intención.",
         "Auditoría P01–P11: respuestas reproducibles."],
        ["conversacional", "DeepSeek redacta la respuesta con los datos calculados por el dominio.",
         "Atención al cliente y P12."],
    ],
    anchos=[3.6, 7.2, 4.8],
)
parrafo("En modo conversacional el modelo actúa como asesor comercial: recibe el catálogo real "
        "(materiales, categorías, precios y stock) y las políticas aplicables, además de un bloque "
        "«Datos verificados» con las cifras calculadas. Puede responder preguntas abiertas sobre "
        "qué vende la empresa, orientar al cliente y pedir la información que falte, sin inventar "
        "precios ni existencias. Si el modelo falla, se devuelve la plantilla del modo asistente.")
parrafo("El cliente puede enviar el historial para dar contexto:")
codigo('{\n  "message": "¿Y cuánto hay de ese material?",\n  "historial": [\n'
       '    {"role": "user", "content": "Quiero dos kilos de glicerina"},\n'
       '    {"role": "assistant", "content": "..."}\n  ]\n}')
parrafo("Para ejecutar f01–f11 el backend debe estar en AI_MODE=asistente. El caso f12 levanta su "
        "propia instancia en el puerto 8001 con AI_MODE=conversacional, de modo que la auditoría "
        "no depende del modo configurado en el servicio principal.", tamano=9, cursiva=True)
parrafo("El servidor no guarda conversaciones: el historial lo envía el cliente y se recorta a "
        "AI_HISTORY_MAX mensajes. La respuesta incluye el campo «datos» con las cifras usadas.",
        tamano=9, cursiva=True)

# ======================================================================
# 6. ENTORNO
# ======================================================================
titulo("6. Preparación del entorno")
paso(1, "Abrir PowerShell en «1. Diagnostico Auditoria\\MVP».")
paso(2, "Instalar dependencias si hace falta (incluye mcp>=2.3.0):")
codigo(".\\venv\\Scripts\\python.exe -m pip install -r requirements.txt")
paso(3, "Opcional: copiar .env.example a .env, completar DEEPSEEK_API_KEY y elegir AI_MODE "
        "(asistente o conversacional). Sin clave, el asistente usa el motor de reglas.")
paso(4, "Iniciar el servicio:")
codigo(".\\venv\\Scripts\\python.exe -m uvicorn app.presentation.main:app --reload")
paso(5, "Confirmar que el servidor escucha en http://127.0.0.1:8000 y abrir Swagger en "
        "http://127.0.0.1:8000/docs.")
paso(6, "En otra terminal, ejecutar la suite:")
codigo(".\\venv\\Scripts\\python.exe -m pytest -q")
paso(7, "Ejecutar los scripts de evidencia desde la carpeta docs\\laboratorio4:")
codigo("cd docs\\laboratorio4\n..\\..\\venv\\Scripts\\python.exe f01_operaciones.py")
paso(8, "El servidor MCP también puede levantarse de forma autónoma por stdio (no es HTTP):")
codigo(".\\venv\\Scripts\\python.exe -m app.infrastructure.mcp_server")

parrafo("Credenciales de demostración", negrita=True, espacio_antes=6)
tabla(
    ["Rol", "Usuario", "Contraseña"],
    [
        ["admin", "admin", "AdminPass123!"],
        ["cliente", "cliente", "ClientPass123!"],
    ],
    anchos=[4.0, 5.0, 6.0],
)
parrafo("El token dura 60 minutos y se envía como «Authorization: Bearer <token>».",
        cursiva=True, tamano=9)

# ======================================================================
# 7. METODOLOGÍA
# ======================================================================
titulo("7. Metodología")
parrafo("Se aplica el ciclo Planear–Hacer–Verificar–Actuar (PHVA):")
tabla(
    ["Fase", "Actividad en el laboratorio", "Evidencia"],
    [
        ["Planear", "Definir casos, datos de entrada y resultado esperado.", "Esta guía, sección 8"],
        ["Hacer", "Ejecutar pytest, Swagger y los scripts f01–f12.", "evidencias/*.json y *.txt"],
        ["Verificar", "Comparar lo obtenido con lo esperado y clasificar hallazgos.", "RESULTADOS_LAB4.md"],
        ["Actuar", "Proponer correcciones y repetir las pruebas afectadas.", "Informe final"],
    ],
    anchos=[3.0, 8.2, 4.4],
)

# ======================================================================
# 8. CASOS
# ======================================================================
titulo("8. Casos de auditoría y pruebas funcionales")


def caso(codigo_caso, nombre, componente, procedimiento, esperado, evidencia):
    titulo(f"{codigo_caso} — {nombre}", nivel=2)
    campo("Componente", componente)
    parrafo("Procedimiento:", negrita=True, espacio_despues=2)
    for i, texto in enumerate(procedimiento, start=1):
        paso(i, texto)
    campo("Resultado esperado", esperado)
    campo("Evidencia", evidencia)


caso(
    "P01", "Operaciones del dominio y cálculo de pedido",
    "Dominio: app/domain/services.py (PricingDomainService) y herramienta MCP calcular_pedido; "
    "prueba tests/test_pricing_domain.py.",
    [
        "Ejecutar «pytest -q tests/test_pricing_domain.py».",
        "Comprobar subtotal 18.000 × 2 = 36.000, total de dos ítems, IVA del 19% sobre 48.000 = 9.120 "
        "y redondeo a dos decimales.",
        "Desde Swagger, enviar «Cotiza 2 kg de glicerina y 3 kg de ácido cítrico» y comparar el "
        "subtotal con los precios de GET /materials.",
        "Ejecutar el script f01_operaciones.py y revisar f01_operaciones.json.",
    ],
    "Las cuatro comprobaciones del dominio son correctas y la cotización coincide con el catálogo.",
    "f01_operaciones.json · salida de pytest · captura de Swagger",
)

caso(
    "P02", "Stock insuficiente y consistencia transaccional",
    "Dominio y aplicación: calcular_pedido, OrderUseCases.create_order; pruebas "
    "tests/test_mcp_adapter.py.",
    [
        "Ejecutar «pytest -q tests/test_mcp_adapter.py».",
        "Desde Swagger, cotizar 10.000 kg de glicerina y revisar el código HTTP y el detalle.",
        "Crear un pedido con dos ítems donde el segundo supera el stock y comprobar que el stock "
        "del primer ítem no cambia.",
        "Enviar un pedido con cantidad 0 y comprobar que devuelve 422.",
        "Ejecutar f02_stock.py.",
    ],
    "No se permite la sobreventa, un pedido fallido no reserva stock parcialmente y la cantidad 0 "
    "se rechaza con 422; ninguna de estas rutas produce HTTP 500.",
    "f02_stock.json",
)

caso(
    "P03", "Valores límite: negativos, decimales y redondeo",
    "Dominio y validaciones: RawMaterialCreateDTO, OrderItemCreateDTO y PricingDomainService.",
    [
        "Verificar en el dominio: subtotal(0.1, 3) = 0.3, subtotal(1234.567, 3) = 3703.70 y "
        "subtotal(18000, 0.5) = 9000.0.",
        "Crear una materia prima con price = -100 y otra con stock = -1; registrar el código HTTP.",
        "Enviar un pedido con quantity = -2 y otro con quantity = 0.5.",
        "Crear un material con precio 1234.567, pedir 3 unidades y comprobar el total 3703.70.",
        "Ejecutar f03_limites.py y limpiar los datos temporales.",
    ],
    "Los resultados conservan el signo y la precisión; los valores inválidos se rechazan con 422 "
    "en todos los endpoints, incluidos los módulos legados.",
    "f03_limites.json",
)

caso(
    "P04", "Contrato HTTP y validación Pydantic en /ai/chat",
    "Presentación: POST /api/v1/ai/chat, AIChatRequestDTO y ai_router.py.",
    [
        "En Swagger ejecutar una solicitud válida: {\"message\": \"Hola\"}.",
        "Probar mensaje ausente, mensaje vacío, solo espacios y tipo no textual.",
        "Probar un campo adicional y el envío como formulario.",
        "Probar Content-Type text/plain, JSON mal formado y UTF-8 inválido.",
        "Repetir sin token y contrastar con POST /materials usando un precio inválido.",
        "Ejecutar f04_contrato.py.",
    ],
    "Solicitud válida 200; errores de esquema 422; tipo de contenido 415; cuerpo inválido 400; sin "
    "token 401. El endpoint legado /materials responde igual (422) tras la corrección.",
    "f04_contrato.json",
)

caso(
    "P05", "Interpretación del mensaje y extracción de cantidades",
    "Aplicación: app/application/ai_use_cases.py (reglas léxicas y expresión regular de cantidades).",
    [
        "Enviar «Cotiza 2 kg de glicerina» y sus variantes en mayúsculas y sin espacio («2kg»).",
        "Probar «Necesito 2 kg de glicerina», «Cotiza 2 kilos de glicerina» y «Cotiza dos kg de glicerina».",
        "Probar dos ítems en una frase y un material inexistente.",
        "Probar una negación («No tengo problemas con mi pedido») y una consulta con término técnico.",
        "Ejecutar f05_prompt.py y comparar esperado contra real.",
    ],
    "Las diez variantes se resuelven correctamente: números en palabras, unidades alternativas, "
    "negaciones que no deben transferir y términos técnicos que no anulan la cotización.",
    "f05_prompt.json",
)

caso(
    "P06", "Recuperación y aplicación de reglas RAG",
    "Infraestructura: mock_vector_db.py; aplicación: ai_use_cases.py.",
    [
        "Inspeccionar buscar_contexto() con mensajes que contengan «IVA», «impuesto», «tope», "
        "«stock» y sin palabras clave.",
        "Desde Swagger, cotizar 2 kg de glicerina con IVA y verificar 36.000 + 6.840 = 42.840.",
        "Cotizar 1.000 kg de una materia prima de alto valor con «tope máximo» y verificar el "
        "recorte a 50.000.000.",
        "Probar «al máximo» sin pedir el tope y registrar si la regla se aplica igualmente.",
        "Ejecutar f06_rag.py.",
    ],
    "El adaptador recupera el contexto esperado y el caso de uso aplica la regla correspondiente. "
    "El tope solo se activa con términos explícitos («tope», «límite», «no superar»), no con "
    "«al máximo».",
    "f06_rag.json",
)

caso(
    "P07", "Adaptador MCP: contrato y transporte real",
    "Infraestructura: app/infrastructure/mcp_server.py; pruebas tests/test_mcp_adapter.py.",
    [
        "Ejecutar «pytest -q tests/test_mcp_adapter.py».",
        "Listar las herramientas y revisar el esquema de calcular_pedido: items requerido, "
        "aplicar_iva y aplicar_tope opcionales.",
        "Invocar listar_materiales, consultar_stock y calcular_pedido.",
        "Comprobar que una herramienta inexistente y un pedido sin stock producen error controlado.",
        "Ejecutar f07_mcp.py, que además abre una sesión MCP completa por stdio "
        "(initialize → list_tools → call_tool).",
    ],
    "El adaptador delega en el dominio, respeta el contrato y funciona por transporte real. "
    "Estas pruebas sí demuestran una sesión MCP completa, a diferencia de una llamada directa al método.",
    "f07_mcp.json · tests/test_mcp_adapter.py",
)

caso(
    "P08", "Integración de extremo a extremo",
    "Todas las capas: presentación → aplicación → RAG/MCP → dominio → SQLite.",
    [
        "Ejecutar «pytest -q tests/test_ai_presentation.py».",
        "Desde Swagger, enviar una cotización con IVA y revisar status y contenido.",
        "Crear un pedido de 2 kg, verificar el descuento de stock y el registro en audit-logs.",
        "Cancelar el pedido, comprobar la restauración del stock y el nuevo registro de auditoría.",
        "Ejecutar f08_e2e.py.",
    ],
    "La API responde de forma coherente: 200 en la cotización, 201 al crear, stock descontado y "
    "restaurado, y ambos eventos trazados en auditoría.",
    "f08_e2e.json",
)

caso(
    "P09", "Manejo de errores y robustez",
    "Presentación y aplicación: ai_router.py, ai_use_cases.py y routers legados.",
    [
        "Probar mensaje no reconocido, mensaje vacío, JSON mal formado y Content-Type inválido.",
        "Probar campos adicionales y revisar que no alteren el comportamiento.",
        "Probar un pedido inválido y una materia prima inválida en los endpoints legados.",
        "Revisar que las respuestas no expongan trazas, nombres de archivos ni paquetes internos.",
        "Ejecutar f09_errores.py.",
    ],
    "Los errores se comunican con 4xx y sin filtrar información interna; no quedan respuestas 500 "
    "en ninguno de los endpoints auditados.",
    "f09_errores.json",
)

caso(
    "P10", "Regresión y consistencia de la arquitectura",
    "Todas las capas y la suite completa de pruebas.",
    [
        "Ejecutar «pytest -q» y guardar la salida.",
        "Relacionar cada archivo de prueba con la capa que verifica.",
        "Analizar los imports del dominio y de la aplicación: no deben depender de FastAPI, "
        "SQLAlchemy ni MCP.",
        "Registrar los fallos preexistentes y repetir las pruebas tras cualquier corrección.",
        "Ejecutar f10_regresion.py.",
    ],
    "Suite reproducible, responsabilidades por capa identificadas y defectos trazables. Los dos "
    "fallos preexistentes (test_auth y test_order_permissions) se documentan sin confundirlos con "
    "regresiones del laboratorio.",
    "f10_regresion.json · f10_pytest.txt",
)

caso(
    "P11", "Motor de lenguaje y respaldo por reglas",
    "Aplicación: ai_use_cases.py; infraestructura: deepseek_llm.py (API compatible con OpenAI).",
    [
        "Sin DEEPSEEK_API_KEY, ejecutar f11_deepseek.py y comprobar que el campo «motor» es «reglas».",
        "Copiar .env.example a .env, completar la clave y reiniciar el backend.",
        "Repetir la ejecución y comprobar que «motor» corresponde al modo configurado "
        "(«deepseek» o «deepseek-conversacional») y medir la latencia.",
        "Forzar un fallo (clave inválida o sin red) y verificar que la respuesta sigue llegando por reglas.",
    ],
    "El asistente responde con el motor configurado, informa cuál utilizó y cae a reglas ante "
    "cualquier fallo del modelo, sin exponer la clave ni trazas.",
    "f11_deepseek.json",
)

caso(
    "P12", "Modo conversacional y memoria de la conversación",
    "Aplicación: ai_use_cases.py; infraestructura: deepseek_llm.py; configuración: AI_MODE.",
    [
        "Levantar una instancia con AI_MODE=conversacional (f12 lo hace en el puerto 8001).",
        "Enviar un saludo y comprobar que responde de forma natural o con la plantilla de respaldo.",
        "Preguntar «¿Qué venden?» y verificar que lista materiales reales del catálogo.",
        "Enviar una cotización y verificar que el campo «datos» trae subtotal, IVA y total calculados.",
        "Enviar un seguimiento con historial («¿Y cuánto hay de ese material?») y revisar que el "
        "contrato lo acepta y que el contexto se usa.",
        "Ejecutar f12_conversacional.py con y sin clave.",
    ],
    "El modo conversacional responde como asesor, lista el catálogo real, mantiene el contrato, "
    "devuelve cifras estructuradas y cae a la plantilla si el modelo no está disponible.",
    "f12_conversacional.json",
)

# ======================================================================
# 9. MATRIZ
# ======================================================================
titulo("9. Matriz resumida de pruebas")
tabla(
    ["ID", "Prueba", "Capa principal", "Evidencia"],
    [
        ["P01", "Operaciones y cálculo de pedido", "Dominio", "Salida pytest / f01"],
        ["P02", "Stock y consistencia transaccional", "Dominio/Aplicación", "f02_stock.json"],
        ["P03", "Negativos y decimales", "Dominio/Presentación", "f03_limites.json"],
        ["P04", "Contrato HTTP/Pydantic", "Presentación", "f04_contrato.json"],
        ["P05", "Prompt y extracción de cantidades", "Aplicación", "f05_prompt.json"],
        ["P06", "Reglas RAG", "Infraestructura/Aplicación", "f06_rag.json"],
        ["P07", "Adaptador MCP y transporte", "Infraestructura", "f07_mcp.json"],
        ["P08", "Flujo extremo a extremo", "Todas", "f08_e2e.json"],
        ["P09", "Errores y robustez", "Presentación/Aplicación", "f09_errores.json"],
        ["P10", "Regresión y arquitectura", "Todas", "f10_regresion.json"],
        ["P11", "Motor DeepSeek y respaldo", "Aplicación/Infraestructura", "f11_deepseek.json"],
        ["P12", "Modo conversacional", "Aplicación/Infraestructura", "f12_conversacional.json"],
    ],
    anchos=[1.6, 6.6, 4.4, 3.0],
)

# ======================================================================
# 10. ENTREGABLES Y RÚBRICA
# ======================================================================
titulo("10. Entregables")
for texto in (
    "Informe en PDF y DOCX con los hallazgos, su severidad y las correcciones propuestas.",
    "Carpeta docs/laboratorio4 con los scripts f01–f12 y la carpeta evidencias.",
    "Salida completa de pytest (f10_pytest.txt) y los JSON crudos de cada caso.",
    "Enlace al repositorio, rama lab4-mcp-rag, sin datos personales ni tokens.",
    "Tabla de adaptación respecto a la guía original (Anexo A).",
):
    vineta(texto)

titulo("11. Criterios de evaluación")
tabla(
    ["Criterio", "Peso", "Descripción"],
    [
        ["Ejecución de los casos", "30%", "Los diez casos se ejecutan y se documentan."],
        ["Evidencias", "25%", "JSON, consolas y capturas verificables y sanitizadas."],
        ["Hallazgos", "20%", "Defectos identificados con severidad y justificación."],
        ["Correcciones propuestas", "15%", "Propuestas viables y trazables a cada hallazgo."],
        ["Arquitectura", "10%", "Análisis de capas, puertos y adaptadores."],
    ],
    anchos=[4.6, 2.0, 9.0],
)

# ======================================================================
# ANEXO A
# ======================================================================
doc.add_page_break()
titulo("Anexo A. Correspondencia con la guía original")
tabla(
    ["Guía original (calculadora)", "Adaptación en Kohem Chemicals"],
    [
        ["Cuatro operaciones básicas", "PricingDomainService: subtotal, total, IVA y tope"],
        ["División por cero", "Stock insuficiente y consistencia transaccional"],
        ["calculator_use_case.py", "ai_use_cases.AIAssistantUseCase"],
        ["mock_vector_db con impuesto 15% y tope 1000", "IVA 19%, tope 50.000.000 COP y stock mínimo 10 kg"],
        ["mcp_server con la herramienta calcular", "Kohem-Chemicals-MCP: listar_materiales, consultar_stock, calcular_pedido"],
        ["Componente LLM simulado", "Reglas por defecto y DeepSeek opcional (deepseek_llm.py)"],
        ["Conversación de un solo turno", "Modo conversacional con historial y redacción del modelo"],
        ["POST /api/v1/calcular", "POST /api/v1/ai/chat"],
        ["Puerto 7000", "Puerto 8000"],
        ["Respuesta CalculoResult", "AIChatResponseDTO (response, transfer_to_employee, reason, motor)"],
    ],
    anchos=[7.2, 8.4],
)

# ======================================================================
# ANEXO B — RESULTADOS
# ======================================================================
titulo("Anexo B. Resultados de la ejecución de referencia")
parrafo("Valores obtenidos el 10/11/2026 sobre la rama lab4-mcp-rag, después de aplicar las "
        "correcciones. La evidencia completa está en docs/laboratorio4/evidencias/despues.",
        tamano=9, cursiva=True)
_resumen_pytest = json.loads((BASE / "evidencias" / "despues" / "f10_regresion.json").read_text(encoding="utf-8"))["pytest"]["resumen"]
parrafo(f"Suite completa: {_resumen_pytest}.", tamano=9, cursiva=True)

EVID_ANTES = BASE / "evidencias" / "antes"
EVID_DESPUES = BASE / "evidencias" / "despues"


def _estado(carpeta: Path, nombre: str) -> str:
    ruta = carpeta / nombre
    if not ruta.exists():
        return "Sin evidencia"
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    if nombre == "f05_prompt.json":
        return f"{datos['coinciden']}/{datos['total']} prompts"
    if nombre == "f09_errores.json":
        fallos = datos["resumen"]["errores_500"]
        return "Sin HTTP 500" if not fallos else "Parcial: HTTP 500 en " + ", ".join(fallos)
    criterios = datos.get("criterios", {})
    fallidos = [
        clave for clave, valor in criterios.items() if valor is False and clave != "cumple_todos"
    ]
    return "Cumple" if not fallidos else "Parcial: " + ", ".join(fallidos)


tabla(
    ["ID", "Caso", "Resultado después de corregir"],
    [
        ["P01", "Operaciones y cálculo", _estado(EVID_DESPUES, "f01_operaciones.json")],
        ["P02", "Stock y atomicidad", _estado(EVID_DESPUES, "f02_stock.json")],
        ["P03", "Límites y precisión", _estado(EVID_DESPUES, "f03_limites.json")],
        ["P04", "Contrato HTTP", _estado(EVID_DESPUES, "f04_contrato.json")],
        ["P05", "Interpretación", _estado(EVID_DESPUES, "f05_prompt.json")],
        ["P06", "Reglas RAG", _estado(EVID_DESPUES, "f06_rag.json")],
        ["P07", "Adaptador MCP", _estado(EVID_DESPUES, "f07_mcp.json")],
        ["P08", "Extremo a extremo", _estado(EVID_DESPUES, "f08_e2e.json")],
        ["P09", "Errores", _estado(EVID_DESPUES, "f09_errores.json")],
        ["P10", "Regresión y arquitectura", _estado(EVID_DESPUES, "f10_regresion.json")],
        ["P11", "Motor DeepSeek / reglas", _estado(EVID_DESPUES, "f11_deepseek.json")],
        ["P12", "Modo conversacional", _estado(EVID_DESPUES, "f12_conversacional.json")],
    ],
    anchos=[1.6, 4.6, 9.4],
)

# ======================================================================
# ANEXO C — HALLAZGOS
# ======================================================================
titulo("Anexo C. Hallazgos y estado de corrección")
tabla(
    ["ID", "Hallazgo", "Severidad", "Estado"],
    [
        ["H-L4-01", "El «LLM» era un motor de reglas limitado.", "Media",
         "Mitigado: DeepSeek, modo conversacional y reglas ampliadas"],
        ["H-L4-02", "El RAG activaba el tope con «al máximo».", "Media",
         "Resuelto: coincidencia por palabra completa"],
        ["H-L4-03", "Endpoints legados devolvían 500 al validar.", "Media",
         "Resuelto: validación centralizada en 422"],
        ["H-L4-04", "Un término técnico anulaba la cotización.", "Baja",
         "Resuelto: la cotización tiene prioridad"],
        ["H-L4-05", "La ruta de SQLite depende del directorio de trabajo.", "Baja",
         "Pendiente"],
        ["H-L4-06", "SECRET_KEY por defecto sin validación al arrancar.", "Media",
         "Pendiente"],
        ["H-L4-07", "El servidor MCP no aplica autenticación.", "Baja",
         "Pendiente (MCP solo local)"],
        ["H-L4-08", "El asistente no registra pedidos ni consulta por ID.", "Informativa",
         "Aceptado por alcance"],
    ],
    anchos=[2.2, 8.4, 2.2, 5.0],
    tamano=8,
)

# ======================================================================
# ANEXO D — ANTES / DESPUÉS
# ======================================================================
titulo("Anexo D. Comparación antes y después de las correcciones")
parrafo("Misma batería de scripts ejecutada antes y después de la fase Actuar del ciclo PHVA.",
        tamano=9, cursiva=True)
tabla(
    ["ID", "Antes", "Después"],
    [
        ["P01", _estado(EVID_ANTES, "f01_operaciones.json"), _estado(EVID_DESPUES, "f01_operaciones.json")],
        ["P02", _estado(EVID_ANTES, "f02_stock.json"), _estado(EVID_DESPUES, "f02_stock.json")],
        ["P03", _estado(EVID_ANTES, "f03_limites.json"), _estado(EVID_DESPUES, "f03_limites.json")],
        ["P04", _estado(EVID_ANTES, "f04_contrato.json"), _estado(EVID_DESPUES, "f04_contrato.json")],
        ["P05", _estado(EVID_ANTES, "f05_prompt.json"), _estado(EVID_DESPUES, "f05_prompt.json")],
        ["P06", _estado(EVID_ANTES, "f06_rag.json"), _estado(EVID_DESPUES, "f06_rag.json")],
        ["P07", _estado(EVID_ANTES, "f07_mcp.json"), _estado(EVID_DESPUES, "f07_mcp.json")],
        ["P08", _estado(EVID_ANTES, "f08_e2e.json"), _estado(EVID_DESPUES, "f08_e2e.json")],
        ["P09", _estado(EVID_ANTES, "f09_errores.json"), _estado(EVID_DESPUES, "f09_errores.json")],
        ["P10", _estado(EVID_ANTES, "f10_regresion.json"), _estado(EVID_DESPUES, "f10_regresion.json")],
        ["P11", "No existía", _estado(EVID_DESPUES, "f11_deepseek.json")],
        ["P12", "No existía", _estado(EVID_DESPUES, "f12_conversacional.json")],
    ],
    anchos=[1.6, 7.0, 7.0],
    tamano=8,
)

# Eliminar párrafos vacíos finales que generan una página en blanco.
nodos = [n for n in doc.element.body.iterchildren() if n.tag != qn("w:sectPr")]
for nodo in reversed(nodos):
    if nodo.tag == qn("w:p") and not "".join(nodo.itertext()).strip():
        doc.element.body.remove(nodo)
    else:
        break

# Cierre mínimo: Word exige un párrafo tras la última tabla, pero uno normal
# añadiría una página en blanco.
cierre = doc.add_paragraph()
cierre.paragraph_format.space_before = Pt(0)
cierre.paragraph_format.space_after = Pt(0)
cierre.paragraph_format.line_spacing = Pt(1)
run_cierre = cierre.add_run("")
run_cierre.font.size = Pt(1)

doc.save(str(SALIDA))
print(f"Documento generado: {SALIDA}")
print(f"Párrafos: {len(doc.paragraphs)} · Tablas: {len(doc.tables)}")

