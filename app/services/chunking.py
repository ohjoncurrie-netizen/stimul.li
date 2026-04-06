import re


CHUNK_SIZE = 2000
CHUNK_THRESHOLD = 10_000


def split_large_document(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    normalized = text.strip()
    if len(normalized) <= chunk_size:
        return [normalized]

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
    if not paragraphs:
        return _split_by_sentences(normalized, chunk_size)

    chunks: list[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        candidate = f"{current_chunk}\n\n{paragraph}".strip() if current_chunk else paragraph
        if len(candidate) <= chunk_size:
            current_chunk = candidate
            continue

        if current_chunk:
            chunks.append(current_chunk)
            current_chunk = ""

        if len(paragraph) <= chunk_size:
            current_chunk = paragraph
        else:
            chunks.extend(_split_by_sentences(paragraph, chunk_size))

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _split_by_sentences(text: str, chunk_size: int) -> list[str]:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    if not sentences:
        return _split_hard(text, chunk_size)

    chunks: list[str] = []
    current_chunk = ""

    for sentence in sentences:
        candidate = f"{current_chunk} {sentence}".strip() if current_chunk else sentence
        if len(candidate) <= chunk_size:
            current_chunk = candidate
            continue

        if current_chunk:
            chunks.append(current_chunk)
            current_chunk = ""

        if len(sentence) <= chunk_size:
            current_chunk = sentence
        else:
            chunks.extend(_split_hard(sentence, chunk_size))

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _split_hard(text: str, chunk_size: int) -> list[str]:
    return [text[index : index + chunk_size].strip() for index in range(0, len(text), chunk_size)]
