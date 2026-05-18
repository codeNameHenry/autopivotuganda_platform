-- ============================================================================
-- AutoPivot Uganda - Database Schema
-- PostgreSQL 15+
-- ============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- ============================================================================
-- USERS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    
    -- Profile
    user_type VARCHAR(50) NOT NULL,
    profile_picture_url TEXT,
    bio TEXT,
    
    -- Location
    primary_location GEOMETRY(POINT, 4326),
    primary_address TEXT,
    region VARCHAR(50),
    
    -- Authentication
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    
    -- Trust
    trust_score FLOAT DEFAULT 50.0,
    seller_rating FLOAT,
    
    -- Subscription
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_expires_at TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_users_location ON users USING gist(primary_location);
CREATE INDEX idx_users_type ON users(user_type);

-- ============================================================================
-- LISTINGS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Vehicle Info
    vehicle_make VARCHAR(50) NOT NULL,
    vehicle_model VARCHAR(100) NOT NULL,
    vehicle_year SMALLINT NOT NULL,
    vehicle_mileage_km INT NOT NULL,
    vehicle_vin VARCHAR(17) UNIQUE,
    
    -- Details
    transmission VARCHAR(50),
    fuel_type VARCHAR(50) NOT NULL,
    body_type VARCHAR(50),
    engine_displacement_cc INT,
    color VARCHAR(30),
    doors INT,
    
    -- Pricing
    listing_price DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'UGX',
    
    -- Seller & Status
    seller_id UUID NOT NULL REFERENCES users(id),
    listing_status VARCHAR(50) DEFAULT 'active',
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    views_count INT DEFAULT 0,
    
    -- Location
    seller_location GEOMETRY(POINT, 4326) NOT NULL,
    seller_address TEXT,
    
    -- Media
    primary_image_url TEXT,
    image_urls TEXT[],
    
    -- AI Scores
    pivot_score FLOAT,
    market_sentiment VARCHAR(50),
    fraud_probability FLOAT,
    
    -- Verification
    mechanic_verified BOOLEAN DEFAULT FALSE,
    mechanic_report_id UUID,
    
    -- Metadata
    description TEXT,
    service_history_available BOOLEAN,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_listings_seller ON listings(seller_id);
CREATE INDEX idx_listings_status ON listings(listing_status);
CREATE INDEX idx_listings_location ON listings USING gist(seller_location);
CREATE INDEX idx_listings_vehicle ON listings(vehicle_make, vehicle_model);
CREATE INDEX idx_listings_created ON listings(created_at DESC);
CREATE INDEX idx_listings_pivot_score ON listings(pivot_score DESC);

-- ============================================================================
-- MECHANIC REPORTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS mechanic_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    mechanic_id UUID NOT NULL REFERENCES users(id),
    
    -- Report Details
    inspection_date TIMESTAMP NOT NULL,
    report_status VARCHAR(50),
    overall_condition VARCHAR(50),
    condition_score FLOAT,
    
    -- Component Conditions
    engine_status VARCHAR(50),
    transmission_status VARCHAR(50),
    suspension_status VARCHAR(50),
    brakes_status VARCHAR(50),
    
    -- Issues
    major_issues TEXT[],
    minor_issues TEXT[],
    rust_detected BOOLEAN,
    accident_indicators BOOLEAN,
    
    -- Pricing
    estimated_repair_cost DECIMAL(12, 2),
    fair_market_price DECIMAL(12, 2),
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_listing ON mechanic_reports(listing_id);
CREATE INDEX idx_reports_mechanic ON mechanic_reports(mechanic_id);

-- ============================================================================
-- CHAT MESSAGES
-- ============================================================================

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    sender_id UUID NOT NULL REFERENCES users(id),
    receiver_id UUID NOT NULL REFERENCES users(id),
    
    -- Message
    message_text TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    is_encrypted BOOLEAN DEFAULT TRUE,
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    -- Related
    listing_id UUID NOT NULL REFERENCES listings(id),
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_conversation ON chat_messages(conversation_id);
CREATE INDEX idx_chat_listing ON chat_messages(listing_id);
CREATE INDEX idx_chat_created ON chat_messages(created_at DESC);

-- ============================================================================
-- LOGISTICS QUOTES
-- ============================================================================

CREATE TABLE IF NOT EXISTS logistics_quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Route
    origin_location GEOMETRY(POINT, 4326) NOT NULL,
    origin_address TEXT,
    destination_location GEOMETRY(POINT, 4326) NOT NULL,
    destination_address TEXT,
    distance_km FLOAT NOT NULL,
    
    -- Pricing
    base_price DECIMAL(10, 2) NOT NULL,
    fuel_surcharge DECIMAL(10, 2),
    total_price DECIMAL(10, 2) NOT NULL,
    
    -- Details
    estimated_duration_hours FLOAT,
    road_condition VARCHAR(50),
    delivery_method VARCHAR(50),
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP
);

CREATE INDEX idx_quotes_distance ON logistics_quotes(distance_km);

-- ============================================================================
-- TRANSACTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Parties
    buyer_id UUID NOT NULL REFERENCES users(id),
    seller_id UUID NOT NULL REFERENCES users(id),
    listing_id UUID NOT NULL REFERENCES listings(id),
    
    -- Transaction
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'UGX',
    transaction_status VARCHAR(50) DEFAULT 'pending',
    
    -- Payment
    payment_method VARCHAR(50),
    payment_reference VARCHAR(255),
    
    -- Escrow
    escrow_status VARCHAR(50) DEFAULT 'none',
    escrow_release_date TIMESTAMP,
    
    -- Audit
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_transactions_buyer ON transactions(buyer_id);
CREATE INDEX idx_transactions_seller ON transactions(seller_id);
CREATE INDEX idx_transactions_status ON transactions(transaction_status);
CREATE INDEX idx_transactions_created ON transactions(initiated_at DESC);

-- ============================================================================
-- WATCHLIST
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_watchlist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    
    UNIQUE(user_id, listing_id)
);

CREATE INDEX idx_watchlist_user ON user_watchlist(user_id);

-- ============================================================================
-- AI MODEL PREDICTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_model_predictions (
    id BIGSERIAL PRIMARY KEY,
    
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    listing_id UUID NOT NULL REFERENCES listings(id),
    
    prediction_value FLOAT NOT NULL,
    confidence_score FLOAT,
    
    actual_value FLOAT,
    outcome_timestamp TIMESTAMP,
    mape_error FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_model ON ai_model_predictions(model_name);
CREATE INDEX idx_predictions_listing ON ai_model_predictions(listing_id);
