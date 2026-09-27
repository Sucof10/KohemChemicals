from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.application.dtos import UserCreateDTO, UserResponseDTO, Token
from app.application.auth_use_cases import AuthUseCases
from app.presentation.dependencies import get_auth_use_cases
from app.domain.exceptions import UserAlreadyExistsException, AuthenticationFailedException

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
async def register(
    dto: UserCreateDTO,
    auth: AuthUseCases = Depends(get_auth_use_cases)
):
    try:
        return await auth.register_user(dto)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description=(
        "Autenticación mediante formulario application/x-www-form-urlencoded, "
        "compatible con el formato de Swagger mostrado en el proyecto del profesor. "
        "Permite ingresar los datos directamente en los campos del formulario."
    ),
)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    auth: AuthUseCases = Depends(get_auth_use_cases)
):
    try:
        token = await auth.authenticate_user(form.username, form.password)
        return {"access_token": token, "token_type": "bearer"}
    except AuthenticationFailedException as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/token",
    response_model=Token,
    summary="Login OAuth2",
    description=(
        "Endpoint compatible con OAuth2 Password y con el botón Authorize de Swagger. "
        "Recibe application/x-www-form-urlencoded."
    ),
)
async def login_oauth(
    form: OAuth2PasswordRequestForm = Depends(),
    auth: AuthUseCases = Depends(get_auth_use_cases)
):
    try:
        token = await auth.authenticate_user(form.username, form.password)
        return {"access_token": token, "token_type": "bearer"}
    except AuthenticationFailedException as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
