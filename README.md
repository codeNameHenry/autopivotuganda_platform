# AutoPivot Uganda

> Africa's Smartest AI-Powered Automotive Marketplace & Buyer-Advocacy Ecosystem

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Flutter 3.10+

### Development Setup

```bash
# Clone the repository
git clone https://github.com/autopivot/uganda.git
cd car_sale_aggregator

# Copy environment configuration
cp .env.example .env

# Start development environment with Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| API Gateway | http://localhost:8000 | Main REST API |
| Web App | http://localhost:3000 | Next.js frontend |
| Admin Dashboard | http://localhost:3001 | Admin panel |
| Elasticsearch | http://localhost:9200 | Search index |
| PostgreSQL | localhost:5432 | Primary database |
| Redis | localhost:6379 | Cache & sessions |
| PgAdmin | http://localhost:5050 | Database admin |
| Swagger Docs | http://localhost:8000/docs | API documentation |

---

## 📁 Project Structure

```
car_sale_aggregator/
├── backend/                          # FastAPI microservices
│   ├── services/
│   │   ├── listing-service/         # Vehicle listing management
│   │   ├── advantage-engine/        # Pivot score & AI scoring
│   │   ├── logistics-service/       # Delivery quotes & routing
│   │   ├── chat-service/            # Encrypted messaging
│   │   ├── user-service/            # Authentication & profiles
│   │   ├── verification-service/    # Mechanic reports
│   │   └── payment-service/         # Transactions & escrow
│   ├── shared/                      # Shared utilities & models
│   ├── scrapers/                    # Web scraping services
│   └── docker-compose.yml
│
├── frontend/
│   ├── web/                         # Next.js web application
│   │   ├── app/                     # App router
│   │   ├── components/              # React components
│   │   ├── lib/                     # Utilities
│   │   └── package.json
│   │
│   └── mobile/                      # Flutter mobile app
│       ├── lib/
│       │   ├── screens/
│       │   ├── widgets/
│       │   ├── models/
│       │   └── services/
│       └── pubspec.yaml
│
├── ml-pipeline/                     # ML model training & serving
│   ├── models/
│   │   ├── pivot_score_model.py
│   │   ├── fuel_predictor_model.py
│   │   ├── market_sentiment_model.py
│   │   └── resale_forecaster_model.py
│   ├── training/
│   ├── inference/
│   ├── airflow_dags/               # Scheduling & orchestration
│   └── requirements.txt
│
├── infrastructure/                  # IaC & deployment
│   ├── kubernetes/                 # K8s manifests
│   ├── terraform/                  # AWS infrastructure
│   ├── docker/                     # Dockerfiles
│   ├── helm/                       # Helm charts
│   └── scripts/
│
├── data/                           # Database & schemas
│   ├── migrations/                 # Alembic migrations
│   ├── seeds/                      # Sample data
│   └── schemas/                    # SQL table definitions
│
├── AUTOPIVOT_UGANDA_SPECIFICATION.md  # Full technical spec
├── docker-compose.yml              # Development environment
├── .env.example                    # Environment template
├── Makefile                        # Common commands
└── README.md                       # This file
```

---

## 🔧 Core Services

### 1. Listing Service (Port 8001)
**Responsibility:** Vehicle listing lifecycle
- Create/update/delete listings
- Image management (with privacy sanitization)
- Listing deduplication
- Full-text search indexing

**Tech Stack:**
- FastAPI
- SQLAlchemy ORM
- Elasticsearch integration
- Pillow (image processing)

**Key Endpoints:**
```
POST   /api/v1/listings              Create listing
GET    /api/v1/listings              List vehicles
GET    /api/v1/listings/{id}         Get listing details
PATCH  /api/v1/listings/{id}         Update listing
DELETE /api/v1/listings/{id}         Delete listing
POST   /api/v1/listings/{id}/images  Upload images
```

### 2. Advantage Engine (Port 8002)
**Responsibility:** AI-powered vehicle intelligence
- Pivot Score calculation
- Market sentiment analysis
- Fuel consumption prediction
- Resale value forecasting
- Alternative recommendations

**Tech Stack:**
- TensorFlow Serving
- XGBoost (gradient boosting)
- Redis caching
- MLflow tracking

**Key Endpoints:**
```
GET    /api/v1/listings/{id}/pivot-score
GET    /api/v1/listings/{id}/market-sentiment
GET    /api/v1/listings/{id}/fuel-prediction
GET    /api/v1/listings/{id}/resale-forecast
GET    /api/v1/listings/{id}/alternatives
```

### 3. Logistics Service (Port 8003)
**Responsibility:** Delivery & transportation
- Distance & route calculations
- Real-time delivery quotes
- Road condition analysis
- Fuel price adjustments

**Tech Stack:**
- Mapbox APIs
- Google Maps APIs
- Redis caching
- PostgreSQL with PostGIS

**Key Endpoints:**
```
POST   /api/v1/logistics/quote
GET    /api/v1/logistics/routes
GET    /api/v1/logistics/fuel-prices
```

### 4. Chat Service (Port 8004)
**Responsibility:** Encrypted seller-buyer messaging
- Ghost Chat (anonymized conversations)
- End-to-end encryption (Signal protocol)
- Inspection scheduling
- Message history

**Tech Stack:**
- FastAPI WebSockets
- Redis Pub/Sub
- PostgreSQL with encryption
- PyCryptodome (encryption)

**Key Endpoints:**
```
GET    /api/v1/chat/conversations
POST   /api/v1/chat/conversations/{id}/messages
DELETE /api/v1/chat/messages/{id}
```

### 5. User Service (Port 8005)
**Responsibility:** Authentication & user management
- User registration/login
- JWT token management
- Profile management
- Two-factor authentication

**Tech Stack:**
- FastAPI
- python-jose (JWT)
- passlib (password hashing)
- PyOTP (2FA)

**Key Endpoints:**
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh-token
GET    /api/v1/users/me
PATCH  /api/v1/users/{id}
```

