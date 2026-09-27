from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    hashed_password: str
    role: str
    is_active: bool = True

@dataclass
class RawMaterial:
    id: Optional[int]
    name: str
    category: str
    unit: str
    price: float
    stock: float
    description: Optional[str] = None
    is_active: bool = True

@dataclass
class OrderItem:
    id: Optional[int]
    raw_material_id: int
    quantity: float
    unit_price: float
    subtotal: float

@dataclass
class Order:
    id: Optional[int]
    customer_id: int
    status: str
    total: float
    notes: Optional[str]
    items: List[OrderItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AuditLog:
    id: Optional[int]
    user_id: Optional[int]
    action: str
    entity: str
    entity_id: Optional[int]
    detail: str
    created_at: datetime = field(default_factory=datetime.utcnow)
