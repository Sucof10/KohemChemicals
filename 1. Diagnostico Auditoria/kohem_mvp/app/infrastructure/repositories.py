from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.entities import User, RawMaterial, Order, OrderItem, AuditLog
from app.domain.interfaces import IUserRepository, IRawMaterialRepository, IOrderRepository, IAuditRepository
from app.infrastructure.models import UserModel, RawMaterialModel, OrderModel, OrderItemModel, AuditLogModel

class SQLiteUserRepository(IUserRepository):
    def __init__(self, session): self.session = session
    async def get_by_id(self, user_id):
        m = (await self.session.execute(select(UserModel).where(UserModel.id == user_id))).scalars().first()
        return User(m.id,m.username,m.email,m.hashed_password,m.role,m.is_active) if m else None
    async def get_by_username(self, username):
        m = (await self.session.execute(select(UserModel).where(UserModel.username == username))).scalars().first()
        return User(m.id,m.username,m.email,m.hashed_password,m.role,m.is_active) if m else None
    async def create(self, user):
        m=UserModel(username=user.username,email=user.email,hashed_password=user.hashed_password,role=user.role,is_active=user.is_active)
        self.session.add(m); await self.session.commit(); await self.session.refresh(m); user.id=m.id; return user

class SQLiteRawMaterialRepository(IRawMaterialRepository):
    def __init__(self, session): self.session=session
    def _entity(self,m): return RawMaterial(m.id,m.name,m.category,m.unit,m.price,m.stock,m.description,m.is_active)
    async def get_by_id(self, material_id):
        m=(await self.session.execute(select(RawMaterialModel).where(RawMaterialModel.id==material_id))).scalars().first()
        return self._entity(m) if m else None
    async def get_all(self, skip=0, limit=100):
        ms=(await self.session.execute(select(RawMaterialModel).offset(skip).limit(limit))).scalars().all()
        return [self._entity(m) for m in ms]
    async def create(self, material):
        m=RawMaterialModel(name=material.name,category=material.category,unit=material.unit,price=material.price,stock=material.stock,description=material.description,is_active=material.is_active)
        self.session.add(m); await self.session.commit(); await self.session.refresh(m); material.id=m.id; return material
    async def update(self, material):
        m=(await self.session.execute(select(RawMaterialModel).where(RawMaterialModel.id==material.id))).scalars().first()
        if m:
            m.name,m.category,m.unit,m.price,m.stock,m.description,m.is_active=material.name,material.category,material.unit,material.price,material.stock,material.description,material.is_active
            await self.session.commit()
        return material
    async def delete(self, material_id):
        m=(await self.session.execute(select(RawMaterialModel).where(RawMaterialModel.id==material_id))).scalars().first()
        if not m: return False
        await self.session.delete(m); await self.session.commit(); return True

class SQLiteOrderRepository(IOrderRepository):
    def __init__(self, session): self.session=session
    def _entity(self,m):
        items=[OrderItem(i.id,i.raw_material_id,i.quantity,i.unit_price,i.subtotal) for i in m.items]
        return Order(m.id,m.customer_id,m.status,m.total,m.notes,items,m.created_at,m.updated_at)
    async def get_by_id(self, order_id):
        m=(await self.session.execute(select(OrderModel).where(OrderModel.id==order_id))).scalars().first()
        return self._entity(m) if m else None
    async def get_all(self, customer_id=None, skip=0, limit=100):
        q=select(OrderModel).offset(skip).limit(limit)
        if customer_id is not None: q=q.where(OrderModel.customer_id==customer_id)
        ms=(await self.session.execute(q.order_by(OrderModel.id.desc()))).scalars().all()
        return [self._entity(m) for m in ms]
    async def create(self, order):
        m=OrderModel(customer_id=order.customer_id,status=order.status,total=order.total,notes=order.notes,created_at=order.created_at,updated_at=order.updated_at)
        self.session.add(m); await self.session.flush()
        for item in order.items:
            im=OrderItemModel(order_id=m.id,raw_material_id=item.raw_material_id,quantity=item.quantity,unit_price=item.unit_price,subtotal=item.subtotal)
            self.session.add(im)
        await self.session.commit(); await self.session.refresh(m)
        return await self.get_by_id(m.id)
    async def update_status(self, order_id, status):
        m=(await self.session.execute(select(OrderModel).where(OrderModel.id==order_id))).scalars().first()
        if not m: return None
        m.status=status; m.updated_at=datetime.utcnow(); await self.session.commit(); return await self.get_by_id(order_id)

class SQLiteAuditRepository(IAuditRepository):
    def __init__(self, session): self.session=session
    def _entity(self,m): return AuditLog(m.id,m.user_id,m.action,m.entity,m.entity_id,m.detail,m.created_at)
    async def create(self, log):
        m=AuditLogModel(user_id=log.user_id,action=log.action,entity=log.entity,entity_id=log.entity_id,detail=log.detail,created_at=log.created_at)
        self.session.add(m); await self.session.commit(); await self.session.refresh(m); return self._entity(m)
    async def get_all(self, limit=100):
        ms=(await self.session.execute(select(AuditLogModel).order_by(AuditLogModel.id.desc()).limit(limit))).scalars().all()
        return [self._entity(m) for m in ms]
