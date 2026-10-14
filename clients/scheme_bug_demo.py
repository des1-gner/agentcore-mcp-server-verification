#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp>=1.19.0,<2", "fastmcp>=2.10.0,<3"]
# ///
"""Show why the local test client URLs need the http:// scheme.

The training's rendered local clients used "localhost:8000/mcp" (no scheme).
Run as written they fail; adding http:// fixes them. This reproduces both.
Start servers/mcp_server_stateless.py first (it listens on :8000).
"""
import asyncio

def stateless(url):
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    async def go():
        async with streamablehttp_client(url, {}, timeout=15, terminate_on_close=False) as (r, w, _):
            async with ClientSession(r, w) as s:
                await s.initialize()
                return (await s.list_tools()).tools[0].name
    return asyncio.run(go())

def stateful_transport(url):
    from fastmcp.client.transports import StreamableHttpTransport
    StreamableHttpTransport(url=url, headers={})
    return "constructed"

for label, fn in (("stateless client", stateless), ("stateful transport", stateful_transport)):
    for url in ("localhost:8000/mcp", "http://localhost:8000/mcp"):
        try:
            r = fn(url)
            print(f"{label:20} {url:28} -> OK ({r})")
        except Exception as e:
            print(f"{label:20} {url:28} -> {type(e).__name__}: {str(e)[:70]}")
