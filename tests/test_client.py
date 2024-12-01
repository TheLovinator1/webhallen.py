from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from webhallen import ProductNotFoundError, Webhallen, WebhallenError


class TestWebhallenClient:
    """Test cases for the Webhallen API client."""

    @respx.mock
    def test_get_product_success(self) -> None:  # noqa: PLR6301
        """Test successful product retrieval."""
        # Configure the mock to match the exact URL and method

        json_response: str = Path("tests/370861.json").read_text("utf-8")
        route: respx.Route = respx.get("https://mock-webhallen.com/api/product/370861").mock(
            return_value=httpx.Response(status_code=200, json=json_response)
        )

        client = Webhallen(base_url="https://mock-webhallen.com/api")
        product_json: dict[str, Any] = client.get_product(370861)

        # The product is nested under the 'product' key
        product: dict = product_json["product"]

        assert route.called
        assert product["id"] == 370861
        assert product["name"] == "PNY GeForce RTX 4080 SUPER VERTO OC 16GB"
        assert product["price"]["price"] == "13790.00"

    @respx.mock
    def test_get_product_not_found(self) -> None:  # noqa: PLR6301
        """Test product not found scenario."""
        # Configure mock for not found scenario
        route: respx.Route = respx.get("https://mock-webhallen.com/api/product/9999").mock(
            return_value=httpx.Response(status_code=404)
        )

        client = Webhallen(base_url="https://mock-webhallen.com/api")

        with pytest.raises(ProductNotFoundError):
            client.get_product(9999)

        assert route.called

    @respx.mock
    def test_connection_error(self) -> None:  # noqa: PLR6301
        """Test connection error handling."""
        # Configure mock to simulate connection error
        route = respx.get("https://mock-webhallen.com/api/product/1234").mock(
            side_effect=httpx.RequestError("Connection failed")
        )

        client = Webhallen(base_url="https://mock-webhallen.com/api")

        with pytest.raises(WebhallenError, match="Connection error"):
            client.get_product(1234)

        assert route.called

    @respx.mock
    def test_server_error(self) -> None:  # noqa: PLR6301
        """Test server error handling."""
        # Configure mock for server error
        route = respx.get("https://mock-webhallen.com/api/product/1234").mock(
            return_value=httpx.Response(status_code=500)
        )

        client = Webhallen(base_url="https://mock-webhallen.com/api")

        with pytest.raises(WebhallenError, match="API request failed"):
            client.get_product(1234)

        assert route.called

    @respx.mock
    def test_search_server_error(self) -> None:  # noqa: PLR6301
        """Test search with server error."""
        # Configure mock for server error
        route: respx.Route = respx.get("https://mock-webhallen.com/api/productdiscovery/search/test").mock(
            return_value=httpx.Response(status_code=500)
        )

        client = Webhallen(base_url="https://mock-webhallen.com/api")

        with pytest.raises(WebhallenError, match="Search request failed"):
            client.search("test")

        assert route.called
