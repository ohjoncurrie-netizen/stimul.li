from app.core.celery_app import celery_app
from app.models import ProcessingRequest
from app.services.flashcards import generate_stimulus_cards


@celery_app.task(name="app.tasks.stimuli.process_text_chunk")
def process_text_chunk(payload: dict, api_key: str) -> list[dict]:
    request = ProcessingRequest.model_validate(payload)
    cards = generate_stimulus_cards(request, api_key=api_key)
    return [card if isinstance(card, dict) else card.model_dump() for card in cards]
