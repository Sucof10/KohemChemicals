from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.infrastructure.database import init_db, AsyncSessionLocal
from app.infrastructure.security import SecurityService
from app.infrastructure.repositories import SQLiteUserRepository, SQLiteRawMaterialRepository
from app.domain.entities import User, RawMaterial
from app.presentation.routers import auth_router, material_router, order_router, ai_router, audit_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with AsyncSessionLocal() as session:
        repo=SQLiteUserRepository(session); sec=SecurityService()
        if not await repo.get_by_username("admin"):
            await repo.create(User(None,"admin","admin@kohem.local",sec.hash_password("AdminPass123!"),"admin",True))
        if not await repo.get_by_username("cliente"):
            await repo.create(User(None,"cliente","cliente@kohem.local",sec.hash_password("ClientPass123!"),"cliente",True))
        mat_repo=SQLiteRawMaterialRepository(session)
        if not await mat_repo.get_by_id(1):
            await mat_repo.create(RawMaterial(None,"Aceite esencial de menta","Aceites esenciales","kg",85000,50,"Materia prima para formulaciones cosméticas."))
        if not await mat_repo.get_by_id(2):
            await mat_repo.create(RawMaterial(None,"Glicerina vegetal","Humectantes","kg",18000,100,"Materia prima para formulaciones cosméticas."))
        if not await mat_repo.get_by_id(3):
            await mat_repo.create(RawMaterial(None,"Ácido cítrico","Reguladores de pH","kg",12000,75,"Materia prima para formulaciones y ajuste de pH."))
    yield

app=FastAPI(title="Kohem Chemicals MVP API", version="1.0.0", lifespan=lifespan, description="MVP para gestión de materias primas y registro de pedidos.")
app.include_router(auth_router.router,prefix="/api/v1")
app.include_router(material_router.router,prefix="/api/v1")
app.include_router(order_router.router,prefix="/api/v1")
app.include_router(ai_router.router,prefix="/api/v1")
app.include_router(audit_router.router,prefix="/api/v1")

@app.get("/")
def root(): return {"status":"API Online","project":"Kohem Chemicals","swagger_docs":"/docs"}
