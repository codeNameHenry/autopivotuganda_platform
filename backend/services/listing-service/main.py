"""
Listing Service - Main FastAPI Application
Handles vehicle listing lifecycle management
Features Uganda-popular vehicles with realistic market data
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import Optional
import random

from backend.shared.schemas import (
    ListingResponse, ListingCreate, ListingUpdate, BaseResponse,
    PaginatedResponse, ListingStatus, FuelType, TransmissionType, BodyType
)

# ============================================================================
# CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)

# Uganda Popular Vehicles - Based on market data
# Most common: Toyota Harrier, RAV4, Vitz, Wish; Honda CR-V; Mazda CX-5; Nissan X-Trail
UGANDA_VEHICLES = [
    {"make": "Toyota", "model": "Harrier", "years": [2010, 2012, 2015, 2018, 2020], "popular": True},
    {"make": "Toyota", "model": "RAV4", "years": [2008, 2012, 2016, 2019], "popular": True},
    {"make": "Toyota", "model": "Vitz", "years": [2008, 2010, 2014, 2018], "popular": True},
    {"make": "Toyota", "model": "Wish", "years": [2008, 2012, 2015], "popular": True},
    {"make": "Honda", "model": "CR-V", "years": [2008, 2012, 2015, 2019], "popular": True},
    {"make": "Honda", "model": "Civic", "years": [2008, 2012, 2016], "popular": True},
    {"make": "Mazda", "model": "CX-5", "years": [2012, 2015, 2018, 2020], "popular": True},
    {"make": "Nissan", "model": "X-Trail", "years": [2008, 2012, 2016, 2019], "popular": True},
    {"make": "Nissan", "model": "Serena", "years": [2010, 2014], "popular": False},
    {"make": "Hyundai", "model": "Elantra", "years": [2012, 2015, 2018], "popular": True},
    {"make": "Kia", "model": "Picanto", "years": [2015, 2018, 2020, 2022], "popular": True},
    {"make": "Volkswagen", "model": "Golf", "years": [2010, 2014, 2018], "popular": False},
]

# Uganda regions and locations
UGANDA_LOCATIONS = [
    {"name": "Kampala", "lat": 0.3476, "lng": 32.5825},
    {"name": "Mbarara", "lat": -0.6155, "lng": 29.7349},
    {"name": "Gulu", "lat": 2.7667, "lng": 32.2833},
    {"name": "Fort Portal", "lat": 0.6727, "lng": 30.2686},
    {"name": "Jinja", "lat": 0.4369, "lng": 33.1270},
    {"name": "Mbale", "lat": 1.0486, "lng": 34.1781},
]

def generate_uganda_listings() -> list[ListingResponse]:
    """Generate realistic Uganda vehicle marketplace listings"""
    listings = []
    id_counter = 1
    
    popular_vehicles = [v for v in UGANDA_VEHICLES if v["popular"]]
    
    for vehicle_spec in popular_vehicles[:10]:  # Top 10 popular vehicles
        for _ in range(2):  # 2 variants per vehicle
            year = random.choice(vehicle_spec["years"])
            location = random.choice(UGANDA_LOCATIONS)
            
            # Price estimation based on Uganda market (in UGX)
            base_prices = {
                ("Toyota", "Harrier"): 12_000_000,
                ("Toyota", "RAV4"): 11_500_000,
                ("Toyota", "Vitz"): 4_500_000,
                ("Honda", "CR-V"): 12_500_000,
                ("Mazda", "CX-5"): 13_000_000,
                ("Nissan", "X-Trail"): 11_000_000,
                ("Hyundai", "Elantra"): 7_500_000,
                ("Kia", "Picanto"): 5_500_000,
                ("Honda", "Civic"): 8_000_000,
                ("Toyota", "Wish"): 9_000_000,
                ("Nissan", "Serena"): 10_000_000,
                ("Volkswagen", "Golf"): 9_500_000,
            }
            
            base_price = base_prices.get(
                (vehicle_spec["make"], vehicle_spec["model"]),
                10_000_000
            )
            
            # Age adjustment (depreciation)
            age = 2024 - year
            depreciation = 0.10 * age  # 10% per year
            price = base_price * (1 - depreciation)
            
            # Add random variation (±15%)
            price *= random.uniform(0.85, 1.15)
            
            mileage = max(80_000, age * 15_000 + random.randint(0, 50_000))
            
            # Pivot score (simplified calculation based on age and mileage)
            pivot_score = max(20, min(100, 85 - (age * 3) - (mileage / 5000)))
            
            listing = ListingResponse(
                id=str(id_counter),
                vehicle_make=vehicle_spec["make"],
                vehicle_model=vehicle_spec["model"],
                vehicle_year=year,
                vehicle_mileage_km=int(mileage),
                fuel_type=FuelType.PETROL if vehicle_spec["make"] != "Nissan" else random.choice([FuelType.PETROL, FuelType.DIESEL]),
                transmission=random.choice([TransmissionType.MANUAL, TransmissionType.AUTOMATIC]),
                body_type=BodyType.SUV if any(x in vehicle_spec["model"] for x in ["CR-V", "Harrier", "RAV4", "CX-5", "X-Trail"]) else (BodyType.HATCHBACK if vehicle_spec["model"] in ["Vitz", "Picanto"] else BodyType.SEDAN),
                listing_price=int(price),
                description=f"Well-maintained {year} {vehicle_spec['make']} {vehicle_spec['model']} with {int(mileage)} km. Ready for immediate sale. Full service history available.",
                seller_id=f"seller-{id_counter % 20}",
                listing_status=ListingStatus.ACTIVE,
                pivot_score=pivot_score,
                market_sentiment="positive" if pivot_score > 80 else ("stable" if pivot_score > 60 else "neutral"),
                views_count=random.randint(20, 200),
                created_at=datetime.utcnow()
            )
            listings.append(listing)
            id_counter += 1
    
    return listings

sample_listings = generate_uganda_listings()

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    logger.info("🚀 Listing Service starting up...")
    yield
    logger.info("🛑 Listing Service shutting down...")

# Create FastAPI application
app = FastAPI(
    title="AutoPivot - Listing Service",
    description="Vehicle listing management and search",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "listing-service",
        "version": "0.1.0",
        "total_listings": len(sample_listings)
    }

# ============================================================================
# LISTING ENDPOINTS
# ============================================================================

@app.get("/api/v1/listings", response_model=PaginatedResponse[ListingResponse])
async def list_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    make: Optional[str] = None,
    model: Optional[str] = None,
    fuel_type: Optional[str] = None,
    body_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    min_mileage: Optional[int] = None,
    max_mileage: Optional[int] = None,
    transmission: Optional[str] = None,
    sort_by: Optional[str] = Query("newest", regex="^(newest|cheapest|most_popular|best_value)$"),
):
    """Get paginated list of vehicles with advanced filtering and sorting"""
    logger.info(f"Fetching listings - skip: {skip}, limit: {limit}, make: {make}")

    filtered = list(sample_listings)

    # Apply filters
    if make:
        filtered = [l for l in filtered if l.vehicle_make.lower() == make.lower()]
    if model:
        filtered = [l for l in filtered if l.vehicle_model.lower() == model.lower()]
    if fuel_type:
        filtered = [l for l in filtered if l.fuel_type.value.lower() == fuel_type.lower()]
    if body_type:
        filtered = [l for l in filtered if l.body_type.value.lower() == body_type.lower()]
    if transmission:
        filtered = [l for l in filtered if l.transmission.value.lower() == transmission.lower()]
    if min_price is not None:
        filtered = [l for l in filtered if l.listing_price >= min_price]
    if max_price is not None:
        filtered = [l for l in filtered if l.listing_price <= max_price]
    if min_year is not None:
        filtered = [l for l in filtered if l.vehicle_year >= min_year]
    if max_year is not None:
        filtered = [l for l in filtered if l.vehicle_year <= max_year]
    if min_mileage is not None:
        filtered = [l for l in filtered if l.vehicle_mileage_km >= min_mileage]
    if max_mileage is not None:
        filtered = [l for l in filtered if l.vehicle_mileage_km <= max_mileage]

    # Apply sorting
    if sort_by == "cheapest":
        filtered.sort(key=lambda x: x.listing_price)
    elif sort_by == "most_popular":
        filtered.sort(key=lambda x: x.views_count, reverse=True)
    elif sort_by == "best_value":
        filtered.sort(key=lambda x: x.pivot_score if x.pivot_score else 0, reverse=True)
    else:  # newest (default)
        filtered.sort(key=lambda x: x.created_at, reverse=True)

    total = len(filtered)
    items = filtered[skip : skip + limit]

    return PaginatedResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        items=items
    )

@app.get("/api/v1/listings/trending")
async def get_trending():
    """Get trending vehicles on the platform"""
    trending = sorted(sample_listings, key=lambda x: x.views_count, reverse=True)[:15]
    return BaseResponse(
        success=True,
        data={"trending": trending},
        meta={"message": "Trending vehicles returned"}
    )

@app.get("/api/v1/listings/steals")
async def get_steals():
    """Get undervalued vehicles (best deals)"""
    steals = [l for l in sample_listings if l.market_sentiment == "positive" and l.pivot_score and l.pivot_score > 85]
    steals.sort(key=lambda x: x.pivot_score, reverse=True)
    return BaseResponse(
        success=True,
        data={"steals": steals[:15]},
        meta={"message": "Undervalued vehicles returned"}
    )

@app.get("/api/v1/listings/{listing_id}", response_model=BaseResponse)
async def get_listing(listing_id: str):
    """Get detailed information about a specific listing"""
    logger.info(f"Fetching listing: {listing_id}")

    listing = next((l for l in sample_listings if l.id == listing_id), None)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    return BaseResponse(
        success=True,
        data={"listing": listing},
        meta={"message": "Listing returned successfully"}
    )

@app.post("/api/v1/listings", response_model=BaseResponse)
async def create_listing(listing: ListingCreate):
    """Create a new vehicle listing"""
    logger.info(f"Creating new listing for {listing.vehicle_make} {listing.vehicle_model}")
    
    return BaseResponse(
        success=True,
        data={"listing_id": f"new-{len(sample_listings) + 1}"},
        meta={"message": "Listing created successfully"}
    )

@app.patch("/api/v1/listings/{listing_id}", response_model=BaseResponse)
async def update_listing(listing_id: str, update: ListingUpdate):
    """Update an existing listing"""
    logger.info(f"Updating listing: {listing_id}")
    
    return BaseResponse(
        success=True,
        data={"message": "Listing updated successfully"}
    )

@app.delete("/api/v1/listings/{listing_id}", response_model=BaseResponse)
async def delete_listing(listing_id: str):
    """Delete a listing"""
    logger.info(f"Deleting listing: {listing_id}")
    
    return BaseResponse(
        success=True,
        data={"message": "Listing deleted successfully"}
    )

@app.post("/api/v1/listings/{listing_id}/images", response_model=BaseResponse)
async def upload_listing_images(listing_id: str):
    """Upload and process images for a listing"""
    logger.info(f"Uploading images for listing: {listing_id}")
    
    return BaseResponse(
        success=True,
        data={"message": "Images uploaded successfully"}
    )

@app.delete("/api/v1/listings/{listing_id}/images/{image_id}", response_model=BaseResponse)
async def delete_listing_image(listing_id: str, image_id: str):
    """Delete a specific image from a listing"""
    logger.info(f"Deleting image {image_id} from listing {listing_id}")
    
    return BaseResponse(
        success=True,
        data={"message": "Image deleted successfully"}
    )
