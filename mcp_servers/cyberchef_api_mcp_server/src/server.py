#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import httpx
import logging
from typing import Any, Optional, List
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

from cyberchefoperations import CyberChefOperations

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Create an MCP server
mcp = FastMCP("CyberChef API MCP Server")

# Determine the CyberChef backend URL (the actual Node.js CyberChef-server)
cyberchef_backend_url = os.getenv("CYBERCHEF_BACKEND_URL")
if cyberchef_backend_url is None:
    log.warning(
        "No environment variable CYBERCHEF_BACKEND_URL found, defaulting to http://localhost:3000/"
    )
    cyberchef_backend_url = "http://localhost:3000/"


class CyberChefRecipeOperation(BaseModel):
    """Model for a recipe operation with or without arguments"""
    op: str
    args: Optional[List[str]] = None


def create_api_request(endpoint: str, request_data: dict) -> Any | dict[str, str]:
    """
    Send a POST request to one of the CyberChef backend API endpoints.

    :param endpoint: API endpoint (relative to CyberChef backend) to call
    :param request_data: data to send with the POST request
    :return: dict object of response data
    """
    api_url = f"{cyberchef_backend_url.rstrip('/')}/{endpoint.lstrip('/')}"
    request_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        log.info(f"Sending POST request to {api_url}")
        response = httpx.post(
            url=api_url,
            headers=request_headers,
            json=request_data
        )
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as req_exc:
        log.error(f"HTTP POST request to {api_url} failed: {req_exc}")
        return {"error": f"HTTP POST request to {api_url} failed: {req_exc}"}


@mcp.resource("data://cyberchef-operations-categories")
def get_cyberchef_operations_categories() -> list:
    """Get updated CyberChef categories for additional context / selection of operations"""
    return CyberChefOperations().get_all_categories()


@mcp.resource("data://cyberchef-operations-by-category/{category}")
def get_cyberchef_operation_by_category(category: str) -> list:
    """Get list of CyberChef operations for a selected category"""
    return CyberChefOperations().get_operations_by_category(category=category)


@mcp.tool()
def bake_recipe(input_data: str, recipe: List[CyberChefRecipeOperation]) -> dict:
    """Bake a recipe on the given input data"""
    request_data = {
        "input": input_data,
        "recipe": [op.model_dump() for op in recipe]
    }
    response_data = create_api_request(endpoint="bake", request_data=request_data)

    # If the response has a byte array, decode to string
    if response_data.get("type") == "byteArray":
        response_data["value"] = bytes(response_data["value"]).decode()
        response_data["type"] = "string"
    return response_data


@mcp.tool()
def batch_bake_recipe(batch_input_data: List[str], recipe: List[CyberChefRecipeOperation]) -> dict:
    """Bake a recipe on a batch of input data"""
    request_data = {
        "input": batch_input_data,
        "recipe": [op.model_dump() for op in recipe]
    }
    response_data = create_api_request(endpoint="batch/bake", request_data=request_data)

    for response in response_data:
        if response.get("type") == "byteArray":
            response["value"] = bytes(response["value"]).decode()
            response["type"] = "string"
    return response_data


@mcp.tool()
def perform_magic_operation(
    input_data: str,
    depth: int = 3,
    intensive_mode: bool = False,
    extensive_language_support: bool = False,
    crib_str: str = ""
) -> dict:
    """Run CyberChef's magic operation"""
    request_data = {
        "input": input_data,
        "args": {
            "depth": depth,
            "intensive_mode": intensive_mode,
            "extensive_language_support": extensive_language_support,
            "crib": crib_str
        }
    }
    return create_api_request(endpoint="magic", request_data=request_data)


def main():
    """Initialize and run the MCP server (listens on :8000, forwards to backend)"""
    log.info("Starting the CyberChef MCP server")
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
