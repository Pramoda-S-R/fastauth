from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional

from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..exceptions import (FailedToVerifyTokenException,
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

        if auth.session:
            # handle session based auth
            pass

        # For simple token auth where credentials might contain user_id directly or claims
        # Adjust based on what extract returns.
        # Assuming extract returns a dict with "sub" or "user_id"
        user_id = credentials.get("sub") or credentials.get("user_id")
        if not user_id:
            raise InvalidCredentialsException()

        user = await auth.user.get(user_id)
        if not user:
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
