"""
JackalPin Python SDK
A client library for the Jackal Pin IPFS pinning service.
"""

from jackalpin.client import JackalPinClient
from jackalpin.errors import JackalPinError, UnauthorizedError, TimeoutError, NotFoundError

__version__ = "1.0.0"
__all__ = [
    "JackalPinClient",
    "JackalPinError",
    "UnauthorizedError",
    "TimeoutError",
    "NotFoundError",
]
