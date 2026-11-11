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
        ]

    async def get_all(self, skip=0, limit=100):
        return self.materiales

    async def get_by_id(self, material_id):
        return next((m for m in self.materiales if m.id == material_id), None)


class LLMConversacional:
    nombre = "falso"

    def __init__(self, interpretacion=None, redaccion="Claro, con gusto te ayudo."):
        self.interpretacion = interpretacion
        self.redaccion = redaccion
        self.llamadas = {"interpretar": [], "redactar": []}

    async def interpretar(self, mensaje, contexto, materiales, historial=None):
        self.llamadas["interpretar"].append({"mensaje": mensaje, "historial": historial})
        return self.interpretacion

    async def redactar(self, mensaje, datos, contexto, historial=None):
        self.llamadas["redactar"].append({"mensaje": mensaje, "datos": datos, "historial": historial})
        return self.redaccion


def construir(llm=None, modo="conversacional", max_historial=8):
    return AIAssistantUseCase(
        rag_repo=MockVectorDbAdapter(),
        mcp_executor=KohemMcpAdapter(CatalogoFalso()),
        llm=llm,
        modo=modo,
        max_historial=max_historial,
    )


async def test_conversacional_usa_redaccion_del_modelo():
    llm = LLMConversacional(
        interpretacion={
            "intencion": "cotizar",
            "items": [{"material": "glicerina", "cantidad": 2, "unidad": "kg"}],
        },
        redaccion="Por 2 kg de glicerina te queda en $36.000.",
    )
    caso = construir(llm)
    respuesta, transferir, _ = await caso.respond("Quiero dos kilos de glicerina")
    assert respuesta == "Por 2 kg de glicerina te queda en $36.000."
    assert transferir is False
    assert caso.ultimo_motor == "falso-conversacional"
    assert caso.ultimos_datos["tipo"] == "cotizacion"
    assert caso.ultimos_datos["total"] == 36000.0


async def test_conversacional_recibe_datos_verificados():
    llm = LLMConversacional(
        interpretacion={
            "intencion": "cotizar",
            "items": [{"material": "glicerina", "cantidad": 2, "unidad": "kg"}],
        }
    )
    caso = construir(llm)
    await caso.respond("Quiero dos kilos de glicerina")
    datos = llm.llamadas["redactar"][0]["datos"]
    assert datos["subtotal"] == 36000.0
    assert datos["items"][0]["precio_unitario"] == 18000


async def test_conversacional_sin_redaccion_usa_plantilla():
    llm = LLMConversacional(
        interpretacion={
            "intencion": "cotizar",
            "items": [{"material": "glicerina", "cantidad": 2, "unidad": "kg"}],
        },
        redaccion=None,
    )
    caso = construir(llm)
    respuesta, _, _ = await caso.respond("Quiero dos kilos de glicerina")
    assert "36.000,00" in respuesta
    assert caso.ultimo_motor == "falso"


async def test_conversacional_charla_libre():
    llm = LLMConversacional(interpretacion={"intencion": "otro"}, redaccion="¡Hola! ¿En qué te ayudo?")
    caso = construir(llm)
    respuesta, _, _ = await caso.respond("Buenas tardes")
    assert respuesta == "¡Hola! ¿En qué te ayudo?"
    assert llm.llamadas["redactar"][0]["datos"] is None


async def test_historial_se_reenvia_y_se_recorta():
    llm = LLMConversacional(interpretacion={"intencion": "otro"}, redaccion="ok")
    caso = construir(llm, max_historial=2)
    historial = [
        {"role": "user", "content": f"mensaje {i}"} for i in range(5)
    ]
    await caso.respond("¿Y de ese?", historial)
    enviado = llm.llamadas["interpretar"][0]["historial"]
    assert len(enviado) == 2
    assert enviado[-1]["content"] == "mensaje 4"
    assert llm.llamadas["redactar"][0]["historial"] == enviado


async def test_modo_asistente_no_redacta():
    llm = LLMConversacional(interpretacion={"intencion": "otro"})
    caso = construir(llm, modo="asistente")
    respuesta, _, _ = await caso.respond("Hola")
    assert "disponibilidad, pedidos" in respuesta
    assert llm.llamadas["redactar"] == []
