"""Adaptador de modelo de lenguaje sobre la API de DeepSeek.

DeepSeek expone una API compatible con la de OpenAI (``/chat/completions``).
El adaptador solo interpreta la consulta y devuelve un JSON estructurado; la
ejecución de acciones sigue pasando por el servidor MCP y el dominio.

Si no hay clave configurada, la red falla o la respuesta no es JSON válido, el
método devuelve ``None`` y el caso de uso continúa con el motor de reglas.
"""

import json
import logging
import re
from typing import Any

import httpx

from app.application.ports import ILLMProvider
from app.infrastructure.config import settings

logger = logging.getLogger(__name__)

_SISTEMA = """Eres el intérprete de consultas de Kohem Chemicals, distribuidora de materias primas.
Devuelve EXCLUSIVAMENTE un objeto JSON, sin texto adicional, con esta forma:
{"intencion": "cotizar" | "stock" | "asesoria" | "otro",
 "items": [{"material": "nombre", "cantidad": 2, "unidad": "kg"}],
 "material_consulta": "nombre o vacío",
 "requiere_asesor": false}

Reglas:
- "cotizar" cuando el usuario pide precio o cantidad de uno o varios materiales.
- "stock" cuando pregunta disponibilidad o existencias.
- "asesoria" cuando hay una duda técnica, una formulación, un reclamo o pide un asesor.
- "otro" para saludos o consultas generales.
- Usa cantidades numéricas aunque el usuario las escriba con palabras.
- Unidades admitidas: kg, g, l, ml, unidad, bulto, bolsa.
- No inventes materiales que no aparezcan en el mensaje."""


class DeepSeekLLMAdapter(ILLMProvider):
    nombre = "deepseek"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ):
        self.api_key = settings.DEEPSEEK_API_KEY if api_key is None else api_key
        self.base_url = (settings.DEEPSEEK_BASE_URL if base_url is None else base_url).rstrip("/")
        self.model = settings.DEEPSEEK_MODEL if model is None else model
        self.timeout = settings.LLM_TIMEOUT_SECONDS if timeout is None else timeout

    @property
    def disponible(self) -> bool:
        return bool(self.api_key)

    async def interpretar(
        self, mensaje: str, contexto: str, materiales: list[str]
    ) -> dict[str, Any] | None:
        if not self.disponible:
            return None

        contenido_usuario = mensaje
        if contexto and contexto != "Sin reglas especiales.":
            contenido_usuario += f"\n\nContexto de políticas:\n{contexto}"
        if materiales:
            contenido_usuario += "\n\nMateriales del catálogo: " + ", ".join(materiales)

        carga = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _SISTEMA},
                {"role": "user", "content": contenido_usuario},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0,
            "max_tokens": 400,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as cliente:
                respuesta = await cliente.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=carga,
                )
                respuesta.raise_for_status()
                contenido = respuesta.json()["choices"][0]["message"]["content"]
            return json.loads(_limpiar_json(contenido))
        except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            logger.warning("DeepSeek no disponible o respuesta inválida: %s", exc)
            return None


def _limpiar_json(contenido: str) -> str:
    """Quita vallas de código si el modelo las incluye."""
    contenido = contenido.strip()
    bloque = re.search(r"```(?:json)?\s*(.*?)```", contenido, re.DOTALL)
    return bloque.group(1).strip() if bloque else contenido
