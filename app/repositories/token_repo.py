from db import Token
from sqlmodel import Session, select
import logging
from typing import Union

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
