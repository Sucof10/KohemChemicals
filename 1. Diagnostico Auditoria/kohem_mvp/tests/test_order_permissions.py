import pytest

@pytest.mark.asyncio
async def test_order_visibility(client):
    await client.post('/api/v1/auth/register',json={'username':'c1','email':'c1@kohem.com','password':'Client123!','role':'cliente'})
    login=await client.post('/api/v1/auth/token',data={'username':'c1','password':'Client123!'})
    assert login.status_code==200
    orders=await client.get('/api/v1/orders',headers={'Authorization':f"Bearer {login.json()['access_token']}"})
    assert orders.status_code==200
    assert orders.json()==[]
