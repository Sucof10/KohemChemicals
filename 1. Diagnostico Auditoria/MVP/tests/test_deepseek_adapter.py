import httpx
import pytest

from app.infrastructure.deepseek_llm import DeepSeekLLMAdapter, _limpiar_json


def test_sin_clave_no_esta_disponible():
    adaptador = DeepSeekLLMAdapter(api_key="")
    assert adaptador.disponible is False


def test_limpia_vallas_de_codigo():
    assert _limpiar_json('```json\n{"intencion": "otro"}\n```') == '{"intencion": "otro"}'
    assert _limpiar_json('{"intencion": "otro"}') == '{"intencion": "otro"}'


@pytest.mark.asyncio
async def test_sin_clave_devuelve_none():
    adaptador = DeepSeekLLMAdapter(api_key="")
    assert await adaptador.interpretar("Hola", "", []) is None


@pytest.mark.asyncio
async def test_error_de_red_devuelve_none(monkeypatch):
    class ClienteFalso:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, *args, **kwargs):
            raise httpx.ConnectError("sin red")

    monkeypatch.setattr("app.infrastructure.deepseek_llm.httpx.AsyncClient", ClienteFalso)
    adaptador = DeepSeekLLMAdapter(api_key="clave-de-prueba")
    assert await adaptador.interpretar("Hola", "", []) is None
