"""
API Gateway - Main entry point for all microservices
Routes requests to appropriate backend services
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoPivot - API Gateway",
    description="Central API Gateway routing to microservices",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    "listing": "http://listing-service:8001",
    "advantage": "http://advantage-engine:8002",
    "logistics": "http://logistics-service:8003",
    "chat": "http://chat-service:8004",
    "user": "http://user-service:8005",
    "verification": "http://verification-service:8006",
    "payment": "http://payment-service:8007",
}

@app.get("/health")
async def health_check():
    """API Gateway health check"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/status")
async def service_status():
    """Check all downstream services"""
    status = {}
    
    async with httpx.AsyncClient(timeout=5) as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health")
                status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_code": response.status_code
                }
            except Exception as e:
                status[service_name] = {
                    "status": "unreachable",
                    "error": str(e)
                }
    
    return {"services": status}

# ============================================================================
# ROUTING PROXY
# ============================================================================

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PATCH", "DELETE", "PUT"])
async def proxy(path: str, request: Request):
    """
    Universal proxy router to all microservices
    Determines which service based on path
    """
    try:
        # Determine target service
        if path.startswith("listings"):
            target_service = SERVICES["listing"]
        elif path.startswith("advantage"):
            target_service = SERVICES["advantage"]
        elif path.startswith("logistics"):
            target_service = SERVICES["logistics"]
        elif path.startswith("chat"):
            target_service = SERVICES["chat"]
        elif path.startswith("auth") or path.startswith("users"):
            target_service = SERVICES["user"]
        elif path.startswith("mechanics") or path.startswith("verification"):
            target_service = SERVICES["verification"]
        elif path.startswith("transactions") or path.startswith("escrow") or path.startswith("payments"):
            target_service = SERVICES["payment"]
        else:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Forward request
        url = f"{target_service}/api/{path}"
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=await request.body()
            )
            
            return JSONResponse(
                status_code=response.status_code,
                content=response.json() if response.text else {}
            )
    
    except httpx.ConnectError:
        logger.error(f"Connection error to service: {target_service}")
        return JSONResponse(
            status_code=503,
            content={"error": "Service unavailable"}
        )
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
