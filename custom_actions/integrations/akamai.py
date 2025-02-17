"""Generic interface to Akamai using EdgeGridAuth"""

from typing import Annotated, Any
from pydantic import Field
from tracecat_registry import RegistrySecret, registry, secrets
import httpx
from akamai.edgegrid import EdgeGridAuth
from urllib.parse import urljoin

ALLOWED_METHODS = ["GET", "POST", "PATCH", "DELETE", "PUT", "HEAD"]

akamai_secret = RegistrySecret(
    name="akamai",
    keys=["AKAMAI_BASE_URL", "AKAMAI_CLIENT_TOKEN",
          "AKAMAI_CLIENT_SECRET", "AKAMAI_ACCESS_TOKEN"]
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
        Field(..., description="API endpoint")
    ],
    params: Annotated[
        dict[str, Any] | None,
        Field(..., description="Parameters to pass with the request")
    ],
    data: Annotated[
        dict[str, Any] | None,
        Field(..., description="Data to pass with the request")
    ],
    timeout: Annotated[
        int | None,
        Field(..., description="Timeout for the request. Default is 60 seconds.")
    ]
) -> dict[str, Any]:
    params = params or {}
    timeout = timeout or 60
    url = urljoin(secrets.get("AKAMAI_BASE_URL"), endpoint)
    async with httpx.AsyncClient() as client:
        client.auth = EdgeGridAuth(
            client_token=secrets.get("AKAMAI_CLIENT_TOKEN"),
            client_secret=secrets.get("AKAMAI_CLIENT_SECRET"),
            access_token=secrets.get("AKAMAI_ACCESS_TOKEN")
        )
        request = client.build_request(
            method=method,
            url=url,
            headers={
                "Content-Type": "application/json",
                "Accept":  "applicaiton/json"
            },
            params=params,
            data=data,
            timeout=timeout
        )
        response = await client.send(request)

    return response.json()
