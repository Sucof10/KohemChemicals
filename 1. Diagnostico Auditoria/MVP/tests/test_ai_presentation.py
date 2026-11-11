import pytest
import pytest_asyncio

from app.domain.entities import RawMaterial
from app.infrastructure.repositories import SQLiteRawMaterialRepository
from app.infrastructure.security import SecurityService

pytestmark = pytest.mark.asyncio


def _token(rol: str = "cliente") -> dict:
    token = SecurityService().create_access_token({"sub": "cliente", "role": rol, "user_id": 1})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def catalogo(db_session):
    repo = SQLiteRawMaterialRepository(db_session)
    await repo.create(RawMaterial(None, "Glicerina vegetal", "Humectantes", "kg", 18000, 100, "", True))
    await repo.create(RawMaterial(None, "Aceite esencial de menta", "Aceites esenciales", "kg", 85000, 8, "", True))


async def test_chat_exige_autenticacion(client):
    respuesta = await client.post("/api/v1/ai/chat", json={"message": "Hola"})
    assert respuesta.status_code == 401


async def test_chat_cotizacion_valida(client, catalogo):
    respuesta = await client.post(
        "/api/v1/ai/chat",
        json={"message": "Cotiza 2 kg de glicerina con IVA"},
        headers=_token(),
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["transfer_to_employee"] is False
    assert "42.840,00" in datos["response"]


async def test_chat_mensaje_ausente_devuelve_422(client):
    respuesta = await client.post("/api/v1/ai/chat", json={"texto": "Hola"}, headers=_token())
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["campo"] == "message"


async def test_chat_mensaje_vacio_devuelve_422(client):
    respuesta = await client.post("/api/v1/ai/chat", json={"message": ""}, headers=_token())
    assert respuesta.status_code == 422


async def test_chat_mensaje_solo_espacios_devuelve_422(client):
    respuesta = await client.post("/api/v1/ai/chat", json={"message": "   "}, headers=_token())
    assert respuesta.status_code == 422
    assert "vacío" in respuesta.json()["detail"]


async def test_chat_tipo_incorrecto_devuelve_422(client):
    respuesta = await client.post("/api/v1/ai/chat", json={"message": 123}, headers=_token())
    assert respuesta.status_code == 422


async def test_chat_content_type_no_soportado(client):
    respuesta = await client.post(
        "/api/v1/ai/chat",
        content="Hola",
        headers={**_token(), "Content-Type": "text/plain"},
    )
    assert respuesta.status_code == 415


async def test_chat_json_mal_formado(client):
    respuesta = await client.post(
        "/api/v1/ai/chat",
        content='{"message": ',
        headers={**_token(), "Content-Type": "application/json"},
    )
    assert respuesta.status_code == 400


async def test_chat_ignora_campos_extra(client, catalogo):
    respuesta = await client.post(
        "/api/v1/ai/chat",
        json={"message": "Hola", "rol": "admin"},
        headers=_token(),
    )
    assert respuesta.status_code == 200
