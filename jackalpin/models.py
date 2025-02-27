"""
Data models for the JackalPin SDK.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Key(BaseModel):
    """API key model."""
    
    name: str
    key: str


class KeyInfo(BaseModel):
    """Information about an API key."""
    
    name: str
    created_at: str


class KeyListResponse(BaseModel):
    """Response from listing API keys."""
    
    keys: List[KeyInfo]
    count: int


class FileDetail(BaseModel):
    """Detailed information about a file."""
    
    id: int
    file_name: str = Field(alias="file_name")
    cid: str
    size: int
    created_at: str = Field(alias="created_at")

    class Config:
        populate_by_name = True


class FileListResponse(BaseModel):
    """Response from listing files."""
    
    files: List[FileDetail]
    count: int


class FileUploadResponse(BaseModel):
    """Response from uploading a file."""
    
    name: str
    cid: str
    merkle: str
    id: Optional[int] = None


class Collection(BaseModel):
    """Collection model."""
    
    name: str
    id: int
    cid: str


class CollectionListResponse(BaseModel):
    """Response from listing collections."""
    
    collections: List[Collection]
    count: int


class CollectionDetailResponse(BaseModel):
    """Detailed information about a collection."""
    
    files: List[FileDetail]
    count: int
    collections: List[Collection]
    name: str
    cid: str


class CollectionCreateResponse(BaseModel):
    """Response from creating a collection."""
    
    id: int


class AccountUsage(BaseModel):
    """Storage usage information."""
    
    bytes_allowed: int = Field(alias="bytes_allowed")
    bytes_used: int = Field(alias="bytes_used")

    class Config:
        populate_by_name = True


class AccountIdResponse(BaseModel):
    """Response from getting account ID."""
    
    id: str


class QueueSizeResponse(BaseModel):
    """Response from getting queue size."""
    
    size: int


class CheckoutSessionResponse(BaseModel):
    """Response from creating a checkout session."""
    
    id: str


class BillingPortalResponse(BaseModel):
    """Response from getting billing portal URL."""
    
    url: str


class TestKeyResponse(BaseModel):
    """Response from testing an API key."""
    
    message: str
