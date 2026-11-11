from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_db
from app.infrastructure.repositories import SQLiteUserRepository, SQLiteRawMaterialRepository, SQLiteOrderRepository, SQLiteAuditRepository
from app.infrastructure.security import SecurityService
from app.infrastructure.config import settings
from app.application.auth_use_cases import AuthUseCases
from app.application.material_use_cases import RawMaterialUseCases
from app.application.order_use_cases import OrderUseCases
from app.application.ai_use_cases import AIAssistantUseCase
from app.application.dtos import TokenData
from app.infrastructure.mock_vector_db import MockVectorDbAdapter
from app.infrastructure.mcp_server import KohemMcpAdapter
from app.infrastructure.deepseek_llm import DeepSeekLLMAdapter

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

_llm = DeepSeekLLMAdapter()

def get_auth_use_cases(db: AsyncSession = Depends(get_db)): return AuthUseCases(SQLiteUserRepository(db), SecurityService(), SecurityService())
def get_material_use_cases(db: AsyncSession = Depends(get_db)): return RawMaterialUseCases(SQLiteRawMaterialRepository(db))
def get_order_use_cases(db: AsyncSession = Depends(get_db)): return OrderUseCases(SQLiteOrderRepository(db), SQLiteRawMaterialRepository(db), SQLiteAuditRepository(db))

def get_ai_use_cases(db: AsyncSession = Depends(get_db)) -> AIAssistantUseCase:
    return AIAssistantUseCase(
        rag_repo=MockVectorDbAdapter(),
        mcp_executor=KohemMcpAdapter(SQLiteRawMaterialRepository(db)),
        llm=_llm if _llm.disponible else None,
        modo=settings.AI_MODE,
        max_historial=settings.AI_HISTORY_MAX,
    )

async def get_current_user_data(token: str = Depends(oauth2_scheme)) -> TokenData:
    exc=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas.", headers={"WWW-Authenticate":"Bearer"})
    payload=SecurityService.decode_token(token)
    if not payload or not payload.get("sub") or not payload.get("role") or not payload.get("user_id"):
        raise exc
    return TokenData(username=payload["sub"],role=payload["role"],user_id=int(payload["user_id"]))
