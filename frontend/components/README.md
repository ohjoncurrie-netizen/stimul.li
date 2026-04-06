# Frontend Components

## `MicroLearningCardGrid`

Responsive React component for rendering stimul.li flashcards with:

- flip animation for prompt/insight
- copy-to-clipboard for the API response payload
- `Save to Collection` action posting to `/v1/collections`

### Example

```tsx
import { MicroLearningCardGrid } from "./MicroLearningCardGrid";

const cards = [
  {
    prompt: "What is retrieval practice?",
    insight: "Actively recalling information strengthens long-term memory better than passive review.",
  },
];

export default function Demo() {
  return (
    <MicroLearningCardGrid
      cards={cards}
      apiBaseUrl="https://api.stimul.li"
      apiKey="stim_your_api_key"
      collectionName="AP Biology"
    />
  );
}
```
