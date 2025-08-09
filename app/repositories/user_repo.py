from sqlmodel import Session, select
import logging
from typing import Union
from uuid import UUID
from app.models import User
from app.schemas.auth import UserCreationSchema

logger = logging.getLogger(__name__)


def get_user_by_email(session: Session, email: str) -> Union[User, None]:
    """
    Retrieves a single user from the database based on their email address.
    """
    # Create a select statement to find the user with the matching email
    try:
        statement = select(User).where(User.email == email)

        # Execute the statement and get the first result
        user = session.exec(statement).first()

        return user
    except Exception as e:
        logger.error(f"ERR GETTING USER BY EMAIL: {e}")
        return None


def get_user_by_id(session: Session, user_id: UUID) -> Union[User, None]:
    """
    Retrieves a single user from the database based on their user id.
    """
    # Create a select statement to find the user with the matching user id
    try:
        statement = select(User).where(User.id == user_id)

        # Execute the statement and get the first result
        user = session.exec(statement).first()

        return user
    except Exception as e:
        logger.error(f"ERR GETTING USER BY ID: {e}")
        return None


def get_user_by_username(session: Session, username: str) -> Union[User, None]:
    """
    Retrieves a single user from the database based on their username.
    """
    # Create a select statement to find the user with the matching username
    try:
        statement = select(User).where(User.username == username)

        # Execute the statement and get the first result
        user = session.exec(statement).first()

        return user
    except Exception as e:
        logger.error(f"ERR GETTING USER BY USERNAME: {e}")
        return None


def create_user(session: Session, user_data: UserCreationSchema) -> Union[User, bool]:
    try:
        user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            username=user_data.username,
            is_active=True,
            is_email_verified=False,
        )
        user.set_password(user_data.password)

        session.add(user)
        session.commit()

        return True
    except Exception as e:
        logger.error(f"ERR CREATING USER: {e}")
        return False
