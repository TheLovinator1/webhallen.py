from __future__ import annotations

import json
from typing import Any

import httpx

from .exceptions import ProductNotFoundError, WebhallenError


class Webhallen:
    """A Python wrapper for the Webhallen API.

    Attributes:
        _base_url (str): Base URL for Webhallen API
        _timeout (int): Timeout for API requests in seconds
    """

    def __init__(self, base_url: str = "https://www.webhallen.com/api", timeout: int = 10) -> None:
        """Initialize the Webhallen API client.

        Args:
            base_url (str, optional): Base URL for the API. Defaults to Webhallen's API endpoint.
            timeout (int, optional): Request timeout in seconds. Defaults to 10.
        """
        self._base_url: str = base_url
        self._timeout: int = timeout
        self._client = httpx.Client(base_url=self._base_url, timeout=self._timeout)

    def get_product(self, product_id: int) -> dict[str, Any]:
        """Retrieve details for a specific product by its ID.

        Args:
            product_id (int): Unique identifier for the product

        Returns:
            Dict containing product details

        Raises:
            ProductNotFoundError: If the product cannot be found
            WebhallenError: For other API-related errors
        """
        try:
            response: httpx.Response = self._client.get(f"/product/{product_id}")
            response.raise_for_status()

            try:
                product_data = json.loads(response.json())
            except json.JSONDecodeError as e:
                msg = f"Failed to decode JSON response: {e!s}"
                raise WebhallenError(msg) from e

            if not product_data:
                msg = f"No product found with ID {product_id}"
                raise ProductNotFoundError(msg)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == httpx.codes.NOT_FOUND:
                msg: str = f"Product with ID {product_id} not found"
                raise ProductNotFoundError(msg) from e
            msg = f"API request failed: {e!s}"
            raise WebhallenError(msg) from e

        except httpx.RequestError as e:
            msg = f"Connection error: {e!s}"
            raise WebhallenError(msg) from e

        else:
            return product_data

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search for products matching the given query.

        Args:
            query (str): Search term

        Returns:
            List of product dictionaries matching the search query

        Raises:
            WebhallenError: For API-related errors
        """
        # TODO(TheLovinator): #1 There is also sort options, categories, and filters that can be applied
        # https://github.com/TheLovinator1/webhallen.py/issues/1
        try:
            response: httpx.Response = self._client.get(f"/productdiscovery/search/{query}")
            response.raise_for_status()

            return response.json().get("products", [])

        except httpx.HTTPStatusError as e:
            msg: str = f"Search request failed: {e!s}"
            raise WebhallenError(msg) from e

        except httpx.RequestError as e:
            msg: str = f"Connection error: {e!s}"
            raise WebhallenError(msg) from e

    def close(self) -> None:
        """Close the HTTP client connection."""
        self._client.close()

    def __del__(self) -> None:
        """Ensure client is closed when object is deleted."""
        self.close()