### 6. Verification Service (Port 8006)
**Responsibility:** Mechanic verification & inspections
- Mechanic onboarding & certification
- Vehicle inspection reports
- Fraud detection
- Quality assurance

**Tech Stack:**
- FastAPI
- TensorFlow (fraud detection)
- S3 (report storage)
- PostgreSQL

**Key Endpoints:**
```
GET    /api/v1/mechanics
POST   /api/v1/listings/{id}/verification/request
GET    /api/v1/listings/{id}/verification
```

### 7. Payment Service (Port 8007)
**Responsibility:** Transactions & financial flows
- Payment processing
- Escrow management
- Refund handling
- Transaction history

**Tech Stack:**
- FastAPI
- Stripe SDK
- Flutterwave SDK
- PostgreSQL

**Key Endpoints:**
```
POST   /api/v1/transactions/initiate
GET    /api/v1/transactions/{id}
POST   /api/v1/transactions/{id}/confirm
POST   /api/v1/escrow/release
```

---

## 🗄️ Database Schema

### Core Tables
- **users** - User profiles & authentication
- **listings** - Vehicle listings
- **mechanic_reports** - Inspection reports
- **logistics_quotes** - Delivery pricing
- **chat_messages** - Encrypted conversations
- **transactions** - Payment records
- **vehicle_price_history** - Time-series pricing
- **ai_model_predictions** - ML model tracking

### Running Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## 🤖 Machine Learning Pipeline

### Models

#### 1. Pivot Score Model
```python
# Predicts: Vehicle value/buying recommendation (0-100)
# Training: Historical sales + market comparables
# Framework: TensorFlow Sequential
# Accuracy: MAE ±8 points
```

#### 2. Fuel Consumption Predictor
```python
# Predicts: Liters per 100km
# Training: Vehicle usage logs
# Framework: XGBoost
# Accuracy: MAPE < 15%
```

#### 3. Market Sentiment Engine
```python
# Predicts: Price classification (undervalued/fair/overpriced)
# Training: Time-series pricing data
# Framework: Prophet + Isolation Forest
```

