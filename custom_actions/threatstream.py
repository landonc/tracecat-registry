from typing import Annotated
from pydantic import Field
from tracecat_registry import registry, RegistrySecret, secrets
import httpx

BASE_URL = "https://api.threatstream.com/api/v2"

registry_secret = RegistrySecret(name="threatstream", keys=["USERNAME","API_KEY"])

@registry.register(
    default_title="Lookup File Hash",
    display_group="Anomali ThreatStream",
    description="Search Anomali ThreatStream for a file hash",
    namespace="tools.threatstreampy",
    secrets=[registry_secret]
)
def lookup_file_hash(file_hash: Annotated[str, Field(description="The file hash to check")]):
    try:        
        params = {
            "value": file_hash,
            "type": "md5",
            "status": "active",
            "limit": 0
        }
        return indicator_lookup(secrets=secrets, params=params)        
    except Exception as ex:
        raise Exception(f"Error retriving results: {ex}")


async def indicator_lookup(secrets: dict, params: dict):    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url = f"{BASE_URL}/intelligence/",
            headers = {
                "Authorization": f"apikey {secrets.get("USERNAME")}:{secrets.get("API_KEY")}",
                "Accept": "application/json"
            },
            params = params
        )
        response.raise_for_status()
        return response.json()