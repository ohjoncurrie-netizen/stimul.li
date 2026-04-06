import csv
import io
import json

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Stimulus, User


def get_owned_stimuli(
    *,
    db: Session,
    user: User,
    stimulus_ids: list[int] | None = None,
) -> list[Stimulus]:
    statement = select(Stimulus).where(Stimulus.user_id == user.id)

    if stimulus_ids:
        statement = statement.where(Stimulus.id.in_(stimulus_ids))

    stimuli = list(db.scalars(statement.order_by(Stimulus.id.desc())).all())
    if not stimuli:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching stimuli found for this account.",
        )

    return list(reversed(stimuli))


def export_quizlet_csv(stimuli: list[Stimulus]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Term", "Definition"])

    for stimulus in stimuli:
        writer.writerow([stimulus.prompt, stimulus.insight])

    return output.getvalue()


def export_canvas_question_bank_json(stimuli: list[Stimulus]) -> str:
    payload = {
        "questions": [
            {
                "question_name": f"Stimulus {stimulus.id}",
                "question_text": stimulus.prompt,
                "question_type": "short_answer_question",
                "points_possible": 1,
                "answers": [
                    {
                        "text": stimulus.insight,
                        "weight": 100,
                    }
                ],
            }
            for stimulus in stimuli
        ]
    }
    return json.dumps(payload, indent=2)
