#!/usr/bin/env python3

from typing import Any, Callable, Optional, Type, Awaitable
from pydantic import BaseModel, ConfigDict, create_model
from llama_index.core.tools import AsyncBaseTool, ToolMetadata, ToolOutput
from llama_index.core.async_utils import asyncio_run

# from llama_index.core.tools.function_tool import create_schema_from_function
import inspect
from pydantic.fields import FieldInfo

from mcp.types import Tool
from mcp import ClientSession

AsyncCallable = Callable[..., Awaitable[Any]]


def async_to_sync(func_async: AsyncCallable) -> Callable:
    """Async from sync."""

    def _sync_wrapped_fn(*args: Any, **kwargs: Any) -> Any:
        return asyncio_run(func_async(*args, **kwargs))  # type: ignore[arg-type]

    return _sync_wrapped_fn


class McpTool(AsyncBaseTool):
    """McpTool is a tool that wraps a Tool object and provides a callable interface."""

    def __init__(
        self,
        tool: Tool,
        session: ClientSession,
    ) -> None:
        """Initialize McpTool with a Tool object.

        Args:
            tool (Tool): The Tool object to wrap.
            fn (Optional[Callable[..., Any]]): A synchronous function to call.
            async_fn (Optional[Callable[..., Any]]): An asynchronous function to call.
        """
        self._session = session
        self._tool = tool
        # Create ToolMetadata from the Tool object
        self._metadata = ToolMetadata(
            name=tool.name,
            description=tool.description or "",
            fn_schema=create_model(tool.name, **tool.inputSchema),
            return_direct=False,  # Adjust as needed
        )
        # self._fn = async_to_sync(self.async_fn)

    @property
    def metadata(self) -> ToolMetadata:
        """Metadata."""
        return self._metadata

    @property
    def tool(self) -> Tool:
        """Tool."""
        return self._tool

    def call(self, *args: Any, **kwargs: Any) -> ToolOutput:
        """Call the tool synchronously."""
        return async_to_sync(self.acall)(*args, **kwargs)

    async def acall(self, *args: Any, **kwargs: Any) -> ToolOutput:
        """Call the tool asynchronously."""
        tool_output = await self._session.call_tool(
            self._tool.name, arguments=args, **kwargs
        )
        return ToolOutput(
            content=str(tool_output),
            tool_name=self._tool.name,
            raw_input={"args": args, "kwargs": kwargs},
            raw_output=tool_output,
        )
