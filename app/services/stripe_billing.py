import os
import uuid

import stripe
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import User


STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_MONTHLY_PRICE_ID = os.getenv("STRIPE_MONTHLY_PRICE_ID")
STRIPE_FLASH_METER_EVENT_NAME = os.getenv("STRIPE_FLASH_METER_EVENT_NAME", "flash_api_call")


class StripeConfigurationError(Exception):
    """Raised when required Stripe settings are missing."""


def _configure_stripe() -> None:
    if not STRIPE_API_KEY:
        raise StripeConfigurationError("STRIPE_API_KEY is not configured.")
    stripe.api_key = STRIPE_API_KEY


def _get_or_create_stripe_customer(db: Session, user: User) -> str:
    _configure_stripe()

    if user.stripe_customer_id:
        return user.stripe_customer_id

    customer = stripe.Customer.create(
        email=user.email,
        metadata={"user_id": str(user.id)},
    )
    user.stripe_customer_id = customer.id
    db.add(user)
    db.commit()
    db.refresh(user)
    return customer.id


def create_subscription_checkout_session(
    *,
    db: Session,
    user: User,
    success_url: str,
    cancel_url: str,
) -> stripe.checkout.Session:
    if not STRIPE_MONTHLY_PRICE_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe monthly price is not configured.",
        )

    try:
        stripe_customer_id = _get_or_create_stripe_customer(db, user)
        return stripe.checkout.Session.create(
            mode="subscription",
            customer=stripe_customer_id,
            line_items=[
                {
                    "price": STRIPE_MONTHLY_PRICE_ID,
                    "quantity": 1,
                }
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(user.id),
            metadata={"user_id": str(user.id)},
        )
    except StripeConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except stripe.StripeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Stripe checkout session creation failed.",
        ) from exc


def report_flash_api_usage(*, db: Session, user: User, units: int = 1) -> None:
    if units < 1:
        raise ValueError("units must be at least 1")

    try:
        stripe_customer_id = _get_or_create_stripe_customer(db, user)
        stripe.billing.MeterEvent.create(
            event_name=STRIPE_FLASH_METER_EVENT_NAME,
            payload={
                "stripe_customer_id": stripe_customer_id,
                "value": str(units),
            },
            identifier=f"flash-{user.id}-{uuid.uuid4()}",
        )
    except StripeConfigurationError:
        raise
    except stripe.StripeError:
        raise
