from fastapi import APIRouter, Depends
from app.application.dtos import AIChatRequestDTO, AIChatResponseDTO, TokenData
from app.application.ai_use_cases import AIUseCases
from app.presentation.dependencies import get_ai_use_cases, get_current_user_data

router=APIRouter(prefix="/ai",tags=["Agente IA"])

@router.post("/chat",response_model=AIChatResponseDTO)
def chat(dto:AIChatRequestDTO,ai:AIUseCases=Depends(get_ai_use_cases),usr:TokenData=Depends(get_current_user_data)):
    response,transfer,reason=ai.respond(dto.message)
    return AIChatResponseDTO(response=response,transfer_to_employee=transfer,reason=reason)
