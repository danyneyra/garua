"""Native MCP results with a text fallback for structured output."""

import json
from typing import Any

from fastmcp.tools import ToolResult
from mcp.types import TextContent, EmbeddedResource, TextResourceContents
from garua import settings
from garua.services.file_delivery import read_inline_resource


def build_tool_result(
    *, content: Any, structured_content: Any, is_error: bool = False
) -> ToolResult:
    """Keep the same payload available to clients reading only content.

    Normalize through FastMCP first so Pydantic models, dates and file URIs
    have exactly the same JSON representation in both output channels.
    """
    result = ToolResult(
        content=content, structured_content=structured_content, is_error=is_error
    )
    remaining = settings.MCP_INLINE_TOTAL_MAX_BYTES
    seen: set[str] = set()
    attachments = []
    for block in result.content:
        if block.type != "resource_link" or block.uri in seen:
            continue
        seen.add(block.uri)
        text = read_inline_resource(
            block.uri, min(settings.MCP_INLINE_FILE_MAX_BYTES, remaining)
        )
        if text is not None:
            remaining -= len(text.encode(settings.CSV_ENCODING))
            attachments.append(
                EmbeddedResource(
                    type="resource",
                    resource=TextResourceContents(
                        uri=block.uri, mime_type="text/csv", text=text
                    ),
                )
            )
    result.content.extend(attachments)
    if result.structured_content is not None:
        payload = dict(result.structured_content)
        messages = [block.text for block in result.content if block.type == "text"]
        if messages and "message" not in payload:
            payload["message"] = "\n\n".join(messages)
        result.structured_content = payload
        # Replace summary blocks with a single complete JSON block. Keep native
        # links and any other non-text content in their original order.
        result.content = [block for block in result.content if block.type != "text"]
        result.content.append(
            TextContent(
                type="text",
                text=json.dumps(result.structured_content, ensure_ascii=False),
            )
        )
    return result
