from fastapi import Depends, Request, HTTPException
from datetime import datetime
from logging import Logger

# local imports
from app.repositories.user_repo import get_user_by_id
from app.core.jwt import decode_token
from app.core.db import Session, get_session

logger = Logger(__name__)


def authenticator(request: Request, session: Session = Depends(get_session)):
    try:
        access = request.cookies.get("access", "")
        if not access:
            raise HTTPException(status_code=401, detail="Unauthorized")

        access_token_payload = decode_token(token=access)
        if not access_token_payload or access_token_payload.exp < int(
            datetime.now().timestamp()
        ):
            raise HTTPException(status_code=401, detail="Unauthorized")
        user_id = access_token_payload.identity
        user = get_user_by_id(session=session, user_id=user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Unauthorized")

        request.state.user = user
    except Exception as e:
        logger.error(f"ERR AT AUTHENTICATOR MIDDLEWARE: {e}")
        raise HTTPException(status_code=401, detail="Unauthorized")
