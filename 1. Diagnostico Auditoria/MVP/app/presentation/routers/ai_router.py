from fastapi import APIRouter, Depends, HTTPException, Request
from app.application.dtos import AIChatRequestDTO, AIChatResponseDTO, TokenData
from app.application.ai_use_cases import AIUseCases
from app.presentation.dependencies import get_ai_use_cases, get_current_user_data

router=APIRouter(prefix="/ai",tags=["Agente IA"])

@router.post("/chat",response_model=AIChatResponseDTO)
async def chat(request:Request,ai:AIUseCases=Depends(get_ai_use_cases),usr:TokenData=Depends(get_current_user_data)):
    content_type=request.headers.get("content-type","").split(";",1)[0].lower()
    if content_type == "application/json":
        dto=AIChatRequestDTO.model_validate(await request.json())
    elif content_type in ("application/x-www-form-urlencoded", "multipart/form-data"):
        dto=AIChatRequestDTO.model_validate(dict(await request.form()))
    else:
        raise HTTPException(status_code=415, detail="Use application/json o application/x-www-form-urlencoded.")
    response,transfer,reason=ai.respond(dto.message)
    return AIChatResponseDTO(response=response,transfer_to_employee=transfer,reason=reason)
