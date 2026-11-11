import json

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError

from app.application.dtos import AIChatRequestDTO, AIChatResponseDTO, TokenData
from app.application.ai_use_cases import AIAssistantUseCase
from app.presentation.dependencies import get_ai_use_cases, get_current_user_data

router = APIRouter(prefix="/ai", tags=["Agente IA"])


@router.post("/chat", response_model=AIChatResponseDTO)
async def chat(
    request: Request,
    ai: AIAssistantUseCase = Depends(get_ai_use_cases),
    usr: TokenData = Depends(get_current_user_data),
):
    content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
    try:
        if content_type == "application/json":
            dto = AIChatRequestDTO.model_validate(await request.json())
        elif content_type in ("application/x-www-form-urlencoded", "multipart/form-data"):
            dto = AIChatRequestDTO.model_validate(dict(await request.form()))
        else:
            raise HTTPException(status_code=415, detail="Use application/json o application/x-www-form-urlencoded.")
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=[{"campo": ".".join(str(p) for p in e["loc"]), "mensaje": e["msg"]} for e in exc.errors()],
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="El cuerpo de la solicitud no es un JSON UTF-8 válido.")

    try:
        response, transfer, reason = await ai.respond(dto.message)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return AIChatResponseDTO(
        response=response,
        transfer_to_employee=transfer,
        reason=reason,
        motor=ai.ultimo_motor,
    )
