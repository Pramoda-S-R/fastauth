# api/router.py
import json
import uuid
from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from ..crypto import hash_password, verify_password
from ..exceptions import (FailedToCreateSessionException,
                          FailedToCreateUserException,
                          FailedToIssueTokenException, FailedToLoginException,
                          FailedToLogoutException, FailedToSignUpException,
                          InvalidPasswordException,
                          MissingLoginFieldsException, UserNotFoundException)
from ..users.base import BaseUser

if TYPE_CHECKING:
    from ..auth.manager import AuthManager


def build_auth_router(auth: "AuthManager") -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["Auth"])

    # Helper functions
    async def issue_tokens(request: Request, response: Response, user: BaseUser):
        session_id: str | None = None
        ua = request.headers.get("user-agent")
        lang = request.headers.get("accept-language")
        ip = request.client.host
        print(ua, lang, ip)
        try:
            if auth.session:
                session_data = {}
                session_id = await auth.session.create(user.id, session_data)
        except Exception as e:
            raise FailedToCreateSessionException(e)

        try:
            jti = str(uuid.uuid4())
            claims = {"sub": user.id, "jti": jti}
            if session_id:
                claims.update({"sid": session_id})
            token = await auth.strategy.issue(
                response, claims, auth.config.session_ttl_seconds
            )
        except Exception as e:
            raise FailedToIssueTokenException(e)

        return token

    class SignUpResponse(auth.config.signup_request):
        id: str
        access_token: Optional[str] = None
        refresh_token: Optional[str] = None

    @router.post("/signup", response_model=SignUpResponse, status_code=201)
    async def signup(
        form: auth.config.signup_request, request: Request, response: Response
    ):
        try:
            # extract password
            password = form.password
            user_data = form.model_dump(exclude={"password"})

            # validate login fields
            if not any(field in user_data for field in auth.config.login_fields):
                raise MissingLoginFieldsException()

            # validate password
            if not auth.config.password_validator(password):
                raise InvalidPasswordException()

            # hash password
            hashed_password = hash_password(password)
            user_data.update({"password": hashed_password})

            # create user
            try:
                user = await auth.user.create(**user_data)
            except Exception as e:
                raise FailedToCreateUserException(e)

            # login after signup
            if auth.config.login_after_signup:
                token = await issue_tokens(request, response, user)

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
    async def login(
        form: auth.config.login_request, request: Request, response: Response
    ):
        try:
            # validate login fields
            if not any(
                field in form.model_dump(exclude={"password"})
                for field in auth.config.login_fields
            ):
                raise MissingLoginFieldsException()

            # validate password
            try:
                auth.config.password_validator(form.password)
            except Exception as e:
                raise InvalidPasswordException(e)

            # find user
            user = await auth.user.find(**form.model_dump(exclude={"password"}))
            if not user:
                raise UserNotFoundException()

            # verify password
            if not verify_password(form.password, user.password):
                raise InvalidPasswordException(Exception("Passwords do not match"))

            # issue tokens
            token = await issue_tokens(request, response, user)

            # prepare response
            response_data = user.model_dump(exclude={"password"})
            if token is not None:
                response_data.update(token)
            response.body = json.dumps(response_data, indent=2).encode("utf-8")
            response.headers["Content-Type"] = "application/json"
            response.media_type = "application/json"
            response.status_code = 200
            return response
        except Exception as e:
            if issubclass(e.__class__, HTTPException):
                raise e
            raise FailedToLoginException(e)

    @router.post("/logout")
    async def logout(request: Request, response: Response):
        try:
            pass
        except Exception as e:
            if issubclass(e.__class__, HTTPException):
                raise e
            raise FailedToLogoutException(e)

    if auth.oauth:

        @router.get("/oauth/{provider}")
        async def oauth_login(provider: str):
            return RedirectResponse(auth.oauth.get_authorization_url())

    return router
