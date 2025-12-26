from typing import TYPE_CHECKING, Callable, Coroutine, Any
from fastapi import Request, HTTPException
from ..exceptions import FailedToVerifyTokenException, InvalidCredentialsException, UserNotFoundException

if TYPE_CHECKING:
    from ..auth.manager import AuthManager

def get_current_user_dependency(
    auth: "AuthManager",
) -> Callable[[Request], Coroutine[Any, Any, Any]]:
    async def get_current_user(request: Request):
        try:
            credentials = await auth.strategy.extract(request)
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

    return get_current_user