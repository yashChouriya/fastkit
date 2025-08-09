from sqlmodel import Session, select
import logging
from typing import Union
from app.models import Token
from app.schemas.token import TokenCreationSchema

logger = logging.getLogger(__name__)


def get_token_by_refresh_token(
    session: Session, refresh_token: str
) -> Union[Token, None]:
    """
    Retrieves a single token instance from the database based on refresh_token.
    """
    # Create a select statement to find the token with the refresh_token
    try:
        statement = select(Token).where(Token.refresh_token == refresh_token)

        # Execute the statement and get the first result
        token_instance = session.exec(statement).first()

        return token_instance
    except Exception as e:
        logger.error(f"ERR GETTING TOKEN INSTANCE BY REFRESH TOKEN: {e}")
        return None


def create_token(
    session: Session, token_data: TokenCreationSchema
) -> Union[Token, None]:
    """
    Retrieves a single token instance from the database based on refresh_token.
    """
    # Create a select statement to find the token with the refresh_token
    try:
        token = Token(
            user_id=token_data.user_id,
            access_token=token_data.access_token,
            refresh_token=token_data.refresh_token,
            ip_address=token_data.ip_address,
            user_agent=token_data.user_agent,
            is_active=True,
        )

        session.add(token)
        session.commit()
        session.refresh(token)

        return token
    except Exception as e:
        logger.error(f"ERR CREATING TOKEN: {e}")
        return None
