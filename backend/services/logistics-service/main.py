"""
Logistics Service - Route Planning & Delivery Quotes
Calculates delivery costs, estimates, and logistics options for Uganda
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
import math

from backend.shared.schemas import (
    BaseResponse, Location, LogisticsQuoteResponse, RoadCondition, DeliveryMethod
)

logger = logging.getLogger(__name__)

# ============================================================================
# LOGISTICS CALCULATION ENGINE
# ============================================================================

class LogisticsCalculator:
    """Calculate delivery quotes for Uganda"""
    
    # Base price per km (varies by road condition)
    BASE_PRICE_PER_KM = 1500  # UGX per km
    
    # Fuel surcharge (UGX per liter, current Uganda rate)
    FUEL_PRICE_PER_LITER = 3500
    
    # Vehicle fuel consumption (L/100km)
    VEHICLE_FUEL_CONSUMPTION = 8.5
    
    # Region fuel surcharges
    REGIONAL_SURCHARGE = {
        "Kampala": 0.0,
        "Mbarara": 0.10,
        "Gulu": 0.20,
        "Fort Portal": 0.15,
        "Jinja": 0.05,
        "Mbale": 0.15,
    }
    
    # Road condition multipliers
    ROAD_CONDITION_MULTIPLIER = {
        "excellent": 1.0,
        "good": 1.1,
        "fair": 1.25,
        "poor": 1.5,
    }
    
    @staticmethod
    def estimate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate approximate distance using Haversine formula (km)"""
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    def estimate_road_condition(distance_km: float) -> str:
        """Estimate road condition based on distance"""
        if distance_km < 50:
            return "good"
        elif distance_km < 150:
            return "good"
        elif distance_km < 300:
            return "fair"
        else:
            return "fair"
    
    @staticmethod
    def calculate_quote(
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float,
        vehicle_type: str = "car"
    ) -> dict:
        """Calculate logistics quote"""
        
        # Calculate distance
        distance_km = LogisticsCalculator.estimate_distance(
            origin_lat, origin_lng,
            destination_lat, destination_lng
        )
        
        # Estimate duration (40 km/hour average in Uganda)
        estimated_duration_hours = distance_km / 40
        
        # Estimate road condition
        road_condition_str = LogisticsCalculator.estimate_road_condition(distance_km)
        
        # Base price calculation
        base_price = distance_km * LogisticsCalculator.BASE_PRICE_PER_KM
        
        # Fuel surcharge
        fuel_needed = (distance_km / 100) * LogisticsCalculator.VEHICLE_FUEL_CONSUMPTION
        fuel_surcharge = fuel_needed * LogisticsCalculator.FUEL_PRICE_PER_LITER
        
        # Distance surcharge (for long distances)
        distance_surcharge = 0
        if distance_km > 200:
            distance_surcharge = (distance_km - 200) * 500
        
        # Road condition surcharge
        road_multiplier = LogisticsCalculator.ROAD_CONDITION_MULTIPLIER.get(road_condition_str, 1.1)
        road_condition_surcharge = base_price * (road_multiplier - 1)
        
        # Total price
        total_price = base_price + fuel_surcharge + distance_surcharge + road_condition_surcharge
        
        # Toll estimate (major highways)
        toll_amount = 50000 if distance_km > 150 else 0
        
        # Delivery methods available
        delivery_methods = [
            DeliveryMethod.TOW_TRUCK,
            DeliveryMethod.DRIVE_DELIVERY,
        ]
        if distance_km < 50:
            delivery_methods.append(DeliveryMethod.FLATBED)
        
        return {
            "distance_km": round(distance_km, 1),
            "estimated_duration_hours": round(estimated_duration_hours, 1),
            "base_price": int(base_price),
            "fuel_surcharge": int(fuel_surcharge),
            "distance_surcharge": int(distance_surcharge),
            "road_condition_surcharge": int(road_condition_surcharge),
            "toll_amount": int(toll_amount),
            "total_price": int(total_price + toll_amount),
            "delivery_methods": delivery_methods,
            "road_condition": road_condition_str,
            "current_fuel_price_per_liter": LogisticsCalculator.FUEL_PRICE_PER_LITER,
            "valid_until": (datetime.utcnow() + timedelta(hours=2)).isoformat()
        }

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    logger.info("🚀 Logistics Service starting...")
    yield
    logger.info("🛑 Logistics Service shutting down...")

app = FastAPI(
    title="AutoPivot - Logistics Service",
    description="Route planning and delivery quote calculation",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "logistics-service",
        "version": "0.1.0",
        "current_fuel_price_per_liter": 3500
    }

@app.post("/api/v1/logistics/quote")
async def get_logistics_quote(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
    vehicle_type: str = "car"
):
    """Get delivery quote between two locations"""
    logger.info(f"Calculating logistics quote: {origin_lat},{origin_lng} -> {destination_lat},{destination_lng}")
    
    quote_data = LogisticsCalculator.calculate_quote(
        origin_lat, origin_lng,
        destination_lat, destination_lng,
        vehicle_type
    )
    
    return BaseResponse(
        success=True,
        data=quote_data,
        meta={"message": "Logistics quote calculated"}
    )

@app.get("/api/v1/logistics/fuel-price")
async def get_current_fuel_price():
    """Get current fuel prices in Uganda"""
    return BaseResponse(
        success=True,
        data={
            "petrol_per_liter_ugx": 3500,
            "diesel_per_liter_ugx": 3400,
            "currency": "UGX",
            "last_updated": datetime.utcnow().isoformat()
        },
        meta={"message": "Current fuel prices"}
    )
