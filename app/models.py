from enum import Enum

from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class ProcessingRequest(BaseModel):
    long_form_text: str = Field(
        ...,
        min_length=1,
        description="The source material to transform into micro-learning cards.",
    )
    desired_card_count: int = Field(
        ...,
        ge=1,
        le=100,
        description="The number of stimulus cards the API should generate.",
    )
    difficulty_level: DifficultyLevel = Field(
        ...,
        description="The target difficulty for the generated cards.",
    )


class StimulusCard(BaseModel):
    id: int | None = Field(default=None, description="Database identifier for this stimulus card.")
    prompt: str = Field(..., min_length=1, description="The front of the card.")
    insight: str = Field(..., min_length=1, description="The back of the card.")


class StimulusCardBatch(BaseModel):
    cards: list[StimulusCard] = Field(
        ...,
        min_length=1,
        description="The extracted flashcards returned by the model.",
    )


StimulusCardResponse = list[StimulusCard]


class PedagogicalCard(BaseModel):
    title: str = Field(..., min_length=1, description="Short label for the learning item.")
    content_body: str = Field(
        ...,
        min_length=1,
        description="The actual pedagogical content to render in the UI.",
    )


class PedagogicalStimuliResponse(BaseModel):
    key_vocabulary: list[PedagogicalCard] = Field(
        ...,
        description="Core vocabulary terms and definitions extracted from the source text.",
    )
    cause_and_effect_relationships: list[PedagogicalCard] = Field(
        ...,
        description="Important causal relationships identified in the source text.",
    )
    critical_thinking_questions: list[PedagogicalCard] = Field(
        ...,
        description="Open-ended questions that prompt deeper reasoning about the text.",
    )


class ReportStimulusErrorRequest(BaseModel):
    reason: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Why the teacher believes the stimulus is inaccurate or misleading.",
    )


class ReportStimulusErrorResponse(BaseModel):
    stimulus_id: int
    flagged: bool
    notification_created: bool
