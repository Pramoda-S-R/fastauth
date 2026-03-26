"""
FastAPI router for authentication endpoints.

Provides:
- POST /auth/signup - User registration
- POST /auth/login - User login
- POST /auth/logout - User logout
- GET /auth/oauth/{provider} - OAuth login redirect
"""

import uuid
from typing import TYPE_CHECKING, Any, Optional

from fastapi import APIRouter, Depends, Request, Response

from ..crypto import hash_password, verify_password, soft_fingerprint
from ..exceptions import (LoginException, LogoutException, SessionException,
                          SignUpException, TokenException, UserException)
from ..users.base import BaseUser
from ..utils import get_accept_language, get_client_ip, get_user_agent, get_accept_encoding

if TYPE_CHECKING:
    from ..auth.manager import AuthManager


def build_auth_router(auth: "AuthManager") -> APIRouter:
    """Build and configure the authentication router.

    Creates endpoints for signup, login, logout, and OAuth.
    Uses the provided AuthManager for business logic.
    """
    router = APIRouter(prefix="/auth", tags=["Authentication"])

    async def _issue_tokens(
        request: Request, response: Response, user: BaseUser
    ) -> Optional[dict[str, str]]:
        """Issue authentication tokens for a user.

        Creates a session (if session store configured) and issues
        tokens via the configured strategy.

        Args:
            request: FastAPI request for metadata extraction
            response: FastAPI response for setting cookies
            user: Authenticated user to issue tokens for

        Returns:
            Token dict if not using cookies, None otherwise
        """
        # Extract request metadata for audit logging
        user_agent = get_user_agent(request)
        accept_language = get_accept_language(request)
        accept_encoding = get_accept_encoding(request)
        client_ip = get_client_ip(request)

        # Generate unique token identifier
        jti = str(uuid.uuid4())

        # Get user ID (must exist at this point)
        user_id = user.id
        if not user_id:
            raise UserException("User ID is missing", status_code=500)

        # Create session if session store is configured
        session_id: Optional[str] = None
        if auth.session:
            try:
                fingerprint = soft_fingerprint(user_agent, client_ip, accept_language, accept_encoding)
                session_data = {"jti": jti, "user_agent": user_agent, "ip": client_ip, "fingerprint": fingerprint}
                session_id = await auth.session.create(
                    user_id=user_id,
                    data=session_data,
                    ttl=auth.config.session_ttl_seconds,
                )
            except Exception as e:
                raise SessionException(str(e))

        # Issue tokens via strategy
        try:
            claims = {"sub": user_id, "jti": jti}
            if session_id:
                claims["sid"] = session_id
            token = await auth.strategy.issue(
                response, claims, auth.config.session_ttl_seconds
            )
        except Exception as e:
            raise TokenException(str(e))

        return token

    async def _build_user_response(
        user: BaseUser, token: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        """Build response data from user model.

        Args:
            user: User model to convert
            token: Optional token to include in response

        Returns:
            Dict suitable for JSON response
        """
        response_data = user.model_dump(exclude={"password"})
        if token:
            response_data.update(token)
        return response_data

    @router.post("/signup", status_code=201)
    async def signup(
        form: auth.config.signup_request,
        request: Request,
        response: Response,
    ):
        """Register a new user account.

        Validates password, hashes it, creates user, and optionally logs in.
        """
        try:
            # Extract password and user data
            password = form.password
            user_data = form.model_dump(exclude={"password"})

            # Validate login fields are provided
            if not any(field in user_data for field in auth.config.login_fields):
                raise SignUpException("Missing login field")

            # Validate password strength
            try:
                auth.config.password_validator(password)
            except Exception as e:
                raise SignUpException(f"Weak password: {str(e)}")

            # Hash password and create user
            hashed_password = hash_password(password)
            user_data["password"] = hashed_password

            try:
                user = await auth.user.create(**user_data)
            except Exception as e:
                raise UserException(str(e), status_code=400)

            # Issue tokens if login_after_signup is enabled
            token = None
            if auth.config.login_after_signup:
                token = await _issue_tokens(request, response, user)

            return await _build_user_response(user, token)

        except UserException:
            raise
        except SignUpException:
            raise
        except Exception as e:
            raise SignUpException(str(e))

    @router.post("/login")
    async def login(
        form: auth.config.login_request,
        request: Request,
        response: Response,
    ):
        """Authenticate a user and issue tokens.

        Validates credentials and returns user data with tokens.
        """
        try:
            # Validate login fields
            login_data = form.model_dump(exclude={"password"})
            if not any(field in login_data for field in auth.config.login_fields):
                raise LoginException()

            # Find user by login field
            user = await auth.user.find(**login_data)
            if not user:
                raise LoginException()

            # Verify password
            if not verify_password(form.password, user.password):
                raise LoginException()

            # Issue tokens
            token = await _issue_tokens(request, response, user)

            return await _build_user_response(user, token)

        except LoginException:
            raise
        except Exception as e:
            raise LoginException(str(e))

    @router.post("/logout", status_code=204)
    async def logout(
        response: Response,
        session_id: str = Depends(auth.current_session),
    ):
        """Log out the current user.

        Deletes session and revokes tokens.
        """
        try:
            if auth.session and session_id:
                await auth.session.delete(session_id)
            await auth.strategy.revoke(response)
        except Exception as e:
            raise LogoutException(str(e))

    # OAuth routes (if OAuth provider configured)
    if auth.oauth:

        @router.get("/oauth/{provider}")
        async def oauth_login(provider: str):
            """Redirect to OAuth provider for authentication."""
            return {"url": auth.oauth.get_authorization_url(provider)}

    return router
