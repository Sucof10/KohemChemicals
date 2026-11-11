"""Puertos de la capa de aplicación.

Contratos que la infraestructura debe implementar (RAG y ejecución de
herramientas MCP). La aplicación depende de estas abstracciones, nunca de
FastAPI, SQLAlchemy ni del SDK de MCP.
"""

from typing import Any, Protocol


class IRagRepository(Protocol):
    def buscar_contexto(self, prompt: str) -> str: ...


class IMcpToolExecutor(Protocol):
    async def ejecutar_herramienta(self, nombre: str, argumentos: dict[str, Any]) -> dict[str, Any]: ...


class ILLMProvider(Protocol):
    nombre: str

    async def interpretar(
        self, mensaje: str, contexto: str, materiales: list[str]
    ) -> dict[str, Any] | None: ...
