"""Caso de uso del asistente conversacional.

Orquesta el flujo completo: recuperación RAG de políticas, interpretación de la
consulta (modelo de lenguaje con respaldo en reglas), ejecución de herramientas
MCP y redacción de la respuesta.
"""

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

from app.application.ports import ILLMProvider, IMcpToolExecutor, IRagRepository
from app.domain.services import PricingDomainService

_UNIDADES = {
    "cero": 0, "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4,
    "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
    "dieciseis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19, "veinte": 20,
}
_DECENAS = {
    "treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60,
    "setenta": 70, "ochenta": 80, "noventa": 90, "cien": 100, "ciento": 100,
}
_VEINTI = {
    "veintiuno": 21, "veintidos": 22, "veintitres": 23, "veinticuatro": 24,
    "veinticinco": 25, "veintiseis": 26, "veintisiete": 27, "veintiocho": 28,
    "veintinueve": 29,
}

_UNIDAD_CANONICA = {
    "kg": "kg", "kilo": "kg", "kilos": "kg", "kilogramo": "kg", "kilogramos": "kg",
    "g": "g", "gramo": "g", "gramos": "g",
    "l": "l", "litro": "l", "litros": "l",
    "ml": "ml", "mililitro": "ml", "mililitros": "ml",
    "u": "unidad", "unidad": "unidad", "unidades": "unidad",
    "bulto": "bulto", "bultos": "bulto", "bolsa": "bolsa", "bolsas": "bolsa",
}

_CANTIDAD_RE = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*"
    r"(kg|kilos?|kilogramos?|g|gramos?|l|litros?|ml|mililitros?|unidades?|u|bultos?|bolsas?)"
    r"\s+de\s+([a-záéíóúñü ]+)",
    re.IGNORECASE,
)

_RAICES_TECNICAS = ("formul", "tecnic", "problema", "urgent", "reclamo", "asesor")
_TERMINOS_STOCK = ("stock", "inventario", "disponibilidad", "existencia")
_TERMINOS_PEDIDO = ("pedido", "comprar", "cotiza", "cotización", "cotizacion")

_MENSAJE_TECNICO = (
    "Puedo registrar tu consulta, pero este caso requiere revisión de un asesor de Kohem Chemicals."
)
_MOTIVO_TECNICO = "La consulta puede requerir conocimiento técnico o intervención humana."


def _normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in sin_tildes if not unicodedata.combining(c))


def _moneda(valor: float) -> str:
    return f"${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _normalizar_numeros(texto: str) -> str:
    """Convierte «dos», «treinta y cinco» o «veinticinco» en dígitos."""

    def decena(match: re.Match) -> str:
        return str(_DECENAS[match.group(1)] + _UNIDADES[match.group(2)])

    def veinti(match: re.Match) -> str:
        return str(_VEINTI[match.group(0)])

    texto = re.sub(
        r"\b(treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa)\s+y\s+"
        r"(un|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve)\b",
        decena,
        texto,
        flags=re.IGNORECASE,
    )
    texto = re.sub(r"\bveinti(?:uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve)\b",
                   veinti, texto, flags=re.IGNORECASE)
    texto = re.sub(
        r"\b(" + "|".join(sorted(_UNIDADES, key=len, reverse=True)) + r")\b",
        lambda m: str(_UNIDADES[m.group(1).lower()]),
        texto,
        flags=re.IGNORECASE,
    )
    texto = re.sub(
        r"\b(" + "|".join(_DECENAS) + r")\b",
        lambda m: str(_DECENAS[m.group(1).lower()]),
        texto,
        flags=re.IGNORECASE,
    )
    texto = re.sub(r"\b(\d+)\s+y\s+medio\b", lambda m: f"{m.group(1)}.5", texto, flags=re.IGNORECASE)
    return texto


def _limpiar_nombre(nombre: str) -> str:
    nombre = re.split(r"\b(?:con|para|y|e)\b", nombre.strip(), flags=re.IGNORECASE)[0]
    return nombre.strip(" ,.;:")


def _extraer_items(mensaje: str) -> list[dict[str, Any]]:
    items = []
    texto = _normalizar_numeros(_normalizar(mensaje))
    for cantidad, unidad, nombre in _CANTIDAD_RE.findall(texto):
        limpio = _limpiar_nombre(nombre)
        if not limpio:
            continue
        items.append(
            {
                "cantidad": float(cantidad.replace(",", ".")),
                "unidad": _UNIDAD_CANONICA.get(unidad.lower(), unidad.lower()),
                "nombre": limpio,
            }
        )
    return items


def _hay_termino_tecnico(mensaje: str) -> bool:
    tokens = re.findall(r"[a-záéíóúñü]+", _normalizar(mensaje))
    for indice, token in enumerate(tokens):
        if any(token.startswith(raiz) for raiz in _RAICES_TECNICAS):
            ventana = tokens[max(0, indice - 3):indice]
            if not any(negacion in ventana for negacion in ("no", "sin", "ningun", "ninguna")):
                return True
    return False


