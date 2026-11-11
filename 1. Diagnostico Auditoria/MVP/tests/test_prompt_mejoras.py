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
            RawMaterial(2, "Ácido cítrico", "Reguladores de pH", "kg", 12000, 75, "", True),
        ]

    async def get_all(self, skip=0, limit=100):
        return self.materiales

    async def get_by_id(self, material_id):
        return next((m for m in self.materiales if m.id == material_id), None)


@pytest.fixture
def caso():
    return AIAssistantUseCase(
        rag_repo=MockVectorDbAdapter(),
        mcp_executor=KohemMcpAdapter(CatalogoFalso()),
    )


async def test_numero_escrito_con_palabras(caso):
    respuesta, _, _ = await caso.respond("Cotiza dos kg de glicerina")
    assert "36.000,00" in respuesta


async def test_unidad_kilos(caso):
    respuesta, _, _ = await caso.respond("Cotiza 2 kilos de glicerina")
    assert "36.000,00" in respuesta


async def test_numero_compuesto(caso):
    respuesta, _, _ = await caso.respond("Cotiza veinticinco kg de glicerina")
    assert "450.000,00" in respuesta


async def test_negacion_no_transfiere(caso):
    _, transferir, _ = await caso.respond("No tengo problemas con mi pedido")
    assert transferir is False


async def test_termino_tecnico_no_anula_la_cotizacion(caso):
    respuesta, transferir, motivo = await caso.respond("Quiero 5 kg de glicerina para mi formulación")
    assert "90.000,00" in respuesta
    assert transferir is True
    assert "técnica" in motivo


async def test_sin_espacio_entre_numero_y_unidad(caso):
    respuesta, _, _ = await caso.respond("Cotiza 2kg de glicerina")
    assert "36.000,00" in respuesta


async def test_no_activa_tope_con_al_maximo(caso):
    respuesta, _, _ = await caso.respond("Cotiza 5 kg de glicerina al máximo")
    assert "tope comercial" not in respuesta
