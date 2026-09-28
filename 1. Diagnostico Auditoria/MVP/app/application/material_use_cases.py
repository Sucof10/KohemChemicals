from typing import List
from app.domain.interfaces import IRawMaterialRepository
from app.domain.entities import RawMaterial
from app.domain.exceptions import EntityNotFoundException, InsufficientPermissionsException
from app.application.dtos import RawMaterialCreateDTO, RawMaterialUpdateDTO

class RawMaterialUseCases:
    def __init__(self, repo: IRawMaterialRepository):
        self.repo = repo

    async def list_materials(self, skip=0, limit=100) -> List[RawMaterial]:
        return await self.repo.get_all(skip, limit)

    async def get_material(self, material_id: int) -> RawMaterial:
        material = await self.repo.get_by_id(material_id)
        if not material:
            raise EntityNotFoundException("Materia prima", material_id)
        return material

    async def create_material(self, dto: RawMaterialCreateDTO, role: str) -> RawMaterial:
        if role != "admin":
            raise InsufficientPermissionsException()
        return await self.repo.create(RawMaterial(None, dto.name, dto.category, dto.unit, dto.price, dto.stock, dto.description, True))

    async def update_material(self, material_id: int, dto: RawMaterialUpdateDTO, role: str) -> RawMaterial:
        if role not in ["admin", "analista"]:
            raise InsufficientPermissionsException()
        material = await self.get_material(material_id)
        for field in ["name", "category", "unit", "price", "stock", "description"]:
            value = getattr(dto, field)
            if value is not None:
                setattr(material, field, value)
        return await self.repo.update(material)

    async def delete_material(self, material_id: int, role: str) -> bool:
        if role != "admin":
            raise InsufficientPermissionsException()
        await self.get_material(material_id)
        return await self.repo.delete(material_id)
