"""
FastAuth exception hierarchy.

All exceptions inherit from HTTPException to integrate with FastAPI's
error handling. Each exception maps to an appropriate HTTP status code.
"""

from fastapi import HTTPException


class SignUpException(HTTPException):
    """Raised when user signup fails.

    Status: 400 Bad Request - client provided invalid input
    """

    def __init__(self, detail: str = "Failed to sign up"):
        super().__init__(status_code=400, detail=detail)


class LoginException(HTTPException):
    """Raised when login fails due to invalid credentials.

    Status: 401 Unauthorized - authentication required
    """

    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(status_code=401, detail=detail)


class LogoutException(HTTPException):
    """Raised when logout fails unexpectedly.

    Status: 500 Internal Server Error - unexpected server error
    """

    def __init__(self, detail: str = "Failed to logout"):
        super().__init__(status_code=500, detail=detail)


class TokenException(HTTPException):
    """Raised when token validation fails.

    Status: 401 Unauthorized - invalid or expired token
    """

    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(status_code=401, detail=detail)


class SessionException(HTTPException):
    """Raised when session validation fails.

    Status: 401 Unauthorized - invalid or expired session
    """

    def __init__(self, detail: str = "Invalid or expired session"):
        super().__init__(status_code=401, detail=detail)


class UserException(HTTPException):
    """Raised when user operation fails.

    Status: 404 Not Found - user not found
          400 Bad Request - user already exists or invalid input
    """

    def __init__(self, detail: str = "User operation failed", status_code: int = 404):
        super().__init__(status_code=status_code, detail=detail)


class CredentialsException(HTTPException):
    """Raised when credential validation fails.

    Status: 401 Unauthorized - credentials invalid or missing
    """

    def __init__(self, detail: str = "Invalid or missing credentials"):
        super().__init__(status_code=401, detail=detail)
