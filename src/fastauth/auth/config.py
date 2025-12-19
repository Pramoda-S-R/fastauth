# auth/config.py
from enum import Enum
from typing import Annotated, Callable

from pydantic import BaseModel, StringConstraints, field_validator

from .models import SignupRequest

LowerSnakeStr = Annotated[
    str,
    StringConstraints(pattern=r'^[a-z_]+$')
]

class AuthConfig(BaseModel):
    slug: LowerSnakeStr
    session_ttl_seconds: int = 3600
    secure_cookies: bool = True
    login_fields: list[str] = ["email"]
    login_after_signup: bool = True
    password_validator: Callable[[str], bool] = lambda x: True
    roles: type[Enum] | None = None
    signup_request: type[BaseModel] | None = SignupRequest

    @field_validator("signup_request")
    @classmethod
    def validate_signup_request(cls, model_cls: type[BaseModel] | None):
        if model_cls is None:
            return model_cls

        # Ensure it's a Pydantic model class
        if not issubclass(model_cls, BaseModel):
            raise TypeError("signup_request must be a Pydantic BaseModel")

        # Required fields you expect
        required_fields = {"password"}

        model_fields = model_cls.model_fields

        missing = required_fields - model_fields.keys()
        if missing:
            raise ValueError(
                f"signup_request is missing required fields: {missing}"
            )

        return model_cls
