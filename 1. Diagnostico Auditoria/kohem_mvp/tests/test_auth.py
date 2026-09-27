import pytest

@pytest.mark.asyncio
async def test_register_and_login(client):
    res=await client.post('/api/v1/auth/register',json={'username':'testuser','email':'test@kohem.com','password':'Secure123!','role':'cliente'})
    assert res.status_code==201
    login=await client.post('/api/v1/auth/login',json={'username':'testuser','password':'Secure123!'})
    assert login.status_code==200
    assert 'access_token' in login.json()


@pytest.mark.asyncio
async def test_login_oauth2_still_works(client):
    await client.post('/api/v1/auth/register',json={'username':'oauthuser','email':'oauth@kohem.com','password':'Secure123!','role':'cliente'})
    login=await client.post('/api/v1/auth/token',data={'username':'oauthuser','password':'Secure123!'})
    assert login.status_code==200
    assert 'access_token' in login.json()
