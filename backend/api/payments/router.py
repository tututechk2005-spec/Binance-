from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.database import get_db
from database.models import User, Payment, Subscription, Plan, Wallet, Transaction
from database.models import PaymentStatus, PaymentProvider, TransactionType
from middleware.auth import get_current_user
from core.config import settings
from .schemas import CreatePaymentRequest, SubscribeRequest
import uuid
import httpx
import stripe

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.get("/plans")
async def get_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Plan).where(Plan.is_active == True))
    plans = result.scalars().all()
    return [
        {
            "id": str(p.id), "name": p.name, "slug": p.slug, "description": p.description,
            "price_monthly": float(p.price_monthly),
            "price_quarterly": float(p.price_quarterly) if p.price_quarterly else None,
            "price_yearly": float(p.price_yearly) if p.price_yearly else None,
            "max_api_keys": p.max_api_keys,
            "max_auto_trades_per_day": p.max_auto_trades_per_day,
            "max_signals_per_day": p.max_signals_per_day,
        }
        for p in plans
    ]


@router.get("/history")
async def get_payment_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Payment).where(Payment.user_id == current_user.id)
        .order_by(desc(Payment.created_at))
        .offset((page - 1) * per_page).limit(per_page)
    )
    payments = result.scalars().all()
    return [
        {
            "id": str(p.id), "provider": p.provider.value, "amount": float(p.amount),
            "currency": p.currency, "status": p.status.value, "created_at": p.created_at,
        }
        for p in payments
    ]


@router.post("/stripe/create-session")
async def stripe_create_session(
    payload: SubscribeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Plan).where(Plan.id == payload.plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found.")
    price_id = plan.stripe_price_id_monthly or plan.stripe_price_id_yearly
    if not price_id:
        raise HTTPException(status_code=400, detail="Stripe price not configured for this plan.")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            customer_email=current_user.email,
            metadata={"user_id": str(current_user.id), "plan_id": str(plan.id)},
            success_url=f"{payload.success_url}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=payload.cancel_url,
        )
        return {"session_id": session.id, "url": session.url}
    except stripe.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature.")
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"].get("user_id")
        plan_id = session["metadata"].get("plan_id")
        if user_id and plan_id:
            payment = Payment(
                user_id=user_id, provider=PaymentProvider.STRIPE,
                external_id=session["id"], amount=session.get("amount_total", 0) / 100,
                currency=session.get("currency", "usd").upper(), status=PaymentStatus.COMPLETED,
            )
            db.add(payment)
            await db.commit()
    return {"received": True}


@router.post("/mtn/initiate")
async def mtn_payment(
    payload: CreatePaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext_id = str(uuid.uuid4())
    try:
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                f"{settings.MTN_BASE_URL}/collection/token/",
                headers={
                    "Authorization": f"Basic {settings.MTN_API_USER}:{settings.MTN_API_KEY}",
                    "Ocp-Apim-Subscription-Key": settings.MTN_SUBSCRIPTION_KEY,
                },
            )
            token = token_resp.json().get("access_token")
            resp = await client.post(
                f"{settings.MTN_BASE_URL}/collection/v1_0/requesttopay",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Reference-Id": ext_id,
                    "X-Target-Environment": settings.MTN_ENVIRONMENT,
                    "Ocp-Apim-Subscription-Key": settings.MTN_SUBSCRIPTION_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "amount": str(payload.amount), "currency": payload.currency or "UGX",
                    "externalId": ext_id, "payer": {"partyIdType": "MSISDN", "partyId": payload.phone_number},
                    "payerMessage": "Binance AI Trader Pro Subscription",
                    "payeeNote": "Subscription payment",
                },
            )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MTN API error: {str(e)}")
    payment = Payment(
        user_id=current_user.id, provider=PaymentProvider.MTN, external_id=ext_id,
        amount=payload.amount, currency=payload.currency or "UGX",
        status=PaymentStatus.PENDING, phone_number=payload.phone_number,
    )
    db.add(payment)
    await db.commit()
    return {"reference_id": ext_id, "status": "pending", "message": "Payment initiated. Approve on your phone."}


@router.post("/airtel/initiate")
async def airtel_payment(
    payload: CreatePaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext_id = str(uuid.uuid4())
    try:
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                f"{settings.AIRTEL_BASE_URL}/auth/oauth2/token",
                data={"client_id": settings.AIRTEL_CLIENT_ID, "client_secret": settings.AIRTEL_CLIENT_SECRET, "grant_type": "client_credentials"},
            )
            token = token_resp.json().get("access_token")
            resp = await client.post(
                f"{settings.AIRTEL_BASE_URL}/merchant/v2/payments/",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "reference": ext_id,
                    "subscriber": {"country": "UG", "currency": "UGX", "msisdn": payload.phone_number},
                    "transaction": {"amount": payload.amount, "country": "UG", "currency": "UGX", "id": ext_id},
                },
            )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Airtel API error: {str(e)}")
    payment = Payment(
        user_id=current_user.id, provider=PaymentProvider.AIRTEL, external_id=ext_id,
        amount=payload.amount, currency=payload.currency or "UGX",
        status=PaymentStatus.PENDING, phone_number=payload.phone_number,
    )
    db.add(payment)
    await db.commit()
    return {"reference_id": ext_id, "status": "pending", "message": "Payment initiated. Approve on your phone."}


@router.get("/mtn/status/{reference_id}")
async def mtn_payment_status(
    reference_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                f"{settings.MTN_BASE_URL}/collection/token/",
                headers={
                    "Authorization": f"Basic {settings.MTN_API_USER}:{settings.MTN_API_KEY}",
                    "Ocp-Apim-Subscription-Key": settings.MTN_SUBSCRIPTION_KEY,
                },
            )
            token = token_resp.json().get("access_token")
            resp = await client.get(
                f"{settings.MTN_BASE_URL}/collection/v1_0/requesttopay/{reference_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Target-Environment": settings.MTN_ENVIRONMENT,
                    "Ocp-Apim-Subscription-Key": settings.MTN_SUBSCRIPTION_KEY,
                },
            )
            data = resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    if data.get("status") == "SUCCESSFUL":
        result = await db.execute(
            select(Payment).where(Payment.external_id == reference_id)
        )
        payment = result.scalar_one_or_none()
        if payment and payment.status == PaymentStatus.PENDING:
            payment.status = PaymentStatus.COMPLETED
            await db.commit()

    return data
