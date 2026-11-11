"""Servidor MCP de Kohem Chemicals.

Expone herramientas del dominio (catálogo, stock y cotización) mediante el
protocolo MCP real. El adaptador puede ejercitarse de dos formas:

* En proceso, con ``ejecutar_herramienta`` (misma ruta ``list_tools`` /
  ``call_tool`` del servidor, sin transporte).
* Por transporte stdio, ejecutando este módulo::

      python -m app.infrastructure.mcp_server
"""

import asyncio
import json
import unicodedata
from typing import Any

from mcp.server import MCPServer

from app.domain.interfaces import IRawMaterialRepository
from app.domain.services import PricingDomainService


def _normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in sin_tildes if not unicodedata.combining(c))


class KohemMcpAdapter:
    """Implementa ``IMcpToolExecutor`` sobre un servidor MCP real."""

    def __init__(self, material_repo: IRawMaterialRepository, pricing: PricingDomainService | None = None):
        self.material_repo = material_repo
        self.pricing = pricing or PricingDomainService()
        self.server = MCPServer(
            name="Kohem-Chemicals-MCP",
            version="1.0.0",
            instructions="Herramientas de catálogo, inventario y cotización de Kohem Chemicals.",
        )
        self._registrar_herramientas()

    # ------------------------------------------------------------------
    # Herramientas expuestas por el protocolo
    # ------------------------------------------------------------------
    def _registrar_herramientas(self) -> None:
        @self.server.tool(
            name="listar_materiales",
            description="Devuelve el catálogo de materias primas activas con precio y stock.",
        )
        async def listar_materiales() -> dict[str, Any]:
            materiales = await self.material_repo.get_all(0, 100)
            return {
                "materiales": [
                    {
                        "id": m.id,
                        "nombre": m.name,
                        "categoria": m.category,
                        "unidad": m.unit,
                        "precio": m.price,
                        "stock": m.stock,
                    }
                    for m in materiales
                    if m.is_active
                ]
            }

        @self.server.tool(
            name="consultar_stock",
            description="Consulta el stock disponible de una materia prima por nombre.",
        )
        async def consultar_stock(nombre: str) -> dict[str, Any]:
            materiales = await self.material_repo.get_all(0, 100)
            buscado = _normalizar(nombre)
            material = next(
                (m for m in materiales if buscado in _normalizar(m.name) or _normalizar(m.name) in buscado),
                None,
            )
            if material is None:
                return {"encontrado": False, "nombre_consultado": nombre}
            return {
                "encontrado": True,
                "material": material.name,
                "stock": material.stock,
                "unidad": material.unit,
                "stock_minimo": self.pricing.STOCK_MINIMO,
                "requiere_revision": self.pricing.requiere_revision(material.stock),
            }

        @self.server.tool(
            name="calcular_pedido",
            description=(
                "Cotiza un pedido a partir de material_id y cantidad. Aplica IVA y tope "
                "solo cuando la regla correspondiente fue recuperada por el RAG."
            ),
        )
        async def calcular_pedido(
            items: list[dict[str, Any]],
            aplicar_iva: bool = False,
            aplicar_tope: bool = False,
        ) -> dict[str, Any]:
            if not items:
                raise ValueError("El pedido debe incluir al menos un ítem.")

            cotizados = []
            for item in items:
                material = await self.material_repo.get_by_id(int(item["material_id"]))
                if material is None or not material.is_active:
                    raise ValueError(f"Materia prima {item['material_id']} no encontrada o inactiva.")
                cantidad = float(item["cantidad"])
                if cantidad > material.stock:
                    raise ValueError(
                        f"Stock insuficiente de {material.name}: disponible {material.stock}, solicitado {cantidad}."
                    )
                cotizados.append(
                    {
                        "material_id": material.id,
                        "nombre": material.name,
                        "cantidad": cantidad,
                        "unidad": material.unit,
                        "precio_unitario": material.price,
                        "subtotal": self.pricing.subtotal(material.price, cantidad),
                        "requiere_revision": self.pricing.requiere_revision(material.stock),
                    }
                )

            subtotal = self.pricing.total([c["subtotal"] for c in cotizados])
            iva = self.pricing.impuesto(subtotal) if aplicar_iva else 0.0
            total = round(subtotal + iva, 2)
            tope_aplicado = False
            if aplicar_tope and total > self.pricing.TOPE_PEDIDO:
                total = self.pricing.aplicar_tope(total)
                tope_aplicado = True

            return {
                "items": cotizados,
                "subtotal": subtotal,
                "iva": iva,
                "total": total,
                "tope_aplicado": tope_aplicado,
                "requiere_revision": any(c["requiere_revision"] for c in cotizados),
            }

    # ------------------------------------------------------------------
    # Contrato consumido por la capa de aplicación
    # ------------------------------------------------------------------
    async def ejecutar_herramienta(self, nombre: str, argumentos: dict[str, Any]) -> dict[str, Any]:
        try:
            resultado = await self.server.call_tool(nombre, argumentos)
        except ValueError:
            raise
        except Exception as exc:  # ToolError / UnexpectedToolError del SDK
            raise ValueError(str(exc)) from exc
        if resultado.structured_content:
            return resultado.structured_content
        texto = "".join(
            getattr(bloque, "text", "") for bloque in resultado.content if getattr(bloque, "type", "") == "text"
        )
        return json.loads(texto)


async def _servidor_autonomo() -> None:
    from app.infrastructure.database import AsyncSessionLocal, init_db
    from app.infrastructure.repositories import SQLiteRawMaterialRepository

    await init_db()
    async with AsyncSessionLocal() as session:
        adaptador = KohemMcpAdapter(SQLiteRawMaterialRepository(session))
        await adaptador.server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(_servidor_autonomo())
