from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.application.dtos import TokenData
from app.presentation.dependencies import get_current_user_data
from app.infrastructure.database import get_db
from app.infrastructure.repositories import SQLiteAuditRepository
from sqlalchemy.ext.asyncio import AsyncSession

class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    entity: str
    entity_id: int | None
    detail: str
    created_at: str

router = APIRouter(prefix="/audit-logs", tags=["Auditoría / Logs"])

@router.get("", response_model=List[AuditLogResponse])
async def list_logs(
    limit: int = 100,
    usr: TokenData = Depends(get_current_user_data),
    db: AsyncSession = Depends(get_db),
):
    if usr.role not in ["admin", "analista"]:
        raise HTTPException(status_code=403, detail="Solo admin o analista pueden consultar los logs.")
    logs = await SQLiteAuditRepository(db).get_all(limit)
    return [AuditLogResponse(id=x.id,user_id=x.user_id,action=x.action,entity=x.entity,entity_id=x.entity_id,detail=x.detail,created_at=x.created_at.isoformat()) for x in logs]
