"""
Shared models and utilities for all services
"""
from datetime import datetime
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from enum import Enum
import uuid

# ============================================================================
# ENUMS
# ============================================================================

class UserType(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    MECHANIC = "mechanic"
    DEALER = "dealer"
    ADMIN = "admin"

class ListingStatus(str, Enum):
    ACTIVE = "active"
    PENDING_VERIFICATION = "pending_verification"
    SOLD = "sold"
    EXPIRED = "expired"
    FLAGGED = "flagged"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class FuelType(str, Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    LPG = "lpg"
    HYBRID = "hybrid"
    ELECTRIC = "electric"

class TransmissionType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    CVT = "cvt"

class BodyType(str, Enum):
    SEDAN = "sedan"
    SUV = "suv"
    HATCHBACK = "hatchback"
    VAN = "van"
    PICKUP = "pickup"

# ============================================================================
# BASE SCHEMAS
# ============================================================================

class BaseResponse(BaseModel):
    """Standard API response format"""
    success: bool
    data: Optional[dict] = None
    error: Optional[dict] = None
    meta: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": "uuid-123"},
                "meta": {"request_id": "req-xyz", "timestamp": "2024-05-15T10:30:00Z"}
            }
        }

class ErrorResponse(BaseModel):
    """Error response format"""
    code: str
    message: str
    details: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": "LISTING_NOT_FOUND",
                "message": "The requested listing does not exist",
                "details": {"listing_id": "uuid-123"}
            }
        }

# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    user_type: UserType

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None

class UserResponse(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trust_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# LISTING SCHEMAS
# ============================================================================

class ListingBase(BaseModel):
    vehicle_make: str
    vehicle_model: str
    vehicle_year: int
    vehicle_mileage_km: int
    fuel_type: FuelType
    transmission: TransmissionType
    body_type: BodyType
    listing_price: float
    description: str

class ListingCreate(ListingBase):
    engine_displacement_cc: Optional[int] = None
    color: Optional[str] = None
    seller_location_lat: float
    seller_location_lng: float
    seller_address: str

class ListingUpdate(BaseModel):
    listing_price: Optional[float] = None
    description: Optional[str] = None
    listing_status: Optional[ListingStatus] = None

class ListingResponse(ListingBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    listing_status: ListingStatus
    pivot_score: Optional[float] = None
    market_sentiment: Optional[str] = None
    views_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# PIVOT SCORE SCHEMAS
# ============================================================================

class PivotScoreRequest(BaseModel):
    listing_id: str

class RiskRating(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class PivotScoreResponse(BaseModel):
    listing_id: str
    score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    smart_buy_index: int = Field(ge=0, le=100)
    risk_rating: RiskRating
    market_sentiment: str
    factors: dict
    created_at: datetime

# ============================================================================
# FUEL PREDICTION SCHEMAS
# ============================================================================

class FuelPredictionResponse(BaseModel):
    listing_id: str
    liters_per_100km: float
    highway_consumption: float
    city_consumption: float
    mixed_consumption: float
    monthly_fuel_budget_ugx: float
    annual_fuel_cost_ugx: float
    confidence_interval: float = 0.15
    created_at: datetime

# ============================================================================
# LOGISTICS SCHEMAS
# ============================================================================

class Location(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "latitude": 0.3476,
                "longitude": 32.5825,
                "address": "Kampala, Uganda"
            }
        }

class LogisticsQuoteRequest(BaseModel):
    origin: Location
    destination: Location
    vehicle_type: str

class RoadCondition(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class DeliveryMethod(str, Enum):
    TOW_TRUCK = "tow_truck"
    DRIVE_DELIVERY = "drive_delivery"
    FLATBED = "flatbed"

class LogisticsQuoteResponse(BaseModel):
    quote_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    distance_km: float
    estimated_duration_hours: float
    base_price: float
    fuel_surcharge: float
    distance_surcharge: float
    total_price: float
    delivery_methods: list[DeliveryMethod]
    road_condition: RoadCondition
    current_fuel_price_per_liter: float
    valid_until: datetime

# ============================================================================
# CHAT SCHEMAS
# ============================================================================

class ChatMessageCreate(BaseModel):
    receiver_id: str
    listing_id: str
    message_text: str
    message_type: str = "text"

class ChatMessageResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    sender_id: str
    receiver_id: str
    message_text: str
    is_read: bool = False
    created_at: datetime

# ============================================================================
# VERIFICATION SCHEMAS
# ============================================================================

class ConditionLevel(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class MechanicReportCreate(BaseModel):
    listing_id: str
    inspection_date: datetime
    overall_condition: ConditionLevel
    engine_status: ConditionLevel
    transmission_status: ConditionLevel
    suspension_status: ConditionLevel
    brakes_status: ConditionLevel
    electrical_status: ConditionLevel
    interior_status: ConditionLevel
    exterior_status: ConditionLevel
    major_issues: list[str]
    minor_issues: list[str]
    rust_detected: bool
    accident_indicators: bool

class MechanicReportResponse(MechanicReportCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mechanic_id: str
    condition_score: float
    estimated_repair_cost: Optional[float] = None
    fair_market_price: Optional[float] = None
    created_at: datetime

# ============================================================================
# PAGINATION
# ============================================================================

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: list[T]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 20,
                "items": []
            }
        }
