from enum import Enum

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.services.export import (
    export_canvas_question_bank_json,
    export_quizlet_csv,
    get_owned_stimuli,
)


class ExportFormat(str, Enum):
    csv = "csv"
    json = "json"


router = APIRouter(prefix="/v1/export", tags=["export"])


@router.get("/{format_name}")
def export_stimuli(
    format_name: ExportFormat,
    stimulus_ids: list[int] | None = Query(
        default=None,
        description="Optional list of stimulus IDs to export. If omitted, exports all stimuli for the current user.",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    stimuli = get_owned_stimuli(db=db, user=current_user, stimulus_ids=stimulus_ids)

    if format_name == ExportFormat.csv:
        return Response(
            content=export_quizlet_csv(stimuli),
            media_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="stimuli-quizlet-export.csv"',
            },
        )

    return Response(
        content=export_canvas_question_bank_json(stimuli),
        media_type="application/json",
        headers={
            "Content-Disposition": 'attachment; filename="stimuli-canvas-question-bank.json"',
        },
    )
