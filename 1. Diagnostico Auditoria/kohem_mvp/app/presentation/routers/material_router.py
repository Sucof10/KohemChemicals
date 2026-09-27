from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.application.dtos import RawMaterialCreateDTO, RawMaterialUpdateDTO, RawMaterialResponseDTO, TokenData
from app.application.material_use_cases import RawMaterialUseCases
from app.presentation.dependencies import get_material_use_cases, get_current_user_data
from app.domain.exceptions import EntityNotFoundException, InsufficientPermissionsException

router=APIRouter(prefix="/materials",tags=["Materias primas / Inventario"])

@router.get("",response_model=List[RawMaterialResponseDTO])
async def list_materials(skip:int=0,limit:int=100,uc:RawMaterialUseCases=Depends(get_material_use_cases)):
    return await uc.list_materials(skip,limit)

@router.get("/{material_id}",response_model=RawMaterialResponseDTO)
async def get_material(material_id:int,uc:RawMaterialUseCases=Depends(get_material_use_cases)):
    try:return await uc.get_material(material_id)
    except EntityNotFoundException as e:raise HTTPException(status_code=404,detail=str(e))

@router.post("",response_model=RawMaterialResponseDTO,status_code=201)
async def create_material(dto:RawMaterialCreateDTO,uc:RawMaterialUseCases=Depends(get_material_use_cases),usr:TokenData=Depends(get_current_user_data)):
    try:return await uc.create_material(dto,usr.role)
    except InsufficientPermissionsException as e:raise HTTPException(status_code=403,detail=str(e))

@router.put("/{material_id}",response_model=RawMaterialResponseDTO)
async def update_material(material_id:int,dto:RawMaterialUpdateDTO,uc:RawMaterialUseCases=Depends(get_material_use_cases),usr:TokenData=Depends(get_current_user_data)):
    try:return await uc.update_material(material_id,dto,usr.role)
    except EntityNotFoundException as e:raise HTTPException(status_code=404,detail=str(e))
    except InsufficientPermissionsException as e:raise HTTPException(status_code=403,detail=str(e))

@router.delete("/{material_id}",status_code=204)
async def delete_material(material_id:int,uc:RawMaterialUseCases=Depends(get_material_use_cases),usr:TokenData=Depends(get_current_user_data)):
    try:await uc.delete_material(material_id,usr.role)
    except EntityNotFoundException as e:raise HTTPException(status_code=404,detail=str(e))
    except InsufficientPermissionsException as e:raise HTTPException(status_code=403,detail=str(e))
