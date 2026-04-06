from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import AdminNotification, Stimulus, User
from app.models import StimulusCard, StimulusCardResponse


def persist_stimuli(
    *,
    db: Session,
    user: User,
    source_text: str,
    cards: StimulusCardResponse,
) -> StimulusCardResponse:
    records = [
        Stimulus(
            user_id=user.id,
            prompt=card["prompt"] if isinstance(card, dict) else card.prompt,
            insight=card["insight"] if isinstance(card, dict) else card.insight,
            source_text=source_text,
        )
        for card in cards
    ]
    db.add_all(records)
    db.commit()

    for record in records:
        db.refresh(record)

    return [
        StimulusCard(id=record.id, prompt=record.prompt, insight=record.insight)
        for record in records
    ]


def flag_stimulus_for_review(
    *,
    db: Session,
    user: User,
    stimulus_id: int,
    reason: str,
) -> tuple[Stimulus, AdminNotification]:
    stimulus = db.get(Stimulus, stimulus_id)
    if stimulus is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stimulus not found.",
        )

    if stimulus.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only report stimuli generated for your own account.",
        )

    stimulus.flagged_for_review = True
    stimulus.report_reason = reason
    stimulus.flagged_at = datetime.now(UTC)

    notification = AdminNotification(
        user_id=user.id,
        stimulus_id=stimulus.id,
        event_type="stimulus_reported_inaccurate",
        message=(
            f"Teacher {user.email} reported stimulus {stimulus.id} as inaccurate: {reason}"
        ),
        is_read=False,
    )

    db.add(notification)
    db.add(stimulus)
    db.commit()
    db.refresh(stimulus)
    db.refresh(notification)
    return stimulus, notification
