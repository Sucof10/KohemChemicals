import pytest

from app.application.ai_use_cases import AIAssistantUseCase
from app.domain.entities import RawMaterial
from app.infrastructure.mcp_server import KohemMcpAdapter
from app.infrastructure.mock_vector_db import MockVectorDbAdapter

pytestmark = pytest.mark.asyncio


class CatalogoFalso:
    def __init__(self):
        self.materiales = [
            RawMaterial(1, "Glicerina vegetal", "Humectantes", "kg", 18000, 100, "", True),
            RawMaterial(2, "Aceite esencial de menta", "Aceites esenciales", "kg", 85000, 8, "", True),
            RawMaterial(3, "Ácido cítrico", "Reguladores de pH", "kg", 12000, 75, "", True),
            RawMaterial(4, "Alcohol cetílico", "Emolientes", "kg", 60000, 2000, "", True),
        ]

    async def get_all(self, skip=0, limit=100):
        return self.materiales

    async def get_by_id(self, material_id):
        return next((m for m in self.materiales if m.id == material_id), None)


@pytest.fixture
def caso_de_uso():
    return AIAssistantUseCase(
        rag_repo=MockVectorDbAdapter(),
        mcp_executor=KohemMcpAdapter(CatalogoFalso()),
    )


async def test_cotizacion_sin_reglas_rag(caso_de_uso):
    respuesta, transferir, motivo = await caso_de_uso.respond("Cotiza 2 kg de glicerina")
    assert "36.000,00" in respuesta
    assert "IVA" not in respuesta
    assert transferir is False
    assert motivo is None


async def test_cotizacion_con_iva_recuperado_por_rag(caso_de_uso):
    respuesta, transferir, _ = await caso_de_uso.respond("Cotiza 2 kg de glicerina con IVA")
    assert "6.840,00" in respuesta
    assert "42.840,00" in respuesta
    assert transferir is False


async def test_cotizacion_con_tope_requiere_aprobacion(caso_de_uso):
    respuesta, transferir, motivo = await caso_de_uso.respond("Cotiza 1000 kg de alcohol cetílico con tope máximo")
    assert "50.000.000,00" in respuesta
    assert transferir is True
    assert "aprobación gerencial" in motivo.lower()


async def test_material_bajo_stock_minimo_requiere_asesor(caso_de_uso):
    respuesta, transferir, motivo = await caso_de_uso.respond("Cotiza 1 kg de aceite esencial de menta")
    assert transferir is True
    assert "stock mínimo" in motivo


async def test_material_desconocido(caso_de_uso):
    respuesta, transferir, motivo = await caso_de_uso.respond("Cotiza 5 kg de mercurio")
    assert "No encontré en el catálogo" in respuesta
    assert transferir is True


async def test_consulta_de_stock(caso_de_uso):
    respuesta, transferir, _ = await caso_de_uso.respond("¿Cuál es el stock de glicerina?")
    assert "100 kg" in respuesta
    assert transferir is False


async def test_consulta_de_stock_bajo_minimo(caso_de_uso):
    respuesta, transferir, _ = await caso_de_uso.respond("Necesito la disponibilidad de aceite esencial de menta")
    assert transferir is True


async def test_consulta_sin_reglas_especiales(caso_de_uso):
    respuesta, transferir, _ = await caso_de_uso.respond("Hola, buenos días")
    assert "disponibilidad, pedidos" in respuesta
    assert transferir is False


async def test_consulta_tecnica_se_transfiere(caso_de_uso):
    _, transferir, motivo = await caso_de_uso.respond("Tengo un problema de formulación")
    assert transferir is True
    assert "conocimiento técnico" in motivo


async def test_mensaje_vacio(caso_de_uso):
    with pytest.raises(ValueError):
        await caso_de_uso.respond("   ")
