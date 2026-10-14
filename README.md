# AgentCore MCP server, checking the examples actually run

I went through the AgentCore "MCP servers" training and ran its code rather than
just reading it, both locally and by deploying a server to a real runtime. This
repo has the scripts I used and what came back.

## What held up

- The stateless server (`servers/mcp_server_stateless.py`) starts on 0.0.0.0:8000
  and serves `/mcp` (HTTP 200 for tools/list).
- The stateful server (`servers/travel_server_stateful.py`) starts with
  `stateless_http=False`; a cold tools/list returns 400 until you initialise a
  session, which is the expected stateful behaviour.
- Deploying with `agentcore create --protocol MCP` then `agentcore deploy`, then
  invoking with the SigV4 client (`clients/remote_client_sigv4.py`), worked end to
  end: it initialised a session and `tools/list` returned the tool.
- Port 8000, the `/mcp` path, the tools/prompts/resources methods, the JSON-RPC
  request/response shapes and the knowledge-check answers all match.

## Two things to fix

1. The local test client URLs need the `http://` scheme. The rendered course used
   `"localhost:8000/mcp"` with no scheme. Run as written the stateless client dies
   with `httpx.UnsupportedProtocol` and the stateful transport with
   `ValueError: Invalid HTTP/S URL`. Add `http://` and both work.
   `clients/scheme_bug_demo.py` reproduces it both ways. This only hits the local
   clients, the deployed SigV4 client builds its own `https://` URL and is fine.

2. The dependency pins are open-ended (`mcp >= 1.19.0`, `fastmcp >= 2.10.0`). The
   current `mcp` 2.x renamed `FastMCP`, so `from mcp.server.fastmcp import FastMCP`
   no longer resolves and the stateless sample breaks on import if you install the
   latest. The code is right for the versions it was written for; it just wants an
   upper bound (`mcp >= 1.19.0, < 2`, `fastmcp >= 2.10.0, < 3`).

## Running it

Install the SDKs for the era the code targets (mcp 1.x, fastmcp 2.x):

    uv run --with 'mcp>=1.19.0,<2' python servers/mcp_server_stateless.py
    uv run --with 'mcp>=1.19.0,<2' --with 'fastmcp>=2.10.0,<3' python clients/scheme_bug_demo.py

For the remote client, set AGENT_ARN to your deployed runtime and use real AWS
credentials. No account IDs are committed, the ARN in the samples is a placeholder.

## References

- Deploy MCP servers in AgentCore Runtime: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html
- Stateful MCP server features: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/mcp-stateful-features.html
- MCP protocol contract (session handling): https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp-protocol-contract.html
- MCP specification: https://modelcontextprotocol.io/specification/2025-11-25
