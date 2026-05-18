"""
Logistics Service - Distance, routing, and delivery pricing
"""
from datetime import datetime
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import logging

from backend.shared.schemas import (
    BaseResponse,
    LogisticsQuoteRequest,
    LogisticsQuoteResponse,
    RoadCondition,
    DeliveryMethod,
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Logistics Service starting...")
    yield
    logger.info("🛑 Logistics Service shutting down...")

app = FastAPI(
    title="AutoPivot - Logistics Service",
    description="Delivery quotes and route optimization",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "logistics-service"}

def haversine_distance(origin, destination) -> float:
    from math import radians, cos, sin, asin, sqrt

    lat1, lon1 = origin
    lat2, lon2 = destination

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    radius_km = 6371
    return round(radius_km * c, 2)


def estimate_duration(distance_km: float, vehicle_type: str) -> float:
    base_speed = 50 if vehicle_type == "suv" else 55
    duration = distance_km / base_speed
    return round(duration, 2)


def compute_quote(distance_km: float, vehicle_type: str) -> LogisticsQuoteResponse:
    fuel_price = 3850
    base_rate = 1500 if vehicle_type == "suv" else 1200
    base_price = max(200000, distance_km * base_rate)
    fuel_surcharge = round((distance_km / 10) * fuel_price)
    distance_surcharge = round(distance_km * 50)
    total_price = base_price + fuel_surcharge + distance_surcharge

    if distance_km < 50:
        methods = [DeliveryMethod.DRIVE_DELIVERY]
        road_condition = RoadCondition.GOOD
    elif distance_km < 200:
        methods = [DeliveryMethod.DRIVE_DELIVERY, DeliveryMethod.TOW_TRUCK]
        road_condition = RoadCondition.FAIR
    else:
        methods = [DeliveryMethod.TOW_TRUCK, DeliveryMethod.FLATBED]
        road_condition = RoadCondition.FAIR

    return LogisticsQuoteResponse(
        distance_km=distance_km,
        estimated_duration_hours=estimate_duration(distance_km, vehicle_type),
        base_price=base_price,
        fuel_surcharge=fuel_surcharge,
        distance_surcharge=distance_surcharge,
        total_price=total_price,
        delivery_methods=methods,
        road_condition=road_condition,
        current_fuel_price_per_liter=fuel_price,
        valid_until=datetime.utcnow().isoformat(),
    )

@app.post("/api/v1/logistics/quote", response_model=BaseResponse)
async def get_logistics_quote(request: LogisticsQuoteRequest):
    logger.info(
        f"Generating logistics quote from {request.origin.latitude},{request.origin.longitude} "
        f"to {request.destination.latitude},{request.destination.longitude}"
    )

    try:
        distance_km = haversine_distance(
            (request.origin.latitude, request.origin.longitude),
            (request.destination.latitude, request.destination.longitude),
        )

        quote = compute_quote(distance_km, request.vehicle_type)

        return BaseResponse(
            success=True,
            data={"quote": quote.model_dump()},
        )
    except Exception as exc:
        logger.error(f"Error generating logistics quote: {exc}")
        raise HTTPException(status_code=500, detail="Failed to generate logistics quote")

@app.get("/api/v1/logistics/routes", response_model=BaseResponse)
async def get_popular_routes():
    logger.info("Fetching popular logistics routes")
    return BaseResponse(
        success=True,
        data={
            "routes": [
                {"from": "Kampala", "to": "Mbarara", "distance_km": 245, "avg_price": 500000, "frequency": "high"},
                {"from": "Gulu", "to": "Kampala", "distance_km": 330, "avg_price": 650000, "frequency": "high"},
            ]
        },
    )

@app.get("/api/v1/logistics/fuel-prices", response_model=BaseResponse)
async def get_current_fuel_prices():
    logger.info("Fetching current fuel prices")
    return BaseResponse(
        success=True,
        data={
            "petrol_price_per_liter": 3850,
            "diesel_price_per_liter": 3600,
            "last_updated": datetime.utcnow().isoformat(),
            "trend_24h": "stable",
            "trend_7d": "up_2%",
        },
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
