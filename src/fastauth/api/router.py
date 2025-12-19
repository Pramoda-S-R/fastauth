# api/router.py
from typing import TYPE_CHECKING, Optional

import uuid
import json
from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

from ..crypto import hash_password
from ..exceptions import (FailedToCreateSessionException,
                          FailedToCreateUserException, FailedToSignUpException,
                          InvalidPasswordException,
                          MissingLoginFieldsException, FailedToIssueTokenException)

if TYPE_CHECKING:
    from ..auth.manager import AuthManager


def build_auth_router(auth: "AuthManager") -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["Auth"])

    class SignUpResponse(auth.config.signup_request):
        id: str
        access_token: Optional[str] = None
        refresh_token: Optional[str] = None
        

    @router.post("/signup", response_model=SignUpResponse, status_code=201)
    async def signup(req: auth.config.signup_request, response: Response): # type: ignore
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
                    if auth.session:
                        session_id = await auth.session.create(user.id, user.model_dump(exclude={"password", "id"}))
                except Exception as e:
                    raise FailedToCreateSessionException(e)

                try:
                    jti = session_id if session_id else str(uuid.uuid4())
                    claims = {"sub": user.id, "jti": jti}
                    token = await auth.strategy.issue(response, claims, auth.config.session_ttl_seconds)
                except Exception as e:
                    raise FailedToIssueTokenException(e)

            response_data = user.model_dump(exclude={"password"})
            if auth.config.login_after_signup and token is not None:
                response_data.update(token)

            response.body = json.dumps(response_data, indent=2).encode("utf-8")
            response.headers["Content-Type"] = "application/json"
            response.media_type = "application/json"
            response.status_code = 201
            return response
        except Exception as e:
            if issubclass(e.__class__, HTTPException):
                raise e
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