def _resolver_material(nombre: str, catalogo: list[dict[str, Any]]) -> dict[str, Any] | None:
    buscado = _normalizar(nombre)
    for material in catalogo:
        actual = _normalizar(material["nombre"])
        if buscado == actual or buscado in actual or actual in buscado:
            return material
    mejor = max(
        catalogo,
        key=lambda m: SequenceMatcher(None, buscado, _normalizar(m["nombre"])).ratio(),
        default=None,
    )
    if mejor and SequenceMatcher(None, buscado, _normalizar(mejor["nombre"])).ratio() >= 0.72:
        return mejor
    return None


def _material_mencionado(consulta: str, catalogo: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Elige el material cuyo nombre comparte más palabras significativas con la consulta."""
    normalizado = _normalizar(consulta)
    mejor, mejor_puntaje = None, 0
    for material in catalogo:
        palabras = [p for p in _normalizar(material["nombre"]).split() if len(p) >= 4 and p not in ("esencial",)]
        puntaje = sum(1 for palabra in palabras if palabra in normalizado)
        if puntaje > mejor_puntaje:
            mejor, mejor_puntaje = material, puntaje
    return mejor


class AIAssistantUseCase:
    """Asistente con RAG de políticas, herramientas MCP y modelo de lenguaje opcional."""

    def __init__(
        self,
        rag_repo: IRagRepository,
        mcp_executor: IMcpToolExecutor,
        pricing: PricingDomainService | None = None,
        llm: ILLMProvider | None = None,
        modo: str = "asistente",
        max_historial: int = 8,
    ):
        self.rag_repo = rag_repo
        self.mcp_executor = mcp_executor
        self.pricing = pricing or PricingDomainService()
        self.llm = llm
        self.modo = modo if modo in ("asistente", "conversacional") else "asistente"
        self.max_historial = max(max_historial, 0)
        self.ultimo_motor = "reglas"
        self.ultimos_datos: dict[str, Any] | None = None

    async def respond(
        self, message: str, historial: list[dict[str, str]] | None = None
    ) -> tuple[str, bool, str | None]:
        consulta = message.strip()
        if not consulta:
            raise ValueError("El mensaje no puede estar vacío.")

        self.ultimos_datos = None
        self.ultimo_motor = "reglas"
        contexto = self.rag_repo.buscar_contexto(consulta)
        historial = (historial or [])[-self.max_historial:]

        respuesta = await self._responder(consulta, contexto, historial)
        if self.modo == "conversacional" and self.llm is not None:
            redactado = await self.llm.redactar(consulta, self.ultimos_datos, contexto, historial)
            if redactado:
                self.ultimo_motor = f"{getattr(self.llm, 'nombre', 'llm')}-conversacional"
                return (redactado, respuesta[1], respuesta[2])
        return respuesta

    async def _responder(
        self, consulta: str, contexto: str, historial: list[dict[str, str]]
    ) -> tuple[str, bool, str | None]:
        interpretacion = await self._interpretar(consulta, contexto, historial)
        if interpretacion is not None:
            respuesta = await self._aplicar_interpretacion(interpretacion, contexto)
            if respuesta is not None:
                return respuesta

        self.ultimo_motor = "reglas"
        items = _extraer_items(consulta)
        tecnico = _hay_termino_tecnico(consulta)

        if items:
            return await self._cotizar(items, contexto, revisar_tecnico=tecnico)
        if tecnico:
            return (_MENSAJE_TECNICO, True, _MOTIVO_TECNICO)

        normalizado = _normalizar(consulta)
        if any(termino in normalizado for termino in _TERMINOS_STOCK):
            return await self._consultar_stock(consulta)

        if any(termino in normalizado for termino in _TERMINOS_PEDIDO):
            return (
                "Puedes crear un pedido seleccionando las materias primas disponibles y las cantidades requeridas.",
                False,
                None,
            )

        return (
            "Puedo ayudarte con disponibilidad, pedidos y orientación inicial sobre el proceso de compra.",
            False,
            None,
        )

    # ------------------------------------------------------------------
    # Interpretación con modelo de lenguaje (respaldo: reglas)
    # ------------------------------------------------------------------
    async def _interpretar(
        self, consulta: str, contexto: str, historial: list[dict[str, str]]
    ) -> dict[str, Any] | None:
        if self.llm is None:
            return None
        datos = await self.llm.interpretar(consulta, contexto, [], historial)
        if not isinstance(datos, dict):
            return None
        intencion = datos.get("intencion")
        if intencion not in {"cotizar", "stock", "asesoria", "otro"}:
            return None
        if intencion == "cotizar":
            items = datos.get("items")
            if not isinstance(items, list) or not items:
                return None
            limpios = []
            for item in items:
                if not isinstance(item, dict):
                    return None
                try:
                    cantidad = float(item.get("cantidad", 0))
                except (TypeError, ValueError):
                    return None
                nombre = str(item.get("material", "")).strip()
                if cantidad <= 0 or not nombre:
                    return None
                limpios.append(
                    {
                        "cantidad": cantidad,
                        "unidad": _UNIDAD_CANONICA.get(str(item.get("unidad", "kg")).lower(), "kg"),
                        "nombre": nombre,
                    }
                )
            datos["items"] = limpios
        self.ultimo_motor = getattr(self.llm, "nombre", "llm")
        return datos

    async def _aplicar_interpretacion(
        self, interpretacion: dict[str, Any], contexto: str
    ) -> tuple[str, bool, str | None] | None:
        intencion = interpretacion["intencion"]
        if intencion == "asesoria":
            return (_MENSAJE_TECNICO, True, _MOTIVO_TECNICO)
        if intencion == "cotizar":
            return await self._cotizar(
                interpretacion["items"],
                contexto,
                revisar_tecnico=bool(interpretacion.get("requiere_asesor")),
            )
        if intencion == "stock":
            material = str(interpretacion.get("material_consulta", "")).strip()
            if material:
                return await self._consultar_stock(material)
        return None

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    async def _cotizar(
        self,
        items: list[dict[str, Any]],
        contexto: str,
        revisar_tecnico: bool = False,
    ) -> tuple[str, bool, str | None]:
        catalogo = (await self.mcp_executor.ejecutar_herramienta("listar_materiales", {}))["materiales"]
        resueltos = []
        desconocidos = []
        for item in items:
            material = _resolver_material(item["nombre"], catalogo)
            if material is None:
                desconocidos.append(item["nombre"])
            else:
                resueltos.append({"material_id": material["id"], "cantidad": item["cantidad"]})

        if not resueltos:
            return (
                f"No encontré en el catálogo: {', '.join(desconocidos)}.",
                True,
                "Material no identificado en el catálogo de Kohem Chemicals.",
            )

        cotizacion = await self.mcp_executor.ejecutar_herramienta(
            "calcular_pedido",
            {
                "items": resueltos,
                "aplicar_iva": "iva del 19%" in _normalizar(contexto),
                "aplicar_tope": "50.000.000" in contexto,
            },
        )
        self.ultimos_datos = {
            "tipo": "cotizacion",
            "items": cotizacion["items"],
            "subtotal": cotizacion["subtotal"],
            "iva": cotizacion["iva"],
            "total": cotizacion["total"],
            "tope_aplicado": cotizacion["tope_aplicado"],
            "requiere_revision": cotizacion["requiere_revision"],
        }

        lineas = ["Cotización de pedido:"]
        for item in cotizacion["items"]:
            lineas.append(
                f"- {item['cantidad']:g} {item['unidad']} de {item['nombre']}: {_moneda(item['subtotal'])}"
            )
        lineas.append(f"Subtotal: {_moneda(cotizacion['subtotal'])}")
        if cotizacion["iva"]:
            lineas.append(f"IVA 19%: {_moneda(cotizacion['iva'])}")
        lineas.append(f"Total: {_moneda(cotizacion['total'])}")
        if cotizacion["tope_aplicado"]:
            lineas.append("Se aplicó el tope comercial de 50.000.000 COP; requiere aprobación gerencial.")
        if desconocidos:
            lineas.append(f"No identificados: {', '.join(desconocidos)}.")
        if revisar_tecnico:
            lineas.append("La consulta incluye terminología técnica: se sugiere revisión de un asesor.")

        transferir = (
            cotizacion["tope_aplicado"]
            or cotizacion["requiere_revision"]
            or bool(desconocidos)
            or revisar_tecnico
        )
        motivo = None
        if cotizacion["tope_aplicado"]:
            motivo = "El pedido supera el tope comercial y requiere aprobación gerencial."
        elif cotizacion["requiere_revision"]:
            motivo = "Alguna materia prima está por debajo del stock mínimo y requiere revisión de un asesor."
        elif desconocidos:
            motivo = "No se identificaron todos los materiales solicitados."
        elif revisar_tecnico:
            motivo = "La consulta incluye terminología técnica y requiere revisión de un asesor."

        return ("\n".join(lineas), transferir, motivo)

    async def _consultar_stock(self, consulta: str) -> tuple[str, bool, str | None]:
        catalogo = (await self.mcp_executor.ejecutar_herramienta("listar_materiales", {}))["materiales"]
        material = _material_mencionado(consulta, catalogo)
        if material is None:
            return (
                "Puedes consultar la disponibilidad de materias primas mediante el catálogo del sistema.",
                False,
                None,
            )

        stock = await self.mcp_executor.ejecutar_herramienta("consultar_stock", {"nombre": material["nombre"]})
        self.ultimos_datos = {"tipo": "stock", **stock}
        respuesta = (
            f"{stock['material']}: {stock['stock']:g} {stock['unidad']} disponibles "
            f"(mínimo operativo {stock['stock_minimo']:g} {stock['unidad']})."
        )
        if stock["requiere_revision"]:
            respuesta += " El stock está por debajo del mínimo: la venta requiere revisión de un asesor."
        return (
            respuesta,
            stock["requiere_revision"],
            "Stock por debajo del mínimo operativo." if stock["requiere_revision"] else None,
        )
