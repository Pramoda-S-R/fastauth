from fastapi import HTTPException


class MissingLoginFieldsException(HTTPException):
    """
    Thrown when one or more login fields are missing
    Status code: 400
    """
    def __init__(self, e: Exception = Exception("One or more login fields are missing")):
        super().__init__(status_code=400, detail=f"Missing login fields: {str(e)}")

class InvalidPasswordException(HTTPException):
    """
    Thrown when the password is invalid
    Status code: 400
    """
    def __init__(self, e: Exception = Exception("There was an error validating the password")):
        super().__init__(status_code=400, detail=f"Invalid password: {str(e)}")

class UserNotFoundException(HTTPException):
    """
    Thrown when the user is not found
    Status code: 404
    """
    def __init__(self, e: Exception = Exception("Requested user was not found")):
        super().__init__(status_code=404, detail=f"User not found: {str(e)}")

class FailedToCreateUserException(HTTPException):
    """
    Thrown when the user could not be created
    Status code: 500
    """
    def __init__(self, e: Exception = Exception("Could not create user")):
        super().__init__(status_code=500, detail=f"Failed to create user: {str(e)}")

class FailedToCreateSessionException(HTTPException):
    """
    Thrown when the session could not be created
    Status code: 500
    """
    def __init__(self, e: Exception = Exception("Could not create session")):
        super().__init__(status_code=500, detail=f"Failed to create session: {str(e)}")

class FailedToIssueTokenException(HTTPException):
    """
    Thrown when the token could not be issued
    Status code: 500
    """
    def __init__(self, e: Exception = Exception("Could not issue token")):
        super().__init__(status_code=500, detail=f"Failed to issue token: {str(e)}")

class FailedToSignUpException(HTTPException):
    """
    Thrown when the user could not be signed up
    Status code: 500
    """
    def __init__(self, e: Exception = Exception("There was an unexpected error signing up")):
        super().__init__(status_code=500, detail=f"Failed to sign up: {str(e)}")

class FailedToLoginException(HTTPException):
    """
    Thrown when the user could not be logged in
    Status code: 500
    """
    def __init__(self, e: Exception = Exception("There was an unexpected error logging in")):
        super().__init__(status_code=500, detail=f"Failed to login: {str(e)}")

class FailedToLogoutException(HTTPException):
    """
    Thrown when the user could not be logged out
    Status code: 500
    """
    def __init__(self, e: Exception = Exception("There was an unexpected error logging out")):
        super().__init__(status_code=500, detail=f"Failed to logout: {str(e)}")

