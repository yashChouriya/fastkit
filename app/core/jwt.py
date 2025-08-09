from jose import jwt
import os
from datetime import datetime, timedelta
import logging
from typing import Union, Dict, Literal
from app.schemas.token import TokenPayloadSchema
from uuid import UUID

logger = logging.getLogger(__name__)


def generate_token(
    identity: UUID, token_type: Literal["access", "refresh"], algorithm="HS256"
) -> Union[None | Dict]:
    try:
        secret = os.getenv("JWT_SECRET", None)
        if not secret:
            raise Exception(
                "'JWT_SECRET is not not present in the environment variables!"
            )

        if token_type == "access":
            expire_after_hours = 1
        elif token_type == "refresh":
            expire_after_hours = 24

        access_token_expires = datetime.now() + timedelta(hours=expire_after_hours)
        token = jwt.encode(
            {
                "identity": str(identity),
                "exp": int(access_token_expires.timestamp()),
                "type": token_type,
            },
            secret,
            algorithm=algorithm,
        )

        return token
    except Exception as e:
        logger.error(f"ERR WHILE GENERATING TOKEN : {e}")
        return None


def decode_token(token: str, algorithm="HS256") -> Union[None | TokenPayloadSchema]:
    try:
        secret = os.getenv("JWT_SECRET", None)
        if not secret:
            raise Exception(
                "'JWT_SECRET is not not present in the environment variables!"
            )
        payload = jwt.decode(token=token, algorithms=algorithm, key=secret)
        return TokenPayloadSchema(**payload)
    except Exception as e:
        logger.error(f"ERR WHILE DECODING TOKEN : {e}")
        return None
