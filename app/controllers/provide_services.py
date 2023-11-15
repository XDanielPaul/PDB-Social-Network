
from app.utils.controller import Service
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import UserRepository


# Service dependency
def provides_user_service(db_session: AsyncSession) -> Service:
    """Constructs repository and service objects for the request."""
    return Service(UserRepository(session=db_session))
