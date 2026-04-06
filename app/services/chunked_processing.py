import math

from celery import group

from app.models import ProcessingRequest, StimulusCard, StimulusCardResponse
from app.services.chunking import CHUNK_SIZE, split_large_document
from app.tasks.stimuli import process_text_chunk


def generate_stimulus_cards_for_large_text(
    request: ProcessingRequest,
    *,
    api_key: str,
) -> StimulusCardResponse:
    chunks = split_large_document(request.long_form_text, chunk_size=CHUNK_SIZE)
    chunk_card_count = max(1, math.ceil(request.desired_card_count / max(len(chunks), 1)) + 1)

    task_group = group(
        process_text_chunk.s(
            {
                "long_form_text": chunk,
                "desired_card_count": chunk_card_count,
                "difficulty_level": request.difficulty_level.value,
            },
            api_key,
        )
        for chunk in chunks
    )
    async_result = task_group.apply_async()
    chunk_results: list[list[dict]] = async_result.get(disable_sync_subtasks=False)

    merged_cards: StimulusCardResponse = []
    seen_pairs: set[tuple[str, str]] = set()

    for chunk_cards in chunk_results:
        for card in chunk_cards:
            pair = (card["prompt"], card["insight"])
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            merged_cards.append(StimulusCard(prompt=card["prompt"], insight=card["insight"]))

    return merged_cards[: request.desired_card_count]
