"""
Custom exceptions for the JackalPin SDK.
"""

from typing import Any, Dict, Optional


class JackalPinError(Exception):
    """Base exception for all JackalPin SDK errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class UnauthorizedError(JackalPinError):
    """Raised when the API key is invalid or missing."""
    
    def __init__(
        self,
        message: str = "Invalid or missing API key",
        response: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=401, response=response)


class NotFoundError(JackalPinError):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        response: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=404, response=response)


class TimeoutError(JackalPinError):
    """Raised when a request times out."""
    
    def __init__(
        self,
        message: str = "Request timed out",
        response: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=None, response=response)


class BadRequestError(JackalPinError):
    """Raised when a request is malformed or invalid."""
    
    def __init__(
        self,
        message: str = "Bad request",
        response: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=400, response=response)


class ServerError(JackalPinError):
    """Raised when the server returns a 5xx error."""
    
    def __init__(
        self,
        message: str = "Server error",
        status_code: int = 500,
        response: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=status_code, response=response)
