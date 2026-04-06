import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.rate_limit import (
    FREE_TIER_PER_MINUTE_LIMIT,
    check_monthly_flash_limit,
    increment_monthly_flash_usage,
    is_free_tier_request,
    limiter,
)
from app.db.models import User
from app.db.session import get_db
from app.models import ProcessingRequest, StimulusCardResponse
from app.services.chunked_processing import generate_stimulus_cards_for_large_text
from app.services.chunking import CHUNK_THRESHOLD
from app.services.flashcards import (
    FlashcardGenerationError,
    generate_mock_stimulus_cards,
    generate_stimulus_cards,
)
from app.services.stripe_billing import report_flash_api_usage
from app.services.stimuli import persist_stimuli


router = APIRouter(tags=["flash"])


@router.post("/flash", response_model=StimulusCardResponse)
@limiter.limit(FREE_TIER_PER_MINUTE_LIMIT, exempt_when=lambda: False)
def create_flash_cards(
    request: Request,
    response: Response,
    payload: ProcessingRequest,
    x_sandbox: str | None = Header(default=None, alias="X-Sandbox"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StimulusCardResponse:
    request.state.current_user = current_user

    if is_free_tier_request(request):
        check_monthly_flash_limit(current_user)

    sandbox_mode = (x_sandbox or "").strip().lower() == "true"
    if sandbox_mode:
        response.headers["X-Sandbox-Mode"] = "true"
        return generate_mock_stimulus_cards(payload)

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY is not configured.",
        )

    try:
        if len(payload.long_form_text) > CHUNK_THRESHOLD:
            cards = generate_stimulus_cards_for_large_text(payload, api_key=openai_api_key)
            response.headers["X-Chunked-Processing"] = "true"
        else:
            cards = generate_stimulus_cards(payload, api_key=openai_api_key)
    except FlashcardGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    persisted_cards = persist_stimuli(
        db=db,
        user=current_user,
        source_text=payload.long_form_text,
        cards=cards,
    )

    increment_monthly_flash_usage(current_user)
    try:
        report_flash_api_usage(db=db, user=current_user, units=1)
    except Exception:
        pass

    return persisted_cards
