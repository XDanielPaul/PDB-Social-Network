from litestar import delete, get, post, put
from uuid import UUID
from litestar.controller import Controller
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK
from app.controllers.provide_services import provides_user_service
from app.models.user_model import ReadDTO, UserModel, WriteDTO
from app.utils.controller import Service
from app.utils.pika import RabbitMQConnection


# UserModel controller which handles requests for /users
class UserController(Controller):
    # Dependency injection
    dto = WriteDTO
    return_dto = ReadDTO
    dependencies = {"service": Provide(provides_user_service, sync_to_thread=False)}

    @get(path="/users")
    async def get_users(self, service: Service) -> list[UserModel]:
        return await service.list()

    @get(path="/users/{user_id:uuid}")
    async def get_user(self, service: Service, user_id: UUID) -> UserModel:
        return await service.get(user_id)

    @post(path="/users")
    async def create_user(self, service: Service, data: UserModel) -> UserModel:
        new_user = await service.create(data)
        await service.repository.session.commit()
        with RabbitMQConnection() as conn:
            conn.publish_message('hello', UserModel.to_dict(new_user, 'post'))

        return new_user

    @put(path="/users/{user_id:uuid}")
    async def update_user(self, data: UserModel, service: Service, user_id: UUID) -> UserModel:
        updated_user = await service.update(user_id, data)
        await service.repository.session.commit()
        with RabbitMQConnection() as conn:
            conn.publish_message('hello', UserModel.to_dict(updated_user, 'put'))
        return updated_user

    @delete(path="/users/{user_id:uuid}", status_code=HTTP_200_OK)
    async def delete_user(self, service: Service, user_id: UUID) -> UserModel:
        deleted_user = await service.delete(user_id)
        await service.repository.session.commit()
        with RabbitMQConnection() as conn:
            conn.publish_message('hello', UserModel.to_dict(deleted_user, 'delete'))
        return deleted_user