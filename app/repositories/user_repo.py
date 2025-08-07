from db import User
from sqlmodel import Session, select
import logging
from typing import Union
from uuid import UUID

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
        logger.error(f"ERR GETTING USER BY EMAIL: {e}")
        return None
