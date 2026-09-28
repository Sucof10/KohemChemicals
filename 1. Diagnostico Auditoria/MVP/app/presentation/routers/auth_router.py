from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from app.application.dtos import UserCreateDTO, UserResponseDTO, Token
from app.application.auth_use_cases import AuthUseCases
from app.presentation.dependencies import get_auth_use_cases
from app.domain.exceptions import UserAlreadyExistsException, AuthenticationFailedException
import json

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def _model_from_form(form, model_cls):
    data = dict(form)
    return model_cls.model_validate(data)


@router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    description="Acepta JSON (application/json) o campos individuales (application/x-www-form-urlencoded). En Swagger puedes cambiar el tipo de contenido y probar cualquiera de las dos formas.",
)
async def register(
    request: Request,
    auth: AuthUseCases = Depends(get_auth_use_cases),
):
    content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
    if content_type == "application/json":
        dto = UserCreateDTO.model_validate(await request.json())
    elif content_type == "application/x-www-form-urlencoded" or content_type == "multipart/form-data":
        dto = _model_from_form(await request.form(), UserCreateDTO)
    else:
        raise HTTPException(status_code=415, detail="Use application/json o application/x-www-form-urlencoded.")
    try:
        return await auth.register_user(dto)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/token",
    response_model=Token,
    summary="Login / Obtener JWT",
    description="Acepta formulario OAuth2 o JSON. El formulario muestra grant_type, username, password, scope, client_id y client_secret; JSON permite enviar el mismo contenido como objeto editable.",
)
async def login_oauth(
    request: Request,
    auth: AuthUseCases = Depends(get_auth_use_cases),
):
    content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
    if content_type == "application/json":
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
    elif content_type == "application/x-www-form-urlencoded" or content_type == "multipart/form-data":
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
    else:
        raise HTTPException(status_code=415, detail="Use application/json o application/x-www-form-urlencoded.")
    if not username or not password:
        raise HTTPException(status_code=422, detail="username y password son obligatorios.")
    try:
        token = await auth.authenticate_user(str(username), str(password))
        return {"access_token": token, "token_type": "bearer"}
    except AuthenticationFailedException as e:
        raise HTTPException(status_code=401, detail=str(e), headers={"WWW-Authenticate": "Bearer"})
