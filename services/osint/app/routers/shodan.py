from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import httpx

router = APIRouter()

# Shodan API configuration
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")
SHODAN_BASE_URL = "https://api.shodan.io"

class HostInfo(BaseModel):
    ip: str
    hostnames: List[str] = []
    ports: List[int] = []
    vulns: List[str] = []
    org: Optional[str] = None
    isp: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    last_update: Optional[str] = None
    data: List[Dict[str, Any]] = []

class SearchResult(BaseModel):
    total: int
    matches: List[Dict[str, Any]]

class ExploitResult(BaseModel):
    total: int
    exploits: List[Dict[str, Any]]

@router.get("/host/{ip}", response_model=HostInfo)
async def get_host_info(ip: str):
    """Get detailed information about a specific IP address from Shodan"""
    
    if not SHODAN_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Shodan API key not configured. Set SHODAN_API_KEY environment variable."
        )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SHODAN_BASE_URL}/shodan/host/{ip}",
                params={"key": SHODAN_API_KEY}
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Host not found in Shodan database")
            
            response.raise_for_status()
            data = response.json()
            
            return HostInfo(
                ip=data.get("ip_str", ip),
                hostnames=data.get("hostnames", []),
                ports=data.get("ports", []),
                vulns=list(data.get("vulns", {}).keys()) if data.get("vulns") else [],
                org=data.get("org"),
                isp=data.get("isp"),
                country=data.get("country_name"),
                city=data.get("city"),
                last_update=data.get("last_update"),
                data=data.get("data", [])[:5]  # Limit to first 5 service entries
            )
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=SearchResult)
async def search_shodan(
    query: str = Query(..., description="Shodan search query"),
    page: int = Query(1, ge=1, description="Page number")
):
    """Search Shodan database with a query string"""
    
    if not SHODAN_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Shodan API key not configured"
        )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SHODAN_BASE_URL}/shodan/host/search",
                params={
                    "key": SHODAN_API_KEY,
                    "query": query,
                    "page": page
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return SearchResult(
                total=data.get("total", 0),
                matches=[
                    {
                        "ip": m.get("ip_str"),
                        "port": m.get("port"),
                        "org": m.get("org"),
                        "product": m.get("product"),
                        "version": m.get("version"),
                        "country": m.get("location", {}).get("country_name")
                    }
                    for m in data.get("matches", [])[:20]
                ]
            )
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/exploits", response_model=ExploitResult)
async def search_exploits(
    query: str = Query(..., description="Search term for exploits (e.g., 'apache', 'CVE-2021')")
):
    """Search for known exploits in Shodan's exploit database"""
    
    if not SHODAN_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Shodan API key not configured"
        )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SHODAN_BASE_URL}/api-info",
                params={"key": SHODAN_API_KEY}
            )
            
            # Use exploits API
            response = await client.get(
                "https://exploits.shodan.io/api/search",
                params={
                    "key": SHODAN_API_KEY,
                    "query": query
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return ExploitResult(
                total=data.get("total", 0),
                exploits=[
                    {
                        "id": e.get("_id"),
                        "description": e.get("description", "")[:200],
                        "source": e.get("source"),
                        "type": e.get("type"),
                        "platform": e.get("platform"),
                        "cve": e.get("cve", [])
                    }
                    for e in data.get("matches", [])[:20]
                ]
            )
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/dns/{domain}")
async def dns_lookup(domain: str):
    """Get DNS information for a domain from Shodan"""
    
    if not SHODAN_API_KEY:
        raise HTTPException(status_code=500, detail="Shodan API key not configured")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SHODAN_BASE_URL}/dns/resolve",
                params={
                    "key": SHODAN_API_KEY,
                    "hostnames": domain
                }
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/api-info")
async def get_api_info():
    """Get Shodan API subscription info and query credits remaining"""
    
    if not SHODAN_API_KEY:
        return {"status": "not_configured", "message": "Set SHODAN_API_KEY environment variable"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SHODAN_BASE_URL}/api-info",
                params={"key": SHODAN_API_KEY}
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "status": "configured",
                "plan": data.get("plan"),
                "query_credits": data.get("query_credits"),
                "scan_credits": data.get("scan_credits")
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
