# ai/prompts

## Purpose
Central library of prompt templates used by `ai/llm`, versioned and
kept separate from application code so they can be iterated on
independently (e.g. by prompt engineers) without touching business logic.

## Expected Input
- Template variables (e.g. citizen profile fields, complaint text)
  to be interpolated into a given prompt template.

## Expected Output
- A fully-formed prompt string ready to send to an LLM via `ai/llm`.

## Future Integration
Consumed exclusively by `ai/llm`. No other module should read
prompt templates directly, keeping prompt logic in one place.

No implementation exists yet.
