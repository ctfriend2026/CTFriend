"""Synchronous adapter for LangChain MCP tools.

LangChain agents in this app call tools synchronously, while MCP tool adapters
are async. These wrappers bridge that difference and cache discovered tools.
"""

import asyncio
import logging
from typing import Dict
from langchain.tools import StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(name=__name__)


class SyncToolWrapper(StructuredTool):
    """
    Wraps an async StructuredTool so it can be invoked synchronously.
    """

    def __init__(self, tool: StructuredTool) -> None:
        super().__init__(
            name=tool.name,
            description=tool.description,
            args_schema=tool.args_schema,
            func=self._sync_func,
        )
        self._tool = tool

    def _sync_func(self, **kwargs):
        """
        Runs the async tool's ainvoke with the full kwargs dict.
        Adds robust error handling so errors don't crash the chat.
        """
        try:
            # Bridge the async MCP tool call into LangChain's sync StructuredTool API.
            return asyncio.run(main=self._tool.ainvoke(input=kwargs))
        except Exception as e:
            logger.exception(msg=f"Error running tool {self.name}: {e}")
            return {"error": f"❌ Tool `{self.name}` failed with error: {str(e)}"}


class MultiServerMCPClientSync:
    """
    A synchronous wrapper around MultiServerMCPClient.
    """

    def __init__(self, server_config: Dict[str, Dict[str, str]]) -> None:
        self._client = MultiServerMCPClient(connections=server_config)
        self._tools = None  # cache wrapped tools

    def get_tools(self) -> list[SyncToolWrapper]:
        """Return a list of StructuredTools, all wrapped as sync tools."""
        if self._tools is None:
            # Tool discovery can hit remote MCP servers, so cache the wrapped list.
            async_tools = asyncio.run(main=self._client.get_tools())
            self._tools = [SyncToolWrapper(tool=t) for t in async_tools]
        return self._tools

    def call_tool(self, tool_name: str, **kwargs):
        """Invoke one of the wrapped tools synchronously."""
        tools = {t.name: t for t in self.get_tools()}
        if tool_name not in tools:
            raise ValueError(
                f"Tool '{tool_name}' not found. Available: {list(tools.keys())}"
            )
        return tools[tool_name].func(**kwargs)

    def list_tools(self) -> list[str]:
        """Return a list of available tool names synchronously."""
        return [t.name for t in self.get_tools()]
