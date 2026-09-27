from typing import List
from app.domain.interfaces import IOrderRepository, IRawMaterialRepository, IAuditRepository
from app.domain.entities import Order, OrderItem, AuditLog
from app.domain.exceptions import EntityNotFoundException, InsufficientStockException, InsufficientPermissionsException, InvalidOrderStateException
from app.application.dtos import OrderCreateDTO

class OrderUseCases:
    def __init__(self, order_repo: IOrderRepository, material_repo: IRawMaterialRepository, audit_repo: IAuditRepository):
        self.order_repo = order_repo
        self.material_repo = material_repo
        self.audit_repo = audit_repo

    async def create_order(self, dto: OrderCreateDTO, customer_id: int) -> Order:
        # MVP rule: verify availability before registering the order.
        items = []
        total = 0.0
        for item_dto in dto.items:
            material = await self.material_repo.get_by_id(item_dto.raw_material_id)
            if not material or not material.is_active:
                raise EntityNotFoundException("Materia prima", item_dto.raw_material_id)
            if material.stock < item_dto.quantity:
                raise InsufficientStockException(material.name, material.stock, item_dto.quantity)
            subtotal = round(material.price * item_dto.quantity, 2)
            items.append(OrderItem(None, material.id, item_dto.quantity, material.price, subtotal))
            total += subtotal

        # Reserve stock immediately so a second order cannot request the same quantity.
        for item in items:
            material = await self.material_repo.get_by_id(item.raw_material_id)
            material.stock = round(material.stock - item.quantity, 4)
            await self.material_repo.update(material)

        order = Order(None, customer_id, "pendiente", round(total, 2), dto.notes, items)
        created = await self.order_repo.create(order)
        await self.audit_repo.create(AuditLog(None, customer_id, "CREATE", "order", created.id, f"Pedido creado por cliente {customer_id}; total={created.total}"))
        return created

    async def get_order(self, order_id: int, user_id: int, role: str) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise EntityNotFoundException("Pedido", order_id)
        if role == "cliente" and order.customer_id != user_id:
            raise InsufficientPermissionsException()
        return order

    async def list_orders(self, user_id: int, role: str, skip=0, limit=100) -> List[Order]:
        return await self.order_repo.get_all(user_id if role == "cliente" else None, skip, limit)

    async def update_status(self, order_id: int, new_status: str, user_id: int, role: str) -> Order:
        order = await self.get_order(order_id, user_id, role)
        if role == "cliente" and new_status != "cancelado":
            raise InsufficientPermissionsException()
        if order.status in ["entregado", "cancelado"]:
            raise InvalidOrderStateException("El pedido ya está en un estado final y no puede modificarse.")
        if new_status == "cancelado" and order.status != "cancelado":
            # Return reserved stock when a pending/active order is cancelled.
            for item in order.items:
                material = await self.material_repo.get_by_id(item.raw_material_id)
                if material:
                    material.stock = round(material.stock + item.quantity, 4)
                    await self.material_repo.update(material)
        updated = await self.order_repo.update_status(order_id, new_status)
        await self.audit_repo.create(AuditLog(None, user_id, "UPDATE_STATUS", "order", order_id, f"Estado cambiado a {new_status}"))
        return updated
