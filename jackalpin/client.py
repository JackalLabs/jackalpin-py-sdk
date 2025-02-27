"""
Main client for the JackalPin SDK.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Union, BinaryIO
from urllib.parse import urljoin, quote

import aiohttp
from dotenv import load_dotenv
from pydantic import ValidationError

from jackalpin.errors import (
    BadRequestError,
    JackalPinError,
    NotFoundError,
    ServerError,
    TimeoutError,
    UnauthorizedError,
)
from jackalpin.models import (
    AccountIdResponse,
    AccountUsage,
    BillingPortalResponse,
    CheckoutSessionResponse,
    Collection,
    CollectionCreateResponse,
    CollectionDetailResponse,
    CollectionListResponse,
    FileDetail,
    FileListResponse,
    FileUploadResponse,
    Key,
    KeyListResponse,
    QueueSizeResponse,
    TestKeyResponse,
)


class JackalPinClient:
    """
    Client for interacting with the JackalPin API.
    """

    def __init__(
            self,
            api_key: Optional[str] = None,
            base_url: str = "https://pinapi.jackalprotocol.com/api",
            timeout: float = 30.0,
    ):
        """
        Initialize a new JackalPin API client.

        Args:
            api_key (str, optional): JWT API key for authentication. If not provided,
                                     will check for JACKALPIN_API_KEY environment variable.
            base_url (str, optional): Base URL for the API.
            timeout (float, optional): Timeout for requests in seconds.
        """
        load_dotenv()

        self.api_key = api_key or os.getenv("JACKALPIN_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key for authentication.

        Args:
            api_key (str): JWT API key
        """
        self.api_key = api_key

    async def _request(
            self,
            method: str,
            path: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None,
            files: Optional[Dict[str, BinaryIO]] = None,
            require_auth: bool = True,
    ) -> Dict[str, Any]:
        """
        Make a request to the API.

        Args:
            method (str): HTTP method to use (GET, POST, etc.)
            path (str): API endpoint path
            params (dict, optional): Query parameters
            data (dict, optional): Request body data
            files (dict, optional): Files to upload
            require_auth (bool, optional): Whether authentication is required

        Returns:
            dict: Response data

        Raises:
            UnauthorizedError: If authentication is required but no API key is provided
            JackalPinError: For API errors
        """
        if require_auth and not self.api_key:
            raise UnauthorizedError("API key is required for authentication")

        # Handle path joining properly
        if path.startswith("/"):
            path = path[1:]  # Remove leading slash to prevent urljoin from removing base path
        url = urljoin(self.base_url + "/", path)
        headers = {}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with aiohttp.ClientSession() as session:
                if files:
                    # Handle file uploads
                    form_data = aiohttp.FormData()

                    if data:
                        for key, value in data.items():
                            form_data.add_field(key, value)

                    for key, file_obj in files.items():
                        form_data.add_field(
                            key,
                            file_obj.read(),
                            filename=getattr(file_obj, "name", "file"),
                            content_type="application/octet-stream",
                        )

                    async with session.request(
                            method,
                            url,
                            params=params,
                            data=form_data,
                            headers=headers,
                            timeout=self.timeout,
                    ) as response:
                        return await self._handle_response(response)
                else:
                    # Handle regular requests
                    if data:
                        headers["Content-Type"] = "application/json"
                        data_str = json.dumps(data)
                    else:
                        data_str = None

                    async with session.request(
                            method,
                            url,
                            params=params,
                            data=data_str,
                            headers=headers,
                            timeout=self.timeout,
                    ) as response:
                        return await self._handle_response(response)

        except asyncio.TimeoutError:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds")
        except aiohttp.ClientError as e:
            raise JackalPinError(f"Request failed: {str(e)}")

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """
        Handle the API response.

        Args:
            response (aiohttp.ClientResponse): Response from the API

        Returns:
            dict: Response data

        Raises:
            UnauthorizedError: For 401 responses
            NotFoundError: For 404 responses
            BadRequestError: For 400 responses
            ServerError: For 5xx responses
            JackalPinError: For other errors
        """
        if response.status == 204:
            return {}

        try:
            response_data = await response.json()
        except Exception:
            response_data = await response.text()
            try:
                response_data = json.loads(response_data)
            except Exception:
                response_data = {"message": response_data}

        if 200 <= response.status < 300:
            return response_data

        error_message = (
            response_data.get("message")
            if isinstance(response_data, dict) and "message" in response_data
            else f"HTTP Error {response.status}: {response.reason}"
        )

        if response.status == 401:
            raise UnauthorizedError(error_message, response_data)
        elif response.status == 404:
            raise NotFoundError(error_message, response_data)
        elif response.status == 400:
            raise BadRequestError(error_message, response_data)
        elif 500 <= response.status < 600:
            raise ServerError(error_message, response.status, response_data)
        else:
            raise JackalPinError(error_message, response.status, response_data)

    # API Methods

    async def test_key(self) -> TestKeyResponse:
        """
        Test if the API key is valid.

        Returns:
            TestKeyResponse: Response with success message

        Raises:
            UnauthorizedError: If the API key is invalid
        """
        result = await self._request("GET", "/test")
        return TestKeyResponse(**result)

    async def list_keys(
            self, page: Optional[int] = None, limit: Optional[int] = None
    ) -> KeyListResponse:
        """
        List all API keys.

        Args:
            page (int, optional): Page number for pagination
            limit (int, optional): Number of items per page

        Returns:
            KeyListResponse: List of keys
        """
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        result = await self._request("GET", "/keys", params=params)
        return KeyListResponse(**result)

    async def create_key(self, key_name: str) -> Key:
        """
        Generate a new API key.

        Args:
            key_name (str): Name for the new key

        Returns:
            Key: Generated key info
        """
        result = await self._request("POST", f"/keys/{quote(key_name)}")
        return Key(**result)

    async def delete_key(self, key_name: str) -> None:
        """
        Delete an API key.

        Args:
            key_name (str): Name of the key to delete
        """
        await self._request("DELETE", f"/keys/{quote(key_name)}")

    async def list_files(
            self,
            page: Optional[int] = None,
            limit: Optional[int] = None,
            name: Optional[str] = None,
    ) -> FileListResponse:
        """
        List all files.

        Args:
            page (int, optional): Page number for pagination
            limit (int, optional): Number of items per page
            name (str, optional): Filter by file name

        Returns:
            FileListResponse: List of files
        """
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if name is not None:
            params["name"] = name

        result = await self._request("GET", "/files", params=params)
        return FileListResponse(**result)

    async def upload_file(self, file_obj: BinaryIO, filename: Optional[str] = None) -> FileUploadResponse:
        """
        Upload a file.

        Args:
            file_obj (BinaryIO): File-like object to upload
            filename (str, optional): Name to use for the file. If not provided, will use file_obj.name if available.

        Returns:
            FileUploadResponse: Upload response with CID
        """
        if filename is None:
            filename = getattr(file_obj, "name", "file")
            if filename == "file":
                raise ValueError("Please provide a filename or use a file object with a name attribute")

        result = await self._request(
            "POST", "/files", files={"file": file_obj}
        )
        return FileUploadResponse(**result)

    async def upload_files(self, files: List[BinaryIO]) -> List[FileUploadResponse]:
        """
        Upload multiple files.

        Args:
            files (List[BinaryIO]): List of file-like objects to upload

        Returns:
            List[FileUploadResponse]: List of upload responses
        """
        upload_files = {f"files": file_obj for file_obj in files}
        result = await self._request("POST", "/v1/files", files=upload_files)

        # Handle the response which should be a list of upload responses
        if isinstance(result, list):
            return [FileUploadResponse(**item) for item in result]
        else:
            return [FileUploadResponse(**result)]

    async def delete_file(self, file_id: Union[str, int]) -> None:
        """
        Delete a file.

        Args:
            file_id (Union[str, int]): ID of the file to delete
        """
        await self._request("DELETE", f"/files/{file_id}")

    async def clone_file(self, url: str) -> FileUploadResponse:
        """
        Clone a file from a URL.

        Args:
            url (str): URL to clone

        Returns:
            FileUploadResponse: Upload response with CID
        """
        result = await self._request("POST", "/clone", data={"link": url})
        return FileUploadResponse(**result)

    async def pin_by_cid(self, cid: str) -> None:
        """
        Pin content from IPFS by CID.

        Args:
            cid (str): IPFS Content ID to pin
        """
        await self._request("POST", f"/pin/{cid}")

    async def create_collection(self, name: str) -> CollectionCreateResponse:
        """
        Create a new collection.

        Args:
            name (str): Name for the new collection

        Returns:
            CollectionCreateResponse: Response with collection ID
        """
        result = await self._request("POST", f"/collections/{quote(name)}")
        return CollectionCreateResponse(**result)

    async def list_collections(
            self,
            page: Optional[int] = None,
            limit: Optional[int] = None,
            name: Optional[str] = None,
    ) -> CollectionListResponse:
        """
        List all collections.

        Args:
            page (int, optional): Page number for pagination
            limit (int, optional): Number of items per page
            name (str, optional): Filter by collection name

        Returns:
            CollectionListResponse: List of collections
        """
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if name is not None:
            params["name"] = name

        result = await self._request("GET", "/collections", params=params)
        return CollectionListResponse(**result)

    async def get_collection(
            self,
            collection_id: Union[str, int],
            page: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> CollectionDetailResponse:
        """
        Get collection details including its files.

        Args:
            collection_id (Union[str, int]): Collection ID
            page (int, optional): Page number for pagination
            limit (int, optional): Number of items per page

        Returns:
            CollectionDetailResponse: Collection details
        """
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        result = await self._request(
            "GET", f"/collections/{collection_id}", params=params
        )
        return CollectionDetailResponse(**result)

    async def delete_collection(self, collection_id: Union[str, int]) -> None:
        """
        Delete a collection.

        Args:
            collection_id (Union[str, int]): Collection ID
        """
        await self._request("DELETE", f"/collections/{collection_id}")

    async def add_file_to_collection(
            self, collection_id: Union[str, int], file_id: Union[str, int]
    ) -> None:
        """
        Add a file to a collection.

        Args:
            collection_id (Union[str, int]): Collection ID
            file_id (Union[str, int]): File ID
        """
        await self._request("PUT", f"/collections/{collection_id}/{file_id}")

    async def remove_file_from_collection(
            self, collection_id: Union[str, int], file_id: Union[str, int]
    ) -> None:
        """
        Remove a file from a collection.

        Args:
            collection_id (Union[str, int]): Collection ID
            file_id (Union[str, int]): File ID
        """
        await self._request("DELETE", f"/collections/{collection_id}/{file_id}")

    async def add_collection_reference(
            self, parent_id: Union[str, int], child_id: Union[str, int]
    ) -> None:
        """
        Add a collection as a reference to another collection.

        Args:
            parent_id (Union[str, int]): Parent collection ID
            child_id (Union[str, int]): Child collection ID
        """
        await self._request("PUT", f"/collections/{parent_id}/c/{child_id}")

    async def get_queue_size(self) -> QueueSizeResponse:
        """
        Get the current processing queue size.

        Returns:
            QueueSizeResponse: Queue size information
        """
        result = await self._request("GET", "/queue", require_auth=False)
        return QueueSizeResponse(**result)

    async def create_account(self) -> None:
        """
        Create a customer account.
        """
        await self._request("POST", "/accounts")

    async def get_usage(self) -> AccountUsage:
        """
        Get storage usage statistics.

        Returns:
            AccountUsage: Account usage information
        """
        result = await self._request("GET", "/accounts/usage")
        return AccountUsage(**result)

    async def get_account_id(self) -> AccountIdResponse:
        """
        Get account ID hash.

        Returns:
            AccountIdResponse: Account ID information
        """
        result = await self._request("GET", "/accounts/id")
        return AccountIdResponse(**result)

    async def create_checkout_session(
            self, lookup_key: str, count: int = 1
    ) -> CheckoutSessionResponse:
        """
        Create a checkout session for subscription.

        Args:
            lookup_key (str): Stripe price lookup key
            count (int, optional): Quantity to purchase

        Returns:
            CheckoutSessionResponse: Checkout session information
        """
        params = {}
        if count != 1:
            params["count"] = count

        result = await self._request(
            "POST", f"/payment/checkout/{quote(lookup_key)}", params=params
        )
        return CheckoutSessionResponse(**result)

    async def get_billing_portal_url(self) -> BillingPortalResponse:
        """
        Get URL for managing billing in Stripe customer portal.

        Returns:
            BillingPortalResponse: Billing portal URL information
        """
        result = await self._request("GET", "/payment/manage")
        return BillingPortalResponse(**result)