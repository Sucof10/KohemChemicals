from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    analista = "analista"
    cliente = "cliente"

class OrderStatus(str, Enum):
    pendiente = "pendiente"
    confirmado = "confirmado"
    preparando = "preparando"
    enviado = "enviado"
    entregado = "entregado"
    cancelado = "cancelado"

class LoginRequestDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None

class UserCreateDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.cliente

class UserResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    role: str
    is_active: bool

class RawMaterialCreateDTO(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    category: str = Field(..., min_length=2, max_length=80)
    unit: str = Field(..., min_length=1, max_length=20)
    price: float = Field(..., gt=0)
    stock: float = Field(..., ge=0)
    description: Optional[str] = Field(None, max_length=500)

class RawMaterialUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    category: Optional[str] = Field(None, min_length=2, max_length=80)
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=500)

class RawMaterialResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: str
    unit: str
    price: float
    stock: float
    description: Optional[str]
    is_active: bool

class OrderItemCreateDTO(BaseModel):
    raw_material_id: int = Field(..., gt=0)
    quantity: float = Field(..., gt=0)

class OrderCreateDTO(BaseModel):
    items: List[OrderItemCreateDTO] = Field(..., min_length=1)
    notes: Optional[str] = Field(None, max_length=500)

class OrderStatusUpdateDTO(BaseModel):
    status: OrderStatus

class OrderItemResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    raw_material_id: int
    quantity: float
    unit_price: float
    subtotal: float

class OrderResponseDTO(BaseModel):
    id: int
    customer_id: int
    status: OrderStatus
    total: float
    notes: Optional[str]
    items: List[OrderItemResponseDTO]
    created_at: str
    updated_at: str

class AIChatRequestDTO(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

class AIChatResponseDTO(BaseModel):
    response: str
    transfer_to_employee: bool
    reason: Optional[str] = None
