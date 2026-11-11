"""Genera un guion breve de sustentación a partir del informe del Laboratorio 4."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = Path(__file__).resolve().parent
PLANTILLA = Path(r"D:\Descargas\Laboratorio 4 - Auditoria Backend IA.docx")
SALIDA = BASE / "GUION_SUSTENTACION_LAB4.docx"
AZUL = RGBColor(0x1F, 0x38, 0x64)
GRIS = RGBColor(0x59, 0x59, 0x59)

doc = Document(str(PLANTILLA))
cuerpo = doc.element.body
for hijo in list(cuerpo.iterchildren()):
    if hijo.tag == qn("w:sectPr"):
        continue
    cuerpo.remove(hijo)

for nombre in ("Heading 1", "Heading 2"):
    estilo = doc.styles[nombre]
    estilo.font.name = "Arial"
    estilo.font.color.rgb = AZUL
    estilo.font.bold = True
doc.styles["Heading 1"].font.size = Pt(13)
doc.styles["Heading 2"].font.size = Pt(11)


def _run(run, tamano=10.5, negrita=False, cursiva=False, color=None, fuente="Arial"):
    run.font.name = fuente
    run.font.size = Pt(tamano)
    run.bold = negrita
    run.italic = cursiva
    if color:
        run.font.color.rgb = color


def p(texto="", negrita=False, cursiva=False, tamano=10.5, color=None, alineacion=None,
      despues=4, antes=0):
    parrafo = doc.add_paragraph()
    if texto:
        _run(parrafo.add_run(texto), tamano=tamano, negrita=negrita, cursiva=cursiva, color=color)
    parrafo.paragraph_format.space_after = Pt(despues)
    parrafo.paragraph_format.space_before = Pt(antes)
    if alineacion is not None:
        parrafo.alignment = alineacion
    return parrafo


def h1(texto):
    parrafo = doc.add_heading(texto, level=1)
    parrafo.paragraph_format.space_before = Pt(10)
    parrafo.paragraph_format.space_after = Pt(4)
    for run in parrafo.runs:
        run.font.name = "Arial"
    return parrafo


def h2(texto):
    parrafo = doc.add_heading(texto, level=2)
    parrafo.paragraph_format.space_before = Pt(8)
    parrafo.paragraph_format.space_after = Pt(3)
    for run in parrafo.runs:
        run.font.name = "Arial"
    return parrafo


def bullet(texto, negrita=False):
    parrafo = doc.add_paragraph(style="List Bullet")
    _run(parrafo.add_run(texto), negrita=negrita)
    parrafo.paragraph_format.left_indent = Cm(0.7)
    parrafo.paragraph_format.first_line_indent = Cm(-0.35)
    parrafo.paragraph_format.space_after = Pt(2)
    return parrafo


def _sombreado(celda, color="1F3864"):
    props = OxmlElement("w:shd")
    props.set(qn("w:fill"), color)
    celda._tc.get_or_add_tcPr().append(props)


def tabla(encabezados, filas, anchos=None, tamano=9):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, texto in enumerate(encabezados):
        celda = t.rows[0].cells[i]
        celda.text = ""
        run = celda.paragraphs[0].add_run(texto)
        _run(run, tamano=tamano, negrita=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        _sombreado(celda)
    for fila in filas:
        celdas = t.add_row().cells
        for i, valor in enumerate(fila):
            celdas[i].text = ""
            parrafo = celdas[i].paragraphs[0]
            _run(parrafo.add_run(str(valor)), tamano=tamano)
            parrafo.paragraph_format.space_after = Pt(1)
    if anchos:
        for fila in t.rows:
            for i, ancho in enumerate(anchos):
                fila.cells[i].width = Cm(ancho)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return t


# ======================================================================
# TÍTULO
# ======================================================================
p("Guion de sustentación", negrita=True, tamano=20, color=AZUL, alineacion=WD_ALIGN_PARAGRAPH.CENTER, despues=2)
p("Laboratorio 4 · Auditoría Backend IA — Kohem Chemicals", tamano=12, color=GRIS,
  alineacion=WD_ALIGN_PARAGRAPH.CENTER, despues=10)

p("Cómo usar este documento", negrita=True, tamano=9, color=GRIS)
p("Es un resumen para estudiar, no un anexo del informe. En 5 minutos cubre qué se auditó, "
  "cómo funciona la IA, qué se encontró y qué responder si preguntan.", tamano=9, cursiva=True,
  color=GRIS, despues=8)

# ======================================================================
# 1. EN UNA FRASE
# ======================================================================
h1("1. En una frase")
p("«Auditamos el backend del MVP de Kohem Chemicals, en especial el asistente de IA, y "
  "verificamos con 12 casos y 75 pruebas que calcula bien los pedidos, valida las entradas, "
  "responde con datos reales y separa correctamente sus capas.»")

# ======================================================================
# 2. QUÉ ES EL PROYECTO
# ======================================================================
h1("2. Qué es Kohem Chemicals")
bullet("Distribuidora de materias primas para cosmética y aseo.")
bullet("MVP con FastAPI + SQLite en el backend y React en el frontend.")
bullet("Módulo de IA: recibe un mensaje, consulta políticas (RAG), ejecuta herramientas (MCP) "
       "y responde con precios y stock reales.")
bullet("Arquitectura Onion: dominio, aplicación, infraestructura y presentación.")

# ======================================================================
# 3. CÓMO FUNCIONA LA IA
# ======================================================================
h1("3. Cómo funciona la IA (lo más importante)")
p("Flujo de un mensaje:", negrita=True)
p("1. El cliente escribe en el chat.\n"
  "2. El backend busca políticas aplicables (IVA, tope, stock mínimo).\n"
  "3. Decide la intención: cotizar, consultar stock, asesoría o conversación.\n"
  "4. Ejecuta herramientas MCP que leen el catálogo y calculan el pedido.\n"
  "5. Responde con las cifras calculadas por el dominio.", tamano=9)

tabla(
    ["Pieza", "Qué hace", "En palabras simples"],
    [
        ["RAG", "Recupera políticas de negocio.", "Le da las reglas antes de responder."],
        ["MCP", "Expone catálogo, stock y cotización.", "Son las «manos» del asistente."],
        ["DeepSeek", "Interpreta y redacta (opcional).", "Es la voz, no la calculadora."],
        ["Dominio", "Calcula subtotal, IVA y tope.", "Es la calculadora confiable."],
    ],
    anchos=[2.8, 6.0, 6.8],
)

p("Dos modos:", negrita=True)
bullet("Asistente (por defecto): respuestas con plantilla, sin depender de internet. "
       "Ideal para auditar y para reproducir resultados.")
bullet("Conversacional: DeepSeek redacta como asesor comercial usando el catálogo y las cifras "
       "reales. Si falla o no hay clave, vuelve solo al modo asistente.")

# ======================================================================
# 4. QUÉ SE AUDITÓ
# ======================================================================
h1("4. Los 12 casos, agrupados")
tabla(
    ["Grupo", "Casos", "Qué se verificó"],
    [
        ["Cálculo y reglas", "P01–P03", "Subtotal, IVA, tope, stock, negativos y decimales."],
        ["Contrato y errores", "P04, P09", "Códigos 200/401/400/415/422, sin 500 ni fugas."],
        ["Lenguaje y RAG", "P05, P06", "Diez formas de pedir, IVA y tope solo cuando aplica."],
        ["Integración", "P07, P08", "MCP real por stdio, pedido, stock y auditoría."],
        ["Calidad y motor", "P10–P12", "75 pruebas, capas limpias, DeepSeek y conversación."],
    ],
    anchos=[3.6, 2.4, 9.6],
)
p("Resultado: los 12 casos cumplen. La suite quedó en 75 pruebas aprobadas y 0 fallos.")

# ======================================================================
# 5. HALLAZGOS
# ======================================================================
h1("5. Hallazgos abiertos (lo que aún se puede mejorar)")
tabla(
    ["ID", "Hallazgo", "Por qué importa", "Recomendación"],
    [
        ["H-L4-01", "La ruta de SQLite depende de la carpeta desde donde se arranca.",
         "Puede crear una base vacía si se ejecuta desde otro lugar.",
         "Usar ruta absoluta o relativa a la raíz."],
        ["H-L4-02", "La clave JWT tiene un valor por defecto.",
         "Con ese valor se podrían falsificar tokens.",
         "Validarla al arrancar y fallar si es la de ejemplo."],
        ["H-L4-03", "El servidor MCP no pide autenticación.",
         "Cualquier proceso local puede usar sus herramientas.",
         "Mantenerlo local o añadir token/allowlist."],
        ["H-L4-04", "El asistente no registra pedidos.",
         "Solo cotiza y consulta stock; el pedido se crea aparte.",
         "Añadir la herramienta registrar_pedido."],
    ],
    anchos=[2.0, 5.4, 4.8, 4.0],
    tamano=8,
)

# ======================================================================
# 6. PREGUNTAS PROBABLES
# ======================================================================
h1("6. Preguntas probables y respuestas cortas")
preguntas = [
    ("¿Es una IA real?", "Sí, opcional. Con clave usa DeepSeek para interpretar y redactar; sin "
     "clave funciona con reglas. Las cifras nunca las inventa el modelo: las calcula el dominio."),
    ("¿Por qué no usa siempre el modelo?", "Por costo, latencia y reproducibilidad. La auditoría "
     "necesita resultados estables; el modo asistente los garantiza."),
    ("¿Qué es MCP?", "Un protocolo para exponer herramientas. Aquí hay tres: listar materiales, "
     "consultar stock y calcular pedido, y se probó también por transporte stdio."),
    ("¿Qué es RAG?", "Recuperar información antes de responder. En este MVP es un adaptador "
     "simulado que busca políticas por palabras clave, no embeddings."),
    ("¿Cómo evitan que invente precios?", "El modelo recibe un bloque de datos ya calculado y se "
     "le prohíbe inventar. Las cifras salen de la base y del dominio."),
    ("¿Qué pasa si DeepSeek falla?", "Se devuelve la respuesta del modo asistente; el chat sigue "
     "funcionando."),
    ("¿Por qué solo 4 hallazgos?", "Porque los otros casos cumplen. Los cuatro abiertos son de "
     "endurecimiento (seguridad, rutas) o de alcance (registrar pedidos)."),
    ("¿Qué mejorarían primero?", "La clave JWT y la ruta de la base, por impacto; luego la "
     "autenticación del MCP y la herramienta de pedidos."),
    ("¿Cómo probaron todo?", "12 scripts con evidencia JSON, 75 pruebas automatizadas y revisión "
     "de imports por capas."),
    ("¿Qué no cubre?", "Frontend, pruebas de carga, RAG con embeddings y registro de pedidos "
     "desde el chat."),
]
for pregunta, respuesta in preguntas:
    p(f"¿{pregunta}", negrita=True, despues=1)
    p(respuesta, tamano=9.5, despues=5)

# ======================================================================
# 7. GUION DE 5 MINUTOS
# ======================================================================
h1("7. Guion sugerido de 5 minutos")
tabla(
    ["Tiempo", "Qué decir"],
    [
        ["0:00–0:40", "Qué es Kohem y qué se auditó: módulo de IA del backend."],
        ["0:40–1:40", "Arquitectura y flujo: RAG → intención → MCP → dominio → respuesta."],
        ["1:40–3:00", "Casos y resultados: 12 casos, 75 pruebas, 0 fallos."],
        ["3:00–4:10", "Demo: Swagger /docs → «¿Qué venden?» y «2 kg de glicerina»."],
        ["4:10–5:00", "Hallazgos y cierre: 4 abiertos, recomendaciones y alcance."],
    ],
    anchos=[2.6, 12.8],
)

# ======================================================================
# 8. QUÉ MOSTRAR
# ======================================================================
h1("8. Qué mostrar en pantalla")
bullet("Swagger en http://127.0.0.1:8000/docs, endpoint POST /api/v1/ai/chat.")
bullet("Pregunta «¿Qué venden?»: el asistente lista los materiales reales.")
bullet("Pregunta «Quiero 2 kg de glicerina»: respuesta con subtotal y total.")
bullet("Salida de pytest: 75 passed.")
bullet("Carpeta docs/laboratorio4/evidencias: JSON de cada caso.")

# ======================================================================
# 9. GLOSARIO
# ======================================================================
h1("9. Glosario mínimo")
bullet("LLM: modelo de lenguaje; aquí DeepSeek, opcional.")
bullet("RAG: recuperación de información para fundamentar la respuesta.")
bullet("MCP: protocolo de herramientas; conecta el asistente con catálogo y cálculo.")
bullet("Onion: arquitectura por capas, con el dominio en el centro.")
bullet("Fallback: respaldo automático cuando el modelo no responde.")

# ======================================================================
# 10. CIERRE
# ======================================================================
h1("10. Frase de cierre")
p("«El backend quedó auditado y funcional: calcula con reglas verificables, responde con datos "
  "reales y puede conversar con DeepSeek sin perder el control de las cifras. Las mejoras "
  "pendientes están identificadas y priorizadas.»", cursiva=True)

nodos = [n for n in doc.element.body.iterchildren() if n.tag != qn("w:sectPr")]
for nodo in reversed(nodos):
    if nodo.tag == qn("w:p") and not "".join(nodo.itertext()).strip():
        doc.element.body.remove(nodo)
    else:
        break
cierre = doc.add_paragraph()
cierre.paragraph_format.space_before = Pt(0)
cierre.paragraph_format.space_after = Pt(0)
cierre.add_run("").font.size = Pt(1)

doc.save(str(SALIDA))
print(f"Guion generado: {SALIDA}")
print(f"Párrafos: {len(doc.paragraphs)} · Tablas: {len(doc.tables)}")
