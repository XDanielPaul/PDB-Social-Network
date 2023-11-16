from litestar import delete, get, post, put
from uuid import UUID
from litestar.controller import Controller
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tag_model import TagPost, TagReturn, PartialTagPostDTO, TagPostDTO
from app.models.tag_model import Tag
from litestar.dto import DTOData
from sqlalchemy import select
from litestar.exceptions import HTTPException
from app.utils.pika import RabbitMQConnection
from app.models.base_for_modelling import DeleteConfirm


class TagController(Controller):
    path = "/tag"

    @get(path="/", tags=["Tag"])
    async def get_tags(self, db_session: AsyncSession) -> list[TagReturn]:
        all_tags_request = await db_session.execute(select(Tag))
        all_tags: list[Tag] = all_tags_request.scalars().all()
        with RabbitMQConnection() as conn:
            conn.publish_message(
                'info', 'Server is getting all tags')
        return [TagReturn(**(tag.to_dict())) for tag in all_tags]

    @get(path="/{id:uuid}", tags=["Tag"])
    async def get_tag(self, id: UUID, db_session: AsyncSession) -> TagReturn:
        tag_request = await db_session.execute(select(Tag).filter(Tag.id == id))
        tag_data = tag_request.scalars().first()
        if not tag_data:
            raise HTTPException(
                detail="Tag with this id doesn't exist.", status_code=HTTP_404_NOT_FOUND)
        return TagReturn(**(tag_data.to_dict()))

    @post(path="/", dto=PartialTagPostDTO, tags=["Tag"])
    async def create_tag(self, data: DTOData[TagPost], db_session: AsyncSession) -> TagReturn:
        add_this = data.create_instance().model_dump()
        check_if_exists = await db_session.execute(select(Tag).filter(Tag.name == add_this.get('name')))
        if check_if_exists.scalars().first():
            raise HTTPException(
                detail="This tag is already in the database.", status_code=HTTP_409_CONFLICT)
        created_tag = Tag(**add_this)
        db_session.add(created_tag)
        await db_session.commit()
        await db_session.refresh(created_tag)
        return TagReturn(**(created_tag.to_dict()))

    @put(path="/", dto=TagPostDTO, tags=["Tag"])
    async def update_tag(self, data: DTOData[TagReturn], db_session: AsyncSession) -> TagReturn:
        data_dct = data.create_instance().model_dump()
        db_tag = await db_session.get(Tag, data_dct['id'])
        if not db_tag:
            raise HTTPException(
                detail="Tag with this id doesn't exist.", status_code=HTTP_404_NOT_FOUND)
        db_tag.name = data_dct['name']
        await db_session.commit()
        await db_session.refresh(db_tag)
        return TagReturn(**(db_tag.to_dict()))

    @delete(path="/{id:uuid}", status_code=200, tags=["Tag"])
    async def delete_tag(self, id: UUID, db_session: AsyncSession) -> DeleteConfirm:
        db_tag = await db_session.get(Tag, id)
        if not db_tag:
            raise HTTPException(
                detail="Tag with this id doesn't exist.", status_code=HTTP_404_NOT_FOUND)
        await db_session.delete(db_tag)
        await db_session.commit()
        return DeleteConfirm(
            deleted=True,
            message=f"Tag with id [{id}] was deleted."
        )
