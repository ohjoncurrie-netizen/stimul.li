"use client";

import { useState } from "react";

import "./MicroLearningCardGrid.css";

export interface StimulusCard {
  prompt: string;
  insight: string;
}

interface SavePayload {
  collectionName?: string;
  card: StimulusCard;
}

interface MicroLearningCardGridProps {
  cards: StimulusCard[];
  apiBaseUrl: string;
  apiKey: string;
  collectionName?: string;
  heading?: string;
  subheading?: string;
}

export function MicroLearningCardGrid({
  cards,
  apiBaseUrl,
  apiKey,
  collectionName = "My First Collection",
  heading = "Micro-Learning Cards",
  subheading = "Tap or click a card to flip it and reveal the insight.",
}: MicroLearningCardGridProps) {
  const [flippedIndex, setFlippedIndex] = useState<number | null>(null);
  const [busyIndex, setBusyIndex] = useState<number | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [savedIndex, setSavedIndex] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleCopy(card: StimulusCard, index: number) {
    setError(null);
    await navigator.clipboard.writeText(JSON.stringify(card, null, 2));
    setCopiedIndex(index);
    window.setTimeout(() => setCopiedIndex((current) => (current === index ? null : current)), 1800);
  }

  async function handleSave(card: StimulusCard, index: number) {
    setError(null);
    setBusyIndex(index);

    const response = await fetch(`${apiBaseUrl.replace(/\/$/, "")}/v1/collections`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      },
      body: JSON.stringify({
        collectionName,
        card,
      } satisfies SavePayload),
    });

    setBusyIndex(null);

    if (!response.ok) {
      const detail = await safeErrorMessage(response);
      setError(detail ?? "Unable to save this card to the collection.");
      return;
    }

    setSavedIndex(index);
    window.setTimeout(() => setSavedIndex((current) => (current === index ? null : current)), 2200);
  }

  return (
    <section className="stimuli-shell">
      <div className="stimuli-header">
        <p className="stimuli-kicker">stimul.li</p>
        <h2>{heading}</h2>
        <p>{subheading}</p>
      </div>

      {error ? <div className="stimuli-error">{error}</div> : null}

      <div className="stimuli-grid">
        {cards.map((card, index) => {
          const flipped = flippedIndex === index;
          const copied = copiedIndex === index;
          const saved = savedIndex === index;
          const busy = busyIndex === index;

          return (
            <article className="stimuli-card-block" key={`${card.prompt}-${index}`}>
              <button
                className={`stimuli-card ${flipped ? "is-flipped" : ""}`}
                type="button"
                onClick={() => setFlippedIndex(flipped ? null : index)}
                aria-pressed={flipped}
              >
                <div className="stimuli-card-face stimuli-card-front">
                  <span className="stimuli-face-label">Prompt</span>
                  <h3>{card.prompt}</h3>
                  <span className="stimuli-hint">Flip for insight</span>
                </div>

                <div className="stimuli-card-face stimuli-card-back">
                  <span className="stimuli-face-label">Insight</span>
                  <p>{card.insight}</p>
                </div>
              </button>

              <div className="stimuli-actions">
                <button
                  type="button"
                  className="stimuli-action secondary"
                  onClick={() => void handleCopy(card, index)}
                >
                  {copied ? "Copied" : "Copy JSON"}
                </button>

                <button
                  type="button"
                  className="stimuli-action primary"
                  onClick={() => void handleSave(card, index)}
                  disabled={busy}
                >
                  {busy ? "Saving..." : saved ? "Saved" : "Save to Collection"}
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

async function safeErrorMessage(response: Response): Promise<string | null> {
  try {
    const body = (await response.json()) as { detail?: string };
    return body.detail ?? null;
  } catch {
    return null;
  }
}
