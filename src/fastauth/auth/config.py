# auth/config.py
from enum import Enum
from typing import Annotated, Callable

from pydantic import BaseModel, StringConstraints, model_validator

from .models import LoginRequest, SignupRequest

LowerSnakeStr = Annotated[str, StringConstraints(pattern=r"^[a-z_]+$")]


class AuthConfig(BaseModel):
    slug: LowerSnakeStr
    session_ttl_seconds: int = 3600
    secure_cookies: bool = True
    login_fields: list[str] = ["email"]
    login_after_signup: bool = True
    password_validator: Callable[[str], bool] = lambda x: True
    roles: type[Enum] | None = None
    signup_request: type[BaseModel] | None = SignupRequest
    login_request: type[BaseModel] | None = LoginRequest

    @model_validator(mode="after")
    def validate_signup_request(self):
        if self.signup_request is None:
            return self

        if not issubclass(self.signup_request, BaseModel):
            raise TypeError("signup_request must be a Pydantic BaseModel")

        model_fields = self.signup_request.model_fields

        if "password" not in model_fields:
            raise ValueError("signup_request is missing required field: password")

        available_login_fields = set(self.login_fields) & model_fields.keys()
        if not available_login_fields:
            raise ValueError(
                f"signup_request must have at least one of the login fields: {self.login_fields}"
            )

        return self

    @model_validator(mode="after")
    def validate_login_request(self):
        if self.login_request is None:
            return self

        if not issubclass(self.login_request, BaseModel):
            raise TypeError("login_request must be a Pydantic BaseModel")

        model_fields = self.login_request.model_fields

        if "password" not in model_fields:
            raise ValueError("login_request is missing required field: password")

        available_login_fields = set(self.login_fields) & model_fields.keys()
        if not available_login_fields:
            raise ValueError(
                f"login_request must have at least one of the login fields: {self.login_fields}"
            )

        return self
