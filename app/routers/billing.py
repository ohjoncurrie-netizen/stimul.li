from fastapi import APIRouter, Depends
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.services.stripe_billing import create_subscription_checkout_session


router = APIRouter(tags=["billing"])


class CreateSubscriptionRequest(BaseModel):
    success_url: HttpUrl
    cancel_url: HttpUrl


class CreateSubscriptionResponse(BaseModel):
    checkout_session_id: str
    checkout_url: HttpUrl


@router.post("/create-subscription", response_model=CreateSubscriptionResponse)
def create_subscription(
    payload: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CreateSubscriptionResponse:
    session = create_subscription_checkout_session(
        db=db,
        user=current_user,
        success_url=str(payload.success_url),
        cancel_url=str(payload.cancel_url),
    )
    return CreateSubscriptionResponse(
        checkout_session_id=session.id,
        checkout_url=session.url,
    )
