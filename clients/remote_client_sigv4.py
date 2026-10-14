import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Generator
from datetime import timedelta

import httpx
from boto3.session import Session
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials


class SigV4HTTPXAuth(httpx.Auth):
    def __init__(self, credentials: Credentials, service: str, region: str):
        self.credentials = credentials
        self.service = service
        self.region = region
        self.signer = SigV4Auth(credentials, service, region)

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        headers = dict(request.headers)
        headers.pop("connection", None)
        aws_request = AWSRequest(method=request.method, url=str(request.url), data=request.content, headers=headers)
        self.signer.add_auth(aws_request)
        request.headers.update(dict(aws_request.headers))
        yield request


@asynccontextmanager
async def streamablehttp_client_with_sigv4(url, credentials, service, region, timeout=120):
    async with streamablehttp_client(url=url, timeout=timeout, terminate_on_close=False, auth=SigV4HTTPXAuth(credentials, service, region)) as result:
        yield result


async def main():
    agent_arn = os.getenv('AGENT_ARN')
    if not agent_arn:
        print("Error: AGENT_ARN environment variable is not set"); sys.exit(1)
    boto_session = Session()
    region = boto_session.region_name or "us-west-2"
    credentials = boto_session.get_credentials()
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    mcp_url = (f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT")
    print(f"Connecting to: {mcp_url}")
    async with streamablehttp_client_with_sigv4(url=mcp_url, credentials=credentials, service="bedrock-agentcore", region=region) as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print(f"Session ID: {get_session_id()}")
            tool_result = await session.list_tools()
            print(f"Tools: {[t.name for t in tool_result.tools]}")

asyncio.run(main())
