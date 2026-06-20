from pydantic import BaseModel
from typing import Optional


class CreatePaymentRequest(BaseModel):
    amount: float
    currency: Optional[str] = "USD"
    phone_number: Optional[str] = None
    plan_id: Optional[str] = None


class SubscribeRequest(BaseModel):
    plan_id: str
    interval: str = "monthly"
    success_url: str = "http://localhost/dashboard"
    cancel_url: str = "http://localhost/pricing"
