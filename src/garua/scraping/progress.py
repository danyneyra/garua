"""Scraping status events independent of MCP and console output."""

from collections.abc import Awaitable, Callable

ProgressCallback = Callable[[str], Awaitable[None]]


async def emit_progress(callback: ProgressCallback | None, message: str) -> None:
    if callback is not None:
        await callback(message)
