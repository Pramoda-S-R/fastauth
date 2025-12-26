from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional

from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..exceptions import (FailedToVerifySessionException,
                          FailedToVerifyTokenException,
                          InvalidCredentialsException, UserNotFoundException)

if TYPE_CHECKING:
    from ..auth.manager import AuthManager

from ..users.base import BaseUser


def get_current_user_dependency(
    auth: "AuthManager",
) -> Callable[[Request], Coroutine[Any, Any, BaseUser]]:
    use_bearer = True
    if hasattr(auth.strategy, "use_cookie") and auth.strategy.use_cookie:
        use_bearer = False

    security = HTTPBearer(auto_error=False)

    async def _get_current_user_logic(request: Request):
        try:
            credentials = await auth.strategy.extract(request)
            if not credentials:
                raise InvalidCredentialsException(
                    Exception("Received Empty or Invalid Credentials")
                )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise FailedToVerifyTokenException(e)

        user_id = credentials.get("sub") or credentials.get("user_id")
        if not user_id:
            raise InvalidCredentialsException()

        if auth.session:
            session_id = credentials.get("sid")
            if not session_id:
                raise InvalidCredentialsException()
            try:
                session_data = await auth.session.get(session_id)
            except Exception as e:
                # unknown error
                raise FailedToVerifySessionException(e)
            if not session_data:
                # session not found
                raise InvalidCredentialsException()
            session_user_id = session_data.get("user_id")
            if session_user_id != user_id:
                # session user id does not match
                raise InvalidCredentialsException()

        user = await auth.user.get(user_id)
        if not user:
            # user not found
            raise UserNotFoundException()
        return user

    if use_bearer:

        async def get_current_user(
            request: Request,
            _: Optional[HTTPAuthorizationCredentials] = Security(security),
        ):
            return await _get_current_user_logic(request)
    else:

        async def get_current_user(request: Request):
            return await _get_current_user_logic(request)

    return get_current_user


def get_current_session_dependency(
    auth: "AuthManager",
) -> Callable[[Request], Coroutine[Any, Any, str]]:
    use_bearer = True
    if hasattr(auth.strategy, "use_cookie") and auth.strategy.use_cookie:
        use_bearer = False

    security = HTTPBearer(auto_error=False)

    async def _get_current_session_logic(request: Request):
        try:
            credentials = await auth.strategy.extract(request)
            if not credentials:
                raise InvalidCredentialsException(
                    Exception("Received Empty or Invalid Credentials")
                )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise FailedToVerifyTokenException(e)

        return credentials.get("sid")

    if use_bearer:

        async def get_current_session(
            request: Request,
            _: Optional[HTTPAuthorizationCredentials] = Security(security),
        ):
            return await _get_current_session_logic(request)
    else:

        async def get_current_session(request: Request):
            return await _get_current_session_logic(request)

    return get_current_session
