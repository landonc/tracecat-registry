"""Generic interface to Akamai using EdgeGridAuth"""

from typing import Annotated, Any
from pydantic import Field
from tracecat_registry import RegistrySecret, registry, secrets
import httpx
from akamai.edgegrid import EdgeGridAuth

akamai_secret = RegistrySecret(
    name="akamai",
    keys=["AKAMAI_BASE_URL", "AKAMAI_CLIENT_TOKEN", "AKAMAI_CLIENT_SECRET", "AKAMAI_ACCESS_TOKEN"]
)
"""Akamai EdgeGridAuth credentials

- name: `akamai`
- keys:
    - `AKAMAI_BASE_URL`
    - `AKAMAI_CLIENT_TOKEN`
    - `AKAMAI_CLIENT_SECRET`
    - `AKAMAI_ACCESS_TOKEN`
"""

@registry.register(
    default_title="Call endpoint",
    description="Authenticate with Akamai EdgeGridAuth and call an API endpoint.",
    display_group="Akamai",
    doc_url="https://techdocs.akamai.com/developer/docs/python",
    namespace="tools.akamai",
    secrets=[akamai_secret],
)
async def call_endpoint(
    method: Annotated[
        str,
        Field(...,
              description="HTTP request method"
        ),
    ],
    endpoint: Annotated[
        str,
        Field(...,description="API endpoint")
    ],
    params: Annotated[
        dict[str, Any] | None,
        Field(...,description="Parameters to pass with the request")
    ]
) -> dict[str, Any]:
    params = params or {}

    async with httpx.AsyncClient() as client:
        
        client.auth = EdgeGridAuth(
            client_token = secrets.get("AKAMAI_CLIENT_TOKEN"),
            client_secret = secrets.get("AKAMAI_CLIENT_SECRET"),
            access_token = secrets.get("AKAMAI_ACCESS_TOKEN")
        )
        client.headers = {
            "Content-Type": "application/json",
            "Accept":  "applicaiton/json"
        }
        request = client.request(method=method)
        response = await client.send(request=request)
    
    return response.json()
