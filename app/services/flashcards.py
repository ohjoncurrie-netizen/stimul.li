import httpx
import openai
from openai import OpenAI

from app.models import (
    PedagogicalStimuliResponse,
    ProcessingRequest,
    StimulusCardBatch,
    StimulusCardResponse,
)


FLASHCARD_SYSTEM_PROMPT = """
You are stimuli, a micro-learning card generator.
Transform long-form text into bite-sized, engaging flashcards.

Requirements:
- Return concise, accurate cards anchored in the source text.
- Each card must contain:
  - prompt: a short front-side question or cue.
  - insight: a compact back-side explanation or takeaway.
- Make each card self-contained and easy to review quickly.
- Match the requested difficulty level.
- Produce exactly the requested number of cards unless the source text is too thin to support it.
- Avoid filler, repetition, vague phrasing, and markdown.
""".strip()

PEDAGOGICAL_SYSTEM_PROMPT = """
You are stimuli, an expert pedagogical designer for classroom learning.
Your job is not to summarize text generically. Your job is to transform source material
into structured teaching assets that help students understand vocabulary, reasoning, and
causal relationships.

Return a strictly valid JSON object that matches the provided schema exactly.

Pedagogical goals:
- Identify the most instructionally important Key Vocabulary from the text.
- Identify the clearest Cause-and-Effect Relationships from the text.
- Write Critical Thinking Questions that prompt analysis, inference, comparison, or evaluation.

Output rules:
- Use only the three top-level fields required by the schema:
  - key_vocabulary
  - cause_and_effect_relationships
  - critical_thinking_questions
- Each item must include:
  - title
  - content_body
- Keep each item concise, concrete, and classroom-ready.
- Ground every item in the source text. Do not invent facts.
- For vocabulary, use the term as the title and a plain-language explanation as content_body.
- For cause-and-effect, use a short relationship label as the title and explain the causal chain in content_body.
- For critical thinking questions, use a brief question stem or theme as the title and put the full question in content_body.
- Avoid markdown, bullet prefixes, commentary, or extra wrapper text.
- Match the requested difficulty level in wording and depth.
""".strip()


class FlashcardGenerationError(Exception):
    """Raised when the flashcard generation request fails."""


class AIServiceTimeoutError(FlashcardGenerationError):
    """Raised when the OpenAI request times out."""


def generate_mock_stimulus_cards(request: ProcessingRequest) -> StimulusCardResponse:
    cards: StimulusCardResponse = []

    for index in range(request.desired_card_count):
        card_number = index + 1
        cards.append(
            {
                "prompt": (
                    f"Sandbox Card {card_number}: What is the main idea behind "
                    f"{request.difficulty_level.value} micro-learning?"
                ),
                "insight": (
                    "This is mock data returned because X-Sandbox was enabled. "
                    "Use it to validate your UI, request flow, and collection logic "
                    "without consuming paid AI generation."
                ),
            }
        )

    return cards


def generate_stimulus_cards(
    request: ProcessingRequest,
    *,
    api_key: str,
    timeout_seconds: float = 30.0,
) -> StimulusCardResponse:
    client = OpenAI(
        api_key=api_key,
        timeout=httpx.Timeout(timeout_seconds, connect=5.0, read=timeout_seconds),
    )

    user_prompt = (
        "Create flashcards from the following content.\n\n"
        f"Difficulty: {request.difficulty_level.value}\n"
        f"Requested card count: {request.desired_card_count}\n\n"
        "Source text:\n"
        f"{request.long_form_text}"
    )

    try:
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": FLASHCARD_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            text_format=StimulusCardBatch,
        )
    except openai.APITimeoutError as exc:
        raise AIServiceTimeoutError(
            "OpenAI request timed out while generating stimulus cards."
        ) from exc
    except openai.APIError as exc:
        raise FlashcardGenerationError(
            "OpenAI request failed while generating stimulus cards."
        ) from exc

    parsed = response.output_parsed
    if parsed is None:
        raise FlashcardGenerationError("OpenAI returned no structured flashcard data.")

    return parsed.cards


def generate_pedagogical_stimuli(
    request: ProcessingRequest,
    *,
    api_key: str,
    timeout_seconds: float = 30.0,
) -> PedagogicalStimuliResponse:
    client = OpenAI(
        api_key=api_key,
        timeout=httpx.Timeout(timeout_seconds, connect=5.0, read=timeout_seconds),
    )

    user_prompt = (
        "Create pedagogical stimuli from the following content.\n\n"
        f"Difficulty: {request.difficulty_level.value}\n"
        f"Target item count hint: {request.desired_card_count}\n\n"
        "Source text:\n"
        f"{request.long_form_text}"
    )

    try:
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": PEDAGOGICAL_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            text_format=PedagogicalStimuliResponse,
        )
    except openai.APITimeoutError as exc:
        raise AIServiceTimeoutError(
            "OpenAI request timed out while generating pedagogical stimuli."
        ) from exc
    except openai.APIError as exc:
        raise FlashcardGenerationError(
            "OpenAI request failed while generating pedagogical stimuli."
        ) from exc

    parsed = response.output_parsed
    if parsed is None:
        raise FlashcardGenerationError("OpenAI returned no structured pedagogical data.")

    return parsed
