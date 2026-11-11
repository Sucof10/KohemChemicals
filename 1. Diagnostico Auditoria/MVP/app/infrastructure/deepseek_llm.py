"""Adaptador de modelo de lenguaje sobre la API de DeepSeek.

DeepSeek expone una API compatible con la de OpenAI (``/chat/completions``).
El adaptador cumple dos funciones:

* ``interpretar``: convertir el mensaje en un JSON de intención y entidades.
* ``redactar``: reescribir la respuesta con tono natural usando únicamente los
  datos que calculó el dominio (nunca inventa precios ni stock).

Si no hay clave configurada, la red falla o la respuesta no es válida, ambos
métodos devuelven ``None`` y el caso de uso continúa con el motor de reglas.
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
- Si hay historial, úsalo para resolver referencias como "ese", "el mismo" o "y de ese".
- No inventes materiales que no aparezcan en el mensaje."""

_SISTEMA_REDACCION = """Eres el asesor comercial de Kohem Chemicals, distribuidora de materias primas
químicas para la industria cosmética y de aseo. Hablas como un vendedor experto: cercano,
claro, breve (máximo 130 palabras) y sin sonar robótico.

Objetivos:
1. Entender qué necesita el cliente y para qué aplicación.
2. Orientarlo con el catálogo y las políticas disponibles.
3. Cotizar cuando haya cantidades.
4. Derivar a un asesor humano si hay formulación, reclamo o tema técnico.

Reglas estrictas:
- Usa SOLO las cifras del bloque "Datos verificados". No inventes precios, stock, plazos,
  descuentos ni condiciones.
- Si el bloque incluye "materiales", puedes nombrar categorías y productos reales del catálogo.
- Si falta un dato, di qué sí tienes y pide solo la información necesaria, una pregunta a la vez.
- No repitas fórmulas de cierre en cada mensaje: varía la despedida o termina con una pregunta útil.
- No menciones bases de datos, MCP, JSON, modelos ni detalles técnicos internos.
- Si preguntan algo fuera del negocio, responde con amabilidad y reorienta hacia lo que Kohem ofrece.
- Si se requiere revisión de un asesor, dilo con naturalidad."""


class DeepSeekLLMAdapter(ILLMProvider):
    nombre = "deepseek"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        temperature: float | None = None,
    ):
        self.api_key = settings.DEEPSEEK_API_KEY if api_key is None else api_key
        self.base_url = (settings.DEEPSEEK_BASE_URL if base_url is None else base_url).rstrip("/")
        self.model = settings.DEEPSEEK_MODEL if model is None else model
        self.timeout = settings.LLM_TIMEOUT_SECONDS if timeout is None else timeout
        self.temperature = settings.LLM_TEMPERATURE if temperature is None else temperature

    @property
    def disponible(self) -> bool:
        return bool(self.api_key)

    async def interpretar(
        self,
        mensaje: str,
        contexto: str,
        materiales: list[str],
        historial: list[dict[str, str]] | None = None,
    ) -> dict[str, Any] | None:
        if not self.disponible:
            return None

        contenido_usuario = mensaje
        if contexto and contexto != "Sin reglas especiales.":
            contenido_usuario += f"\n\nContexto de políticas:\n{contexto}"
        if materiales:
            contenido_usuario += "\n\nMateriales del catálogo: " + ", ".join(materiales)

        mensajes = [{"role": "system", "content": _SISTEMA}]
        mensajes.extend(_historial_valido(historial))
        mensajes.append({"role": "user", "content": contenido_usuario})

        contenido = await self._llamar(mensajes, temperatura=0, max_tokens=400, formato_json=True)
        if contenido is None:
            return None
        try:
            return json.loads(_limpiar_json(contenido))
        except json.JSONDecodeError:
            logger.warning("DeepSeek devolvió un JSON inválido al interpretar.")
            return None

    async def redactar(
        self,
        mensaje: str,
        datos: dict[str, Any] | None,
        contexto: str,
        historial: list[dict[str, str]] | None = None,
    ) -> str | None:
        if not self.disponible:
            return None

        contenido_usuario = f"Consulta del cliente: {mensaje}"
        contenido_usuario += "\n\nDatos verificados:\n" + json.dumps(
            datos or {}, ensure_ascii=False, indent=2
        )
        if contexto and contexto != "Sin reglas especiales.":
            contenido_usuario += "\n\nPolíticas aplicables:\n" + contexto

        mensajes = [{"role": "system", "content": _SISTEMA_REDACCION}]
        mensajes.extend(_historial_valido(historial))
        mensajes.append({"role": "user", "content": contenido_usuario})

        contenido = await self._llamar(mensajes, temperatura=self.temperature, max_tokens=300)
        return contenido.strip() if contenido else None

    async def _llamar(
        self,
        mensajes: list[dict],
        temperatura: float,
        max_tokens: int,
        formato_json: bool = False,
    ) -> str | None:
        carga = {
            "model": self.model,
            "messages": mensajes,
            "temperature": temperatura,
            "max_tokens": max_tokens,
        }
        if formato_json:
            carga["response_format"] = {"type": "json_object"}
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
                return respuesta.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
            logger.warning("DeepSeek no disponible o respuesta inválida: %s", exc)
            return None


def _historial_valido(historial: list[dict[str, str]] | None) -> list[dict[str, str]]:
    if not historial:
        return []
    return [
        {"role": m["role"], "content": str(m["content"])}
        for m in historial
        if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content")
    ]


def _limpiar_json(contenido: str) -> str:
    """Quita vallas de código si el modelo las incluye."""
    contenido = contenido.strip()
    bloque = re.search(r"```(?:json)?\s*(.*?)```", contenido, re.DOTALL)
    return bloque.group(1).strip() if bloque else contenido
