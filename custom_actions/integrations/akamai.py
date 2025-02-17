"""Generic interface to Akamai using EdgeGridAuth"""

from typing import Annotated, Any
from pydantic import Field
from tracecat_registry import RegistrySecret, registry, secrets
# import httpx
from akamai.edgegrid import EdgeGridAuth

import requests
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


def akamai_request(
    auth: dict[str, Any] | tuple | None,
    method: str,
    url: str,
    params: dict[str, Any] | None,
    data: dict[str, Any] | None,
    timeout: int | None
) -> dict[str, Any]:
    params = params or {}
    timeout = timeout or 60

    client = requests.Session()
    client.auth = auth
    response = client.request(
        method=method,
        url=url,
        headers={
            "Content-Type": "application/json",
            "Accept":  "application/json"
        },
        params=params,
        data=data,
        timeout=timeout
    )

    return response.json()


@registry.register(
    default_title="Call endpoint",
    description="Authenticate with Akamai EdgeGridAuth and call an API endpoint.",
    display_group="Akamai",
    doc_url="https://techdocs.akamai.com/developer/docs/python",
    namespace="tools.akamai",
    secrets=[akamai_secret],
)
# non-async for requests
def call_endpoint(
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

    response = akamai_request(
        auth=EdgeGridAuth(
            client_token=secrets.get("AKAMAI_CLIENT_TOKEN"),
            client_secret=secrets.get("AKAMAI_CLIENT_SECRET"),
            access_token=secrets.get("AKAMAI_ACCESS_TOKEN")
        ),
        method=method,
        url=url,
        params=params,
        data=data,
        timeout=timeout
    )

    return response.json()

# akamai.edgegrid throws errors, seems likely due to it registering a hook in the requests session at
# https://github.com/akamai/AkamaiOPEN-edgegrid-python/blob/036f057f317445b50852b1d57d695835150dfdd1/akamai/edgegrid/edgegrid.py#L199C9-L199C58

# async for httpx
# async def call_endpoint(
#     method: Annotated[
#         str,
#         Field(...,
#               description="HTTP request method"
#               ),
#     ],
#     endpoint: Annotated[
#         str,
#         Field(..., description="API endpoint")
#     ],
#     params: Annotated[
#         dict[str, Any] | None,
#         Field(..., description="Parameters to pass with the request")
#     ],
#     data: Annotated[
#         dict[str, Any] | None,
#         Field(..., description="Data to pass with the request")
#     ],
#     timeout: Annotated[
#         int | None,
#         Field(..., description="Timeout for the request. Default is 60 seconds.")
#     ]
# ) -> dict[str, Any]:
#     params = params or {}
#     timeout = timeout or 60
#     url = urljoin(secrets.get("AKAMAI_BASE_URL"), endpoint)

#     async with httpx.AsyncClient() as client:
#         client.auth = EdgeGridAuth(
#             client_token=secrets.get("AKAMAI_CLIENT_TOKEN"),
#             client_secret=secrets.get("AKAMAI_CLIENT_SECRET"),
#             access_token=secrets.get("AKAMAI_ACCESS_TOKEN")
#         )
#         client.base_url = secrets.get("AKAMAI_BASE_URL")
#         req = client.build_request(
#             method=method,
#             url=endpoint,
#             headers={
#                 "Content-Type": "application/json",
#                 "Accept":  "application/json"
#             },
#             params=params,
#             data=data,
#             timeout=timeout
#         )
#         response = await client.send(req)
#         response.raise_for_status()
#         return response.json()


@registry.register(
    default_title="List network lists",
    description="List all network lists that are visible for the authenticated user.",
    display_group="Akamai",
    doc_url="https://techdocs.akamai.com/developer/docs/python",
    namespace="tools.akamai",
    secrets=[akamai_secret],
)
def list_network_lists(
    include_elements: Annotated[
        bool | None,
        Field(...,
              description="If enabled, the response list includes all items. For large network lists, this may slow responses and yield large response objects. The default false value when listing more than one network list omits the network list's elements and only provides higher-level metadata."
              ),
    ],
    search: Annotated[
        str | None,
        Field(...,
              description="Only list items that match the specified substring in any network list's name or list of items."
              ),
    ],
    list_type: Annotated[
        str: None,
        Field(..., description="Filters the output to lists of only the given type of network lists if provided, either *IP* or *GEO*. This corresponds to the network list object's type member.")
    ],
    extended: Annotated[
        bool | None,
        Field(..., description="When enabled, provides additional response data identifying who created and updated the list and when, and the network list's deployment status in both STAGING and PRODUCTION environments. This data takes longer to provide.")
    ]
):
    params = {}
    if include_elements:
        params.update({"includeElements": include_elements})
    if search:
        params.update({"search": search})
    if list_type:
        params.update({"listType": list_type})
    if extended:
        params.update({"extended": extended})

    return akamai_request(
        auth=EdgeGridAuth(
            client_token=secrets.get("AKAMAI_CLIENT_TOKEN"),
            client_secret=secrets.get("AKAMAI_CLIENT_SECRET"),
            access_token=secrets.get("AKAMAI_ACCESS_TOKEN")
        ),
        method="GET",
        endpoint="/network-list/v2/network-lists",
        params=params
    )
