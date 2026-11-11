import pytest

from app.infrastructure.security import SecurityService

pytestmark = pytest.mark.asyncio


def _cabecera(rol="admin", user_id=1):
    token = SecurityService().create_access_token({"sub": rol, "role": rol, "user_id": user_id})
    return {"Authorization": f"Bearer {token}"}


async def test_material_con_precio_negativo_devuelve_422(client):
    respuesta = await client.post(
        "/api/v1/materials",
        json={"name": "Prueba", "category": "Prueba", "unit": "kg", "price": -100, "stock": 10},
        headers=_cabecera(),
    )
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["campo"] == "price"


async def test_material_con_stock_negativo_devuelve_422(client):
    respuesta = await client.post(
        "/api/v1/materials",
        json={"name": "Prueba", "category": "Prueba", "unit": "kg", "price": 100, "stock": -1},
        headers=_cabecera(),
    )
    assert respuesta.status_code == 422


async def test_pedido_con_cantidad_cero_devuelve_422(client):
    respuesta = await client.post(
        "/api/v1/orders",
        json={"items": [{"raw_material_id": 1, "quantity": 0}]},
        headers=_cabecera("cliente"),
    )
    assert respuesta.status_code == 422


async def test_pedido_con_cantidad_negativa_devuelve_422(client):
    respuesta = await client.post(
        "/api/v1/orders",
        json={"items": [{"raw_material_id": 1, "quantity": -2}]},
        headers=_cabecera("cliente"),
    )
    assert respuesta.status_code == 422


async def test_registro_con_usuario_corto_devuelve_422(client):
    respuesta = await client.post(
        "/api/v1/auth/register",
        json={"username": "ab", "email": "ab@kohem.com", "password": "Secure123!", "role": "cliente"},
    )
    assert respuesta.status_code == 422


async def test_json_mal_formado_devuelve_400(client):
    respuesta = await client.post(
        "/api/v1/materials",
        content=b'{"name": ',
        headers={**_cabecera(), "Content-Type": "application/json"},
    )
    assert respuesta.status_code == 400


async def test_content_type_invalido_devuelve_415(client):
    respuesta = await client.post(
        "/api/v1/materials",
        content=b"x",
        headers={**_cabecera(), "Content-Type": "text/plain"},
    )
    assert respuesta.status_code == 415


async def test_items_de_formulario_mal_formados_devuelve_422(client):
    respuesta = await client.post(
        "/api/v1/orders",
        data={"items": "{no-es-json"},
        headers=_cabecera("cliente"),
    )
    assert respuesta.status_code == 422
