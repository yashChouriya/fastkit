from sqlmodel import Session, select, update
from typing import Union
from uuid import UUID
import logging


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


def update_access_token(
    session: Session, token_instance: Token, access_token: str
) -> Union[Token, None]:
    try:
        token_instance.access_token = access_token
        session.add(token_instance)
        session.commit()
        session.refresh(token_instance)

        return token_instance
    except Exception as e:
        logger.error(f"ERR UPDATING ACCESS TOKEN: {e}")
        return None


def deactivate_user_current_token(session: Session, refresh_token: str) -> bool:
    try:
        # Lock the row to avoid races if multiple requests hit at once
        stmt = (
            select(Token).where(Token.refresh_token == refresh_token).with_for_update()
        )
        token: Token | None = session.exec(stmt).one_or_none()
        if not token or token.is_active is False:
            return False

        token.is_active = False
        session.commit()
        return True
    except Exception:
        session.rollback()
        logger.exception("ERR DEACTIVATING A TOKEN")
        return False


def deactivate_all_tokens_for_user(session: Session, user_id: UUID) -> int:
    """
    Returns the number of rows deactivated.
    """
    stmt = (
        update(Token)
        .where(Token.user_id == user_id, Token.is_active.is_(True))
        .values(
            is_active=False,
        )
        .execution_options(synchronize_session=False)
    )
    try:
        result = session.exec(stmt)
        session.commit()
        return max(result.rowcount or 0, 0)
    except Exception as e:
        session.rollback()
        logger.exception("ERR DEACTIVATING ALL USER TOKENS: %s", e)
        return 0
