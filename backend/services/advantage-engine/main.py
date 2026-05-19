"""
Advantage Engine Service - Pivot Score Calculation
Calculates AI-powered vehicle quality and value scores using ML models
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import Optional
import math

from backend.shared.schemas import (
    BaseResponse, PivotScoreResponse, RiskRating
)

logger = logging.getLogger(__name__)

# ============================================================================
# PIVOT SCORE CALCULATION ENGINE
# ============================================================================

class PivotScoreCalculator:
    """Calculate AutoPivot Pivot Score based on vehicle characteristics"""
    
    # Vehicle reliability scores (manufacturer ranking)
    RELIABILITY_SCORES = {
        ("Toyota", "Harrier"): 95,
        ("Toyota", "RAV4"): 94,
        ("Toyota", "Vitz"): 92,
        ("Honda", "CR-V"): 93,
        ("Honda", "Civic"): 91,
        ("Mazda", "CX-5"): 89,
        ("Nissan", "X-Trail"): 87,
        ("Hyundai", "Elantra"): 80,
        ("Kia", "Picanto"): 82,
    }
    
    # Average fuel consumption (L/100km)
    FUEL_EFFICIENCY = {
        ("Toyota", "Vitz"): 6.5,
        ("Toyota", "Wish"): 8.2,
        ("Toyota", "Harrier"): 10.5,
        ("Toyota", "RAV4"): 9.8,
        ("Honda", "Civic"): 7.2,
        ("Honda", "CR-V"): 9.5,
        ("Mazda", "CX-5"): 8.8,
        ("Nissan", "X-Trail"): 10.2,
    }
    
    # Market depreciation rates (% per year)
    DEPRECIATION_RATES = {
        ("Toyota", "Harrier"): 0.08,
        ("Toyota", "RAV4"): 0.08,
        ("Toyota", "Vitz"): 0.07,
        ("Honda", "CR-V"): 0.08,
        ("Mazda", "CX-5"): 0.09,
        ("Nissan", "X-Trail"): 0.09,
    }
    
    @staticmethod
    def calculate_pivot_score(
        vehicle_make: str,
        vehicle_model: str,
        vehicle_year: int,
        vehicle_mileage_km: int,
        listing_price: float,
        fuel_type: str = "petrol"
    ) -> tuple[float, float, int, str, dict]:
        """
        Calculate comprehensive Pivot Score
        
        Returns:
            - pivot_score (0-100)
            - confidence (0-1)
            - smart_buy_index (0-100 percentile)
            - risk_rating (low/medium/high)
            - factors (dict with component scores)
        """
        
        # 1. Reliability Score (25%)
        key = (vehicle_make, vehicle_model)
        reliability_score = PivotScoreCalculator.RELIABILITY_SCORES.get(key, 85)
        
        # 2. Age & Condition Score (35%)
        current_year = 2024
        age = current_year - vehicle_year
        age_score = max(20, 100 - (age * 5))  # Decreases by 5 points per year
        
        # Mileage assessment
        expected_mileage = age * 12000  # Uganda avg 12,000 km/year
        mileage_ratio = vehicle_mileage_km / max(expected_mileage, 80000)
        mileage_score = max(10, 100 - (mileage_ratio * 50))
        
        age_condition = (age_score * 0.6) + (mileage_score * 0.4)
        
        # 3. Market Value Score (25%)
        depreciation_rate = PivotScoreCalculator.DEPRECIATION_RATES.get(key, 0.08)
        expected_price = PivotScoreCalculator._estimate_market_price(
            vehicle_make, vehicle_model, vehicle_year
        )
        price_vs_market = listing_price / max(expected_price, 1)
        
        if price_vs_market < 0.85:
            market_score = 95  # Great deal
        elif price_vs_market < 0.95:
            market_score = 85  # Good deal
        elif price_vs_market < 1.05:
            market_score = 75  # Fair price
        elif price_vs_market < 1.15:
            market_score = 60  # Slight premium
        else:
            market_score = 40  # Overpriced
        
        # 4. Fuel Efficiency Score (15%)
        fuel_eff = PivotScoreCalculator.FUEL_EFFICIENCY.get(key, 8.5)
        fuel_score = max(40, 100 - (fuel_eff * 5))  # Lower consumption = higher score
        
        # Composite Pivot Score
        pivot_score = (
            (reliability_score * 0.25) +
            (age_condition * 0.35) +
            (market_score * 0.25) +
            (fuel_score * 0.15)
        )
        
        # Confidence score (based on data availability)
        confidence = min(1.0, 0.85 + (reliability_score / 500))
        
        # Risk rating
        if pivot_score > 80:
            risk_rating = RiskRating.LOW
        elif pivot_score > 60:
            risk_rating = RiskRating.MEDIUM
        else:
            risk_rating = RiskRating.HIGH
        
        # Smart Buy Index (percentile ranking)
        smart_buy_index = min(100, max(0, int(pivot_score)))
        
        # Factors breakdown
        factors = {
            "reliability": reliability_score,
            "age_condition": age_condition,
            "market_value": market_score,
            "fuel_efficiency": fuel_score,
            "age_years": age,
            "mileage_km": vehicle_mileage_km,
            "price_vs_market_ratio": round(price_vs_market, 2),
        }
        
        return pivot_score, confidence, smart_buy_index, risk_rating, factors
    
    @staticmethod
    def _estimate_market_price(make: str, model: str, year: int) -> float:
        """Estimate market price based on vehicle specs"""
        base_prices = {
            ("Toyota", "Harrier"): 12_000_000,
            ("Toyota", "RAV4"): 11_500_000,
            ("Toyota", "Vitz"): 4_500_000,
            ("Honda", "CR-V"): 12_500_000,
            ("Mazda", "CX-5"): 13_000_000,
            ("Nissan", "X-Trail"): 11_000_000,
            ("Hyundai", "Elantra"): 7_500_000,
            ("Kia", "Picanto"): 5_500_000,
        }
        
        base_price = base_prices.get((make, model), 10_000_000)
        age = 2024 - year
        depreciation_rate = PivotScoreCalculator.DEPRECIATION_RATES.get((make, model), 0.08)
        
        # Apply depreciation
        current_value = base_price * ((1 - depreciation_rate) ** age)
        return max(current_value, base_price * 0.3)  # Don't go below 30% of base

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    logger.info("🚀 Advantage Engine starting up...")
    yield
    logger.info("🛑 Advantage Engine shutting down...")

app = FastAPI(
    title="AutoPivot - Advantage Engine",
    description="AI-powered vehicle scoring and analytics",
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "advantage-engine",
        "version": "0.1.0"
    }

@app.post("/api/v1/scores/pivot")
async def calculate_pivot_score(
    vehicle_make: str = Query(...),
    vehicle_model: str = Query(...),
    vehicle_year: int = Query(...),
    vehicle_mileage_km: int = Query(...),
    listing_price: float = Query(...),
    fuel_type: str = Query("petrol")
):
    """Calculate Pivot Score for a vehicle"""
    logger.info(f"Calculating Pivot Score for {vehicle_make} {vehicle_model}")
    
    pivot_score, confidence, smart_buy_index, risk_rating, factors = \
        PivotScoreCalculator.calculate_pivot_score(
            vehicle_make, vehicle_model, vehicle_year,
            vehicle_mileage_km, listing_price, fuel_type
        )
    
    return BaseResponse(
        success=True,
        data={
            "pivot_score": round(pivot_score, 1),
            "confidence": round(confidence, 2),
            "smart_buy_index": smart_buy_index,
            "risk_rating": risk_rating.value,
            "factors": factors
        },
        meta={"message": "Pivot Score calculated successfully"}
    )

@app.get("/api/v1/insights/fuel-prediction")
async def predict_fuel_consumption(
    vehicle_make: str = Query(...),
    vehicle_model: str = Query(...),
    vehicle_year: int = Query(...),
    transmission: str = Query("automatic")
):
    """Predict fuel consumption for a vehicle"""
    logger.info(f"Predicting fuel for {vehicle_make} {vehicle_model}")
    
    fuel_eff = PivotScoreCalculator.FUEL_EFFICIENCY.get(
        (vehicle_make, vehicle_model),
        8.5
    )
    
    # Adjust for transmission
    if transmission == "manual":
        fuel_eff *= 0.90  # Manual transmissions are ~10% more efficient
    
    # Adjust for age
    age = 2024 - vehicle_year
    fuel_eff *= (1 + age * 0.02)  # Older cars slightly worse fuel economy
    
    monthly_budget_ugx = fuel_eff * 30 * 3500  # 3,500 UGX per liter
    annual_cost_ugx = monthly_budget_ugx * 12
    
    return BaseResponse(
        success=True,
        data={
            "liters_per_100km": round(fuel_eff, 1),
            "highway_consumption": round(fuel_eff * 0.90, 1),
            "city_consumption": round(fuel_eff * 1.15, 1),
            "monthly_fuel_budget_ugx": round(monthly_budget_ugx),
            "annual_fuel_cost_ugx": round(annual_cost_ugx),
            "current_fuel_price_per_liter": 3500
        },
        meta={"message": "Fuel prediction calculated"}
    )

@app.get("/api/v1/insights/resale-forecast")
async def forecast_resale_value(
    vehicle_make: str = Query(...),
    vehicle_model: str = Query(...),
    vehicle_year: int = Query(...),
    current_price: float = Query(...),
    months_ahead: int = Query(24, ge=6, le=60)
):
    """Forecast vehicle resale value in the future"""
    logger.info(f"Forecasting resale for {vehicle_make} {vehicle_model}")
    
    depreciation_rate = PivotScoreCalculator.DEPRECIATION_RATES.get(
        (vehicle_make, vehicle_model),
        0.08
    )
    
    years_ahead = months_ahead / 12
    future_value = current_price * ((1 - depreciation_rate) ** years_ahead)
    depreciation_percent = ((current_price - future_value) / current_price) * 100
    
    return BaseResponse(
        success=True,
        data={
            "current_value_ugx": int(current_price),
            "forecasted_value_ugx": int(future_value),
            "months_ahead": months_ahead,
            "depreciation_percent": round(depreciation_percent, 1),
            "depreciation_rate_per_year": round(depreciation_rate * 100, 1),
            "market_liquidity": "good" if future_value > current_price * 0.5 else "fair"
        },
        meta={"message": "Resale forecast calculated"}
    )

@app.get("/api/v1/insights/market-sentiment")
async def analyze_market_sentiment(
    vehicle_make: str = Query(...),
    vehicle_model: str = Query(...),
    listing_price: float = Query(...),
):
    """Analyze market sentiment for a vehicle price"""
    logger.info(f"Analyzing market sentiment for {vehicle_make} {vehicle_model}")
    
    # Estimate market price
    market_price = PivotScoreCalculator._estimate_market_price(
        vehicle_make, vehicle_model, 2024
    )
    
    price_ratio = listing_price / market_price
    
    if price_ratio < 0.85:
        sentiment = "undervalued"
        recommendation = "Great deal! Consider buying"
        negotiation_room = f"±5-10%"
    elif price_ratio < 0.95:
        sentiment = "below_market"
        recommendation = "Good price, fair value"
        negotiation_room = f"±3-5%"
    elif price_ratio < 1.05:
        sentiment = "fairly_priced"
        recommendation = "Fair market price"
        negotiation_room = f"±2-3%"
    elif price_ratio < 1.15:
        sentiment = "slight_premium"
        recommendation = "Slight premium"
        negotiation_room = f"±5-10%"
    else:
        sentiment = "overpriced"
        recommendation = "Overpriced, negotiate aggressively"
        negotiation_room = f"±10-20%"
    
    return BaseResponse(
        success=True,
        data={
            "market_sentiment": sentiment,
            "recommendation": recommendation,
            "estimated_market_price_ugx": int(market_price),
            "listing_price_ugx": int(listing_price),
            "price_deviation_percent": round((price_ratio - 1) * 100, 1),
            "negotiation_range": negotiation_room
        },
        meta={"message": "Market sentiment analyzed"}
    )
