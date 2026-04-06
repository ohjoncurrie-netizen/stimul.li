from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.models import ReportStimulusErrorRequest, ReportStimulusErrorResponse
from app.services.stimuli import flag_stimulus_for_review


router = APIRouter(prefix="/stimuli", tags=["stimuli"])


@router.post("/{stimulus_id}/report-error", response_model=ReportStimulusErrorResponse)
def report_stimulus_error(
    stimulus_id: int,
    payload: ReportStimulusErrorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportStimulusErrorResponse:
    stimulus, notification = flag_stimulus_for_review(
        db=db,
        user=current_user,
        stimulus_id=stimulus_id,
        reason=payload.reason,
    )
    return ReportStimulusErrorResponse(
        stimulus_id=stimulus.id,
        flagged=stimulus.flagged_for_review,
        notification_created=notification.id is not None,
    )
