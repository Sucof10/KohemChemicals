import pytest

async def token(client,username,password):
    return (await client.post('/api/v1/auth/token',data={'username':username,'password':password})).json()['access_token']

@pytest.mark.asyncio
async def test_client_cannot_create_material_but_can_create_order(client):
    await client.post('/api/v1/auth/register',json={'username':'adminx','email':'adminx@kohem.com','password':'Admin123!','role':'admin'})
    await client.post('/api/v1/auth/register',json={'username':'clientx','email':'clientx@kohem.com','password':'Client123!','role':'cliente'})
    admin=await token(client,'adminx','Admin123!')
    customer=await token(client,'clientx','Client123!')
    payload={'name':'Glicerina','category':'Humectantes','unit':'kg','price':20000,'stock':10,'description':'Test'}
    assert (await client.post('/api/v1/materials',json=payload,headers={'Authorization':f'Bearer {customer}'})).status_code==403
    created=await client.post('/api/v1/materials',json=payload,headers={'Authorization':f'Bearer {admin}'})
    assert created.status_code==201
    mid=created.json()['id']
    order=await client.post('/api/v1/orders',json={'items':[{'raw_material_id':mid,'quantity':3}], 'notes':'Pedido MVP'},headers={'Authorization':f'Bearer {customer}'})
    assert order.status_code==201
    assert order.json()['total']==60000
    materials=(await client.get('/api/v1/materials')).json()
    material=next(m for m in materials if m['id']==mid)
    assert material['stock']==7
