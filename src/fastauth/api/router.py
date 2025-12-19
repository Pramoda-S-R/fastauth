# api/router.py
from pydantic import BaseModel, ConfigDict
from typing import TYPE_CHECKING
from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import RedirectResponse
from ..crypto import hash_password
from ..exceptions import (
    MissingLoginFieldsException,
    InvalidPasswordException,
    FailedToCreateUserException,
    FailedToCreateSessionException,
    FailedToSignUpException,
)
if TYPE_CHECKING:
    from ..auth.manager import AuthManager


def build_auth_router(auth: "AuthManager") -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["Auth"])

    # Create a SignupRequest model dynamically from the user schema, excluding 'id'
    class SignupRequest(BaseModel):
        password: str
        
        model_config = ConfigDict(extra="allow")


    @router.post("/signup")
    async def signup(req: SignupRequest, response: Response): # type: ignore
        try:
            # extract password
            password = req.password
            user_data = req.model_dump(exclude={"password"})

            # validate login fields
            if any(field not in user_data for field in auth.config.login_fields):
                raise MissingLoginFieldsException()

            # validate password
            if not auth.config.password_validator(password):
                raise InvalidPasswordException()

            # hash password
            hashed_password = hash_password(password)
            user_data.update({"password": hashed_password})

            # create user
            try:
                user = await auth.user.create(user_data)
            except Exception as e:
                raise FailedToCreateUserException(e)

            # login after signup
            if auth.config.login_after_signup:
                try:
                    session_id = await auth.session.create(user_id=user.id, data={})
                    print(session_id)
                    await auth.strategy.issue(response, user_id=user.id)
                except Exception as e:
                    raise FailedToCreateSessionException(e)
            
            return user
        except Exception as e:
            raise FailedToSignUpException(e)

    @router.post("/login")
    async def login(req: dict): # type: ignore
        # Implementation will follow based on searching for user with provided login_fields
        pass

    @router.post("/logout")
    async def logout(response: Response):
        pass

    if auth.oauth:
        @router.get("/oauth/{provider}")
        async def oauth_login(provider: str):
            return RedirectResponse(
                auth.oauth.get_authorization_url()
            )

    return router
