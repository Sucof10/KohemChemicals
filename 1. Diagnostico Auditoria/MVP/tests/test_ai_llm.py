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


class LLMFalso:
    nombre = "falso"

    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.llamadas = []

    async def interpretar(self, mensaje, contexto, materiales, historial=None):
        self.llamadas.append({"mensaje": mensaje, "contexto": contexto, "historial": historial})
        return self.respuesta

    async def redactar(self, mensaje, datos, contexto, historial=None):
        return None


def construir(llm=None):
    return AIAssistantUseCase(
        rag_repo=MockVectorDbAdapter(),
        mcp_executor=KohemMcpAdapter(CatalogoFalso()),
        llm=llm,
    )


async def test_llm_interpreta_cotizacion_con_palabras():
    llm = LLMFalso(
        {
            "intencion": "cotizar",
            "items": [{"material": "glicerina", "cantidad": 2, "unidad": "kg"}],
        }
    )
    caso = construir(llm)
    respuesta, transferir, _ = await caso.respond("Quiero dos kilos de glicerina")
    assert "36.000,00" in respuesta
    assert transferir is False
    assert caso.ultimo_motor == "falso"
    assert llm.llamadas and "glicerina" in llm.llamadas[0]["mensaje"]


async def test_llm_interpreta_consulta_de_stock():
    caso = construir(LLMFalso({"intencion": "stock", "material_consulta": "glicerina"}))
    respuesta, transferir, _ = await caso.respond("¿Tienen glicerina?")
    assert "100 kg" in respuesta
    assert transferir is False
    assert caso.ultimo_motor == "falso"


async def test_llm_deriva_a_asesor():
    caso = construir(LLMFalso({"intencion": "asesoria"}))
    _, transferir, motivo = await caso.respond("Necesito ayuda con una formulación")
    assert transferir is True
    assert "conocimiento técnico" in motivo


async def test_sin_llm_usa_reglas():
    caso = construir(None)
    respuesta, transferir, _ = await caso.respond("Cotiza 2 kg de glicerina")
    assert "36.000,00" in respuesta
    assert transferir is False
    assert caso.ultimo_motor == "reglas"


async def test_llm_invalido_cae_en_reglas():
    caso = construir(LLMFalso({"intencion": "cotizar", "items": []}))
    respuesta, _, _ = await caso.respond("Cotiza 2 kg de glicerina")
    assert "36.000,00" in respuesta
    assert caso.ultimo_motor == "reglas"


async def test_llm_que_falla_cae_en_reglas():
    caso = construir(LLMFalso(None))
    respuesta, _, _ = await caso.respond("Dos kilos de glicerina")
    assert "36.000,00" in respuesta
    assert caso.ultimo_motor == "reglas"
