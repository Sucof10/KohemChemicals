from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.application.dtos import OrderCreateDTO, OrderStatusUpdateDTO, OrderResponseDTO, OrderItemResponseDTO, TokenData
from app.application.order_use_cases import OrderUseCases
from app.presentation.dependencies import get_order_use_cases, get_current_user_data
from app.domain.exceptions import EntityNotFoundException, InsufficientStockException, InsufficientPermissionsException, InvalidOrderStateException

router=APIRouter(prefix="/orders",tags=["Pedidos"])

def to_response(order):
    return OrderResponseDTO(id=order.id,customer_id=order.customer_id,status=order.status,total=order.total,notes=order.notes,
        items=[OrderItemResponseDTO(id=i.id,raw_material_id=i.raw_material_id,quantity=i.quantity,unit_price=i.unit_price,subtotal=i.subtotal) for i in order.items],
        created_at=order.created_at.isoformat(),updated_at=order.updated_at.isoformat())

@router.post("",response_model=OrderResponseDTO,status_code=201)
async def create_order(dto:OrderCreateDTO,uc:OrderUseCases=Depends(get_order_use_cases),usr:TokenData=Depends(get_current_user_data)):
    if usr.role!="cliente": raise HTTPException(status_code=403,detail="Solo un cliente puede registrar un pedido.")
    try:return to_response(await uc.create_order(dto,usr.user_id))
    except (EntityNotFoundException,InsufficientStockException) as e:raise HTTPException(status_code=400,detail=str(e))

@router.get("",response_model=List[OrderResponseDTO])
async def list_orders(skip:int=0,limit:int=100,uc:OrderUseCases=Depends(get_order_use_cases),usr:TokenData=Depends(get_current_user_data)):
    orders=await uc.list_orders(usr.user_id,usr.role,skip,limit)
    return [to_response(o) for o in orders]

@router.get("/{order_id}",response_model=OrderResponseDTO)
async def get_order(order_id:int,uc:OrderUseCases=Depends(get_order_use_cases),usr:TokenData=Depends(get_current_user_data)):
    try:return to_response(await uc.get_order(order_id,usr.user_id,usr.role))
    except EntityNotFoundException as e:raise HTTPException(status_code=404,detail=str(e))
    except InsufficientPermissionsException as e:raise HTTPException(status_code=403,detail=str(e))

@router.patch("/{order_id}/status",response_model=OrderResponseDTO)
async def update_status(order_id:int,dto:OrderStatusUpdateDTO,uc:OrderUseCases=Depends(get_order_use_cases),usr:TokenData=Depends(get_current_user_data)):
    try:return to_response(await uc.update_status(order_id,dto.status.value,usr.user_id,usr.role))
    except EntityNotFoundException as e:raise HTTPException(status_code=404,detail=str(e))
    except InsufficientPermissionsException as e:raise HTTPException(status_code=403,detail=str(e))
    except InvalidOrderStateException as e:raise HTTPException(status_code=409,detail=str(e))
