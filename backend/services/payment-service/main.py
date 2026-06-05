"""
Payment Service - Transaction and escrow management
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Payment Service starting...")
    yield
    logger.info("🛑 Payment Service shutting down...")

app = FastAPI(
    title="AutoPivot - Payment Service",
    description="Transaction processing and escrow management",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-service"}

@app.post("/api/v1/transactions/initiate")
async def initiate_transaction(listing_id: str, buyer_id: str, payment_method: str = "bank_transfer"):
    """Initiate a payment transaction.

    Preference for Uganda: `bank_transfer` and `mobile_money` are accepted and recommended.
    The endpoint validates the method and returns a stubbed transaction record.
    """
    allowed_methods = {"bank_transfer", "mobile_money", "card", "pay_later"}
    if payment_method not in allowed_methods:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=f"Unsupported payment method: {payment_method}")

    logger.info(f"Initiating transaction for listing: {listing_id} via {payment_method}")

    # In a real service we'd create a DB record and initiate provider integration here.
    txn = {
        "transaction_id": f"txn-{listing_id}-{buyer_id}",
        "listing_id": listing_id,
        "buyer_id": buyer_id,
        "payment_method": payment_method,
        "status": "initiated",
        "preferred_methods": ["bank_transfer", "mobile_money"],
    }

    return {"transaction": txn}

@app.get("/api/v1/transactions/{transaction_id}")
async def get_transaction(transaction_id: str):
    """Get transaction details"""
    logger.info(f"Fetching transaction: {transaction_id}")
    return {"transaction": {}}

@app.post("/api/v1/escrow/release")
async def release_escrow(transaction_id: str):
    """Release escrow funds after buyer confirms delivery"""
    logger.info(f"Releasing escrow for transaction: {transaction_id}")
    return {"message": "Escrow released"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
