from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from app.application.dtos import OrderCreateDTO, OrderStatusUpdateDTO, OrderResponseDTO, OrderItemResponseDTO, TokenData
from app.application.order_use_cases import OrderUseCases
from app.presentation.dependencies import get_order_use_cases, get_current_user_data
from app.domain.exceptions import EntityNotFoundException, InsufficientStockException, InsufficientPermissionsException, InvalidOrderStateException
import json

router=APIRouter(prefix="/orders",tags=["Pedidos"])

def to_response(order):
    return OrderResponseDTO(id=order.id,customer_id=order.customer_id,status=order.status,total=order.total,notes=order.notes,
        items=[OrderItemResponseDTO(id=i.id,raw_material_id=i.raw_material_id,quantity=i.quantity,unit_price=i.unit_price,subtotal=i.subtotal) for i in order.items],
        created_at=order.created_at.isoformat(),updated_at=order.updated_at.isoformat())

async def parse_order_create(request: Request):
    content_type=request.headers.get("content-type","").split(";",1)[0].lower()
    if content_type == "application/json":
        return OrderCreateDTO.model_validate(await request.json())
    if content_type in ("application/x-www-form-urlencoded", "multipart/form-data"):
        form=await request.form(); data=dict(form)
        if isinstance(data.get("items"), str):
            try: data["items"]=json.loads(data["items"])
            except json.JSONDecodeError: raise HTTPException(status_code=422, detail="El campo items debe contener un JSON válido.")
        return OrderCreateDTO.model_validate(data)
    raise HTTPException(status_code=415, detail="Use application/json o application/x-www-form-urlencoded.")

async def parse_status(request: Request):
    content_type=request.headers.get("content-type","").split(";",1)[0].lower()
    if content_type == "application/json": return OrderStatusUpdateDTO.model_validate(await request.json())
    if content_type in ("application/x-www-form-urlencoded", "multipart/form-data"): return OrderStatusUpdateDTO.model_validate(dict(await request.form()))
    raise HTTPException(status_code=415, detail="Use application/json o application/x-www-form-urlencoded.")

@router.post("",response_model=OrderResponseDTO,status_code=201)
async def create_order(request:Request,uc:OrderUseCases=Depends(get_order_use_cases),usr:TokenData=Depends(get_current_user_data)):
    if usr.role!="cliente": raise HTTPException(status_code=403,detail="Solo un cliente puede registrar un pedido.")
    try:return to_response(await uc.create_order(await parse_order_create(request),usr.user_id))
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
async def update_status(order_id:int,request:Request,uc:OrderUseCases=Depends(get_order_use_cases),usr:TokenData=Depends(get_current_user_data)):
    try:
        dto=await parse_status(request)
        return to_response(await uc.update_status(order_id,dto.status.value,usr.user_id,usr.role))
    except EntityNotFoundException as e:raise HTTPException(status_code=404,detail=str(e))
    except InsufficientPermissionsException as e:raise HTTPException(status_code=403,detail=str(e))
    except InvalidOrderStateException as e:raise HTTPException(status_code=409,detail=str(e))
