import pytest

from app.domain.entities import RawMaterial
from app.infrastructure.mcp_server import KohemMcpAdapter

pytestmark = pytest.mark.asyncio


class CatalogoFalso:
    """Repositorio en memoria: permite auditar el adaptador sin base de datos."""

    def __init__(self):
        self.materiales = [
            RawMaterial(1, "Glicerina vegetal", "Humectantes", "kg", 18000, 100, "", True),
            RawMaterial(2, "Aceite esencial de menta", "Aceites esenciales", "kg", 85000, 8, "", True),
            RawMaterial(3, "Ácido cítrico", "Reguladores de pH", "kg", 12000, 75, "", True),
            RawMaterial(4, "Insumo inactivo", "Otros", "kg", 5000, 500, "", False),
        ]

    async def get_all(self, skip=0, limit=100):
        return self.materiales

    async def get_by_id(self, material_id):
        return next((m for m in self.materiales if m.id == material_id), None)


@pytest.fixture
def adaptador():
    return KohemMcpAdapter(CatalogoFalso())


async def test_contrato_de_herramientas(adaptador):
    herramientas = await adaptador.server.list_tools()
    nombres = {h.name for h in herramientas}
    assert nombres == {"listar_materiales", "consultar_stock", "calcular_pedido"}

    calcular = next(h for h in herramientas if h.name == "calcular_pedido")
    assert set(calcular.input_schema["properties"]) == {"items", "aplicar_iva", "aplicar_tope"}
    assert "items" in calcular.input_schema["required"]


async def test_listar_materiales_omite_inactivos(adaptador):
    resultado = await adaptador.ejecutar_herramienta("listar_materiales", {})
    ids = {m["id"] for m in resultado["materiales"]}
    assert ids == {1, 2, 3}


async def test_consultar_stock_encontrado(adaptador):
    resultado = await adaptador.ejecutar_herramienta("consultar_stock", {"nombre": "glicerina"})
    assert resultado["encontrado"] is True
    assert resultado["stock"] == 100
    assert resultado["requiere_revision"] is False


async def test_consultar_stock_bajo_minimo(adaptador):
    resultado = await adaptador.ejecutar_herramienta("consultar_stock", {"nombre": "aceite esencial de menta"})
    assert resultado["requiere_revision"] is True


async def test_consultar_stock_inexistente(adaptador):
    resultado = await adaptador.ejecutar_herramienta("consultar_stock", {"nombre": "mercurio"})
    assert resultado["encontrado"] is False


async def test_calcular_pedido_sin_reglas(adaptador):
    resultado = await adaptador.ejecutar_herramienta(
        "calcular_pedido", {"items": [{"material_id": 1, "cantidad": 2}]}
    )
    assert resultado["subtotal"] == 36000.0
    assert resultado["iva"] == 0.0
    assert resultado["total"] == 36000.0
    assert resultado["tope_aplicado"] is False


async def test_calcular_pedido_con_iva(adaptador):
    resultado = await adaptador.ejecutar_herramienta(
        "calcular_pedido", {"items": [{"material_id": 1, "cantidad": 2}], "aplicar_iva": True}
    )
    assert resultado["iva"] == 6840.0
    assert resultado["total"] == 42840.0


async def test_calcular_pedido_con_tope(adaptador):
    adaptador.material_repo.materiales[0].stock = 5000
    resultado = await adaptador.ejecutar_herramienta(
        "calcular_pedido",
        {"items": [{"material_id": 1, "cantidad": 3000}], "aplicar_tope": True},
    )
    assert resultado["subtotal"] == 54000000.0
    assert resultado["total"] == 50000000.0
    assert resultado["tope_aplicado"] is True


async def test_calcular_pedido_stock_insuficiente(adaptador):
    with pytest.raises(Exception):
        await adaptador.ejecutar_herramienta(
            "calcular_pedido", {"items": [{"material_id": 1, "cantidad": 101}]}
        )


async def test_herramienta_desconocida(adaptador):
    with pytest.raises(Exception):
        await adaptador.ejecutar_herramienta("raiz_cuadrada", {"valor": 9})


async def test_pedido_vacio(adaptador):
    with pytest.raises(Exception):
        await adaptador.ejecutar_herramienta("calcular_pedido", {"items": []})