#### 4. Resale Value Forecaster
```python
# Predicts: Vehicle value in 6/12/24 months
# Training: Historical resale prices
# Framework: LSTM Ensemble + Prophet
# Accuracy: MAPE < 18%
```

### Training Pipeline

```bash
# Feature engineering
python ml-pipeline/training/extract_features.py

# Model training
python ml-pipeline/training/train_pivot_score.py
python ml-pipeline/training/train_fuel_predictor.py

# Model validation
python ml-pipeline/training/validate_models.py

# Deploy to serving
python ml-pipeline/inference/deploy_model.py
```

---

## 🐳 Docker Deployment

### Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f listing-service

# Stop all services
docker-compose down

# Rebuild images
docker-compose build --no-cache
```

### Production Deployment

```bash
# Build production images
docker build -f infrastructure/docker/Dockerfile.prod -t autopivot/listing-service:latest backend/services/listing-service/

# Push to registry
docker push autopivot/listing-service:latest

# Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/listing-service-deployment.yaml
```

---

## ☸️ Kubernetes Deployment

```bash
# Initialize cluster (AWS EKS)
eksctl create cluster --name autopivot-prod --region eu-west-2

# Install ingress controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx

# Deploy services
kubectl apply -f infrastructure/kubernetes/

# Check deployments
kubectl get deployments
kubectl get services
kubectl get pods

# Monitor logs
kubectl logs -f deployment/listing-service
```

---

## 📊 Monitoring & Observability

### Logs
```bash
# Elasticsearch + Kibana
# Access: http://localhost:5601

# Search logs
GET /autopivot-logs-*/_search
{
  "query": {
    "match": { "service": "listing-service" }
  }
}
```

### Metrics
```bash
# Prometheus + Grafana
# Access: http://localhost:3001/grafana

# Key metrics:
# - http_requests_total
# - api_response_time_seconds
# - database_query_duration_seconds
# - ml_model_inference_time_seconds
```

### Distributed Tracing
```bash
# Jaeger UI
# Access: http://localhost:6831

# Trace a request end-to-end across all microservices
```

---

## 🔒 Security

### Environment Variables
```bash
# Never commit .env file!
# Use .env.example as template
# Store secrets in AWS Secrets Manager (production)
```

### Database
```bash
# Enable SSL/TLS
SSL_MODE=require

# Regular backups
aws rds create-db-snapshot --db-instance-identifier autopivot-prod

# Encryption at rest
AWS KMS key rotation: Quarterly
```

### API Security
```bash
# Rate limiting: 1000 requests/hour per user
# CORS: Strict origin policy
# CSRF: Token validation
# Input validation: Pydantic schemas
# SQL injection: Parameterized queries
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific service tests
pytest backend/services/listing-service/tests/

# Integration tests
pytest tests/integration/

# Load testing
locust -f tests/load/locustfile.py
```

---

## 📚 API Documentation

### Swagger UI
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

### Generate OpenAPI spec
```bash
python scripts/generate_openapi_spec.py
```

---

## 🚀 Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] ML models packaged
- [ ] Docker images built & tested
- [ ] Kubernetes manifests validated
- [ ] Load testing passed (>10K RPS)
- [ ] Security audit completed
- [ ] Monitoring configured
- [ ] Backup strategy verified
- [ ] Documentation updated

---

## 📖 Documentation

- **Technical Specification:** `AUTOPIVOT_UGANDA_SPECIFICATION.md`
- **API Reference:** `docs/API.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **Deployment Guide:** `docs/DEPLOYMENT.md`
- **ML Pipeline:** `docs/ML_PIPELINE.md`

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit pull request

### Code Standards
- Python: PEP 8, Black formatter
- JavaScript: ESLint, Prettier
- Dart: Flutter style guide

---

## 📝 License

MIT License - See LICENSE file

---

## 📞 Support

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Email:** support@autopivot.ug

---

**Status:** 🚧 Under Development (MVP Phase)
**Last Updated:** May 15, 2026
