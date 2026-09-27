from typing import Protocol
from app.domain.interfaces import IUserRepository
from app.domain.entities import User
from app.domain.exceptions import AuthenticationFailedException, UserAlreadyExistsException
from app.application.dtos import UserCreateDTO

class IPasswordHasher(Protocol):
    def hash_password(self, password: str) -> str: ...
    def verify_password(self, plain_password: str, hashed_password: str) -> bool: ...

class ITokenService(Protocol):
    def create_access_token(self, data: dict) -> str: ...

class AuthUseCases:
    def __init__(self, user_repo: IUserRepository, hasher: IPasswordHasher, token_service: ITokenService):
        self.user_repo = user_repo
        self.hasher = hasher
        self.token_service = token_service

    async def register_user(self, dto: UserCreateDTO) -> User:
        existing = await self.user_repo.get_by_username(dto.username)
        if existing:
            raise UserAlreadyExistsException(dto.username)
        hashed_pwd = self.hasher.hash_password(dto.password)
        user = User(None, dto.username, str(dto.email), hashed_pwd, dto.role.value, True)
        return await self.user_repo.create(user)

    async def authenticate_user(self, username: str, password: str) -> str:
        user = await self.user_repo.get_by_username(username)
        if not user or not user.is_active or not self.hasher.verify_password(password, user.hashed_password):
            raise AuthenticationFailedException()
        return self.token_service.create_access_token({"sub": user.username, "role": user.role, "user_id": user.id})
