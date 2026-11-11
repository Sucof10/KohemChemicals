"""P07 — Adaptador MCP: contrato de herramientas y transporte real.

Comprueba el esquema declarado, la delegación al dominio y una sesión MCP
completa por stdio (initialize → list_tools → call_tool).
"""

import asyncio
import os
import sys
import time
from pathlib import Path

RAIZ_MVP = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_MVP))
# La BD SQLite se resuelve contra el directorio de trabajo: cambiar antes de importar la app.
os.chdir(RAIZ_MVP)

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from _common import guardar, imprimir
from app.infrastructure.database import AsyncSessionLocal, init_db
from app.infrastructure.mcp_server import KohemMcpAdapter
from app.infrastructure.repositories import SQLiteRawMaterialRepository


async def _en_proceso() -> dict:
    async with AsyncSessionLocal() as sesion:
        adaptador = KohemMcpAdapter(SQLiteRawMaterialRepository(sesion))
        herramientas = [
            {"nombre": h.name, "descripcion": h.description, "esquema": h.input_schema}
            for h in await adaptador.server.list_tools()
        ]
        stock = await adaptador.ejecutar_herramienta("consultar_stock", {"nombre": "glicerina"})
        calculo = await adaptador.ejecutar_herramienta(
            "calcular_pedido", {"items": [{"material_id": 1, "cantidad": 2}], "aplicar_iva": True}
        )
        try:
            await adaptador.ejecutar_herramienta("raiz_cuadrada", {"valor": 9})
            error = None
        except Exception as exc:  # el protocolo debe rechazar herramientas inexistentes
            error = f"{type(exc).__name__}: {exc}"
    return {
        "herramientas": herramientas,
        "consultar_stock": stock,
        "calcular_pedido": calculo,
        "herramienta_inexistente": error,
    }


async def _por_transporte() -> dict:
    parametros = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.infrastructure.mcp_server"],
        cwd=str(RAIZ_MVP),
    )
    inicio = time.perf_counter()
    async with stdio_client(parametros) as (lectura, escritura):
        async with ClientSession(lectura, escritura) as sesion:
            info = await sesion.initialize()
            herramientas = await sesion.list_tools()
            stock = await sesion.call_tool("consultar_stock", {"nombre": "glicerina"})
            calculo = await sesion.call_tool(
                "calcular_pedido", {"items": [{"material_id": 1, "cantidad": 2}]}
            )
    return {
        "servidor": {"nombre": info.server_info.name, "version": info.server_info.version},
        "herramientas": [h.name for h in herramientas.tools],
        "consultar_stock": stock.structured_content,
        "calcular_pedido": calculo.structured_content,
        "duracion_ms": round((time.perf_counter() - inicio) * 1000, 1),
    }


async def ejecutar() -> dict:
    await init_db()
    en_proceso = await _en_proceso()
    transporte = await _por_transporte()
    evidencia = {
        "en_proceso": en_proceso,
        "transporte_stdio": transporte,
        "criterios": {
            "tres_herramientas": {h["nombre"] for h in en_proceso["herramientas"]}
            == {"listar_materiales", "consultar_stock", "calcular_pedido"},
            "esquema_requerido": set(
                next(h for h in en_proceso["herramientas"] if h["nombre"] == "calcular_pedido")["esquema"][
                    "required"
                ]
            )
            == {"items"},
            "rechaza_herramienta_inexistente": en_proceso["herramienta_inexistente"] is not None,
            "transporte_inicializa": transporte["servidor"]["nombre"] == "Kohem-Chemicals-MCP",
            "transporte_devuelve_datos": transporte["consultar_stock"]["encontrado"] is True,
        },
    }
    evidencia["criterios"]["cumple_todos"] = all(evidencia["criterios"].values())
    return evidencia


if __name__ == "__main__":
    resultado = asyncio.run(ejecutar())
    imprimir("P07 — Adaptador MCP", resultado)
    guardar("f07_mcp.json", resultado)
