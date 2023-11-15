from pydantic import BaseModel
from uuid import UUID
from litestar.dto import DTOConfig, DTOData
from litestar.contrib.pydantic import PydanticDTO


class TagPost(BaseModel):
    name: str


class PartialTagPostDTO(PydanticDTO[TagPost]):
    config = DTOConfig(partial=True)


class TagReturn(BaseModel):
    id: UUID
    name: str


class TagPostDTO(PydanticDTO[TagReturn]):
    config = DTOConfig(partial=True)
