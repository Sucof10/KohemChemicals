"""Adaptador RAG simulado (base vectorial en memoria).

La recuperación es por palabras clave completas, no semántica: suficiente para
el MVP y explícito en la auditoría del Laboratorio 4.
"""

import re
import unicodedata

from app.application.ports import IRagRepository


def _normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in sin_tildes if not unicodedata.combining(c))


class MockVectorDbAdapter(IRagRepository):
    """Base de conocimiento de políticas comerciales de Kohem Chemicals."""

    def __init__(self):
        self._db = {
            "stock": (
                "Política de inventario: cada materia prima exige un stock mínimo de 10 kg. "
                "Si el stock disponible es inferior, la solicitud requiere revisión de un asesor."
            ),
            "iva": (
                "Política tributaria: a todo pedido se le aplica un IVA del 19% sobre el subtotal."
            ),
            "tope": (
                "Política comercial: ningún pedido puede superar 50.000.000 COP; "
                "el excedente requiere aprobación gerencial."
            ),
        }
        # Coincidencia por palabra completa: evita que «al máximo» active el tope.
        self._patrones = {
            "stock": re.compile(r"\b(stock|inventario|disponibilidad|existencias?)\b"),
            "iva": re.compile(r"\b(iva|impuestos?|tributari[oa]s?)\b"),
            "tope": re.compile(r"\b(topes?|limites?)\b|\bno (superar|exceder)\b"),
        }

    def buscar_contexto(self, prompt: str) -> str:
        texto = _normalizar(prompt)
        reglas = [self._db[clave] for clave, patron in self._patrones.items() if patron.search(texto)]
        return "\n".join(reglas) if reglas else "Sin reglas especiales."
