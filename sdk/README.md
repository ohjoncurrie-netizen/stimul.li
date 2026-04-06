# stimul.li SDK

TypeScript SDK for integrating with the `stimul.li` API.

## Install

```bash
npm install @stimuli/sdk
```

## Usage

```ts
import { StimuliClient } from "@stimuli/sdk";

const client = new StimuliClient({
  baseUrl: "https://api.stimul.li",
  apiKey: process.env.STIMULI_API_KEY,
  timeoutMs: 15000,
  retries: {
    maxRetries: 2,
    initialDelayMs: 300
  }
});

const cards = await client.createFlashcards({
  long_form_text: "Long-form source text goes here.",
  desired_card_count: 5,
  difficulty_level: "beginner"
});

console.log(cards);
```

## What it includes

- Typed request and response interfaces
- Retries for `429`, `408`, and `5xx` responses
- Network timeout protection
- Structured API errors with `statusCode` and `requestId`
