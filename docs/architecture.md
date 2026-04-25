# datasage architecture

## Overview

datasage is a Streamlit-based visual pipeline builder for NLP workflows. It guides users through five sequential stages, applying LLM-powered "recipes" at each step.

## Pipeline stages

```
Ingest → Clean → Extract → Analyze → Export
```

| Stage   | Purpose |
|---------|---------|
| Ingest  | Load raw text (paste or upload) |
| Clean   | Remove noise, normalize formatting |
| Extract | Pull structured information using LLM prompts |
| Analyze | Summarize, classify, or compare |
| Export  | Save results as .txt, .json, or .csv |

## LLM backends

All backends implement the same `LLMClient` interface (`datasage/llm/base.py`):

- `AnthropicClient` — uses the `anthropic` SDK
- `OpenAIClient` — uses the `openai` SDK
- `OllamaClient` — uses the `ollama` SDK (local models)

The active backend is selected at config time and stored in `~/.datasage/config.yaml`.

## Recipes

Recipes are prompt templates stored in `datasage/pipeline/recipes.py`. Each recipe belongs to a stage and contains a `{text}` placeholder that is replaced with the user's current input at runtime. Users can also write custom prompts.

## Config

Config is stored at `~/.datasage/config.yaml`:

```yaml
backend: anthropic        # anthropic | openai | ollama
api_key: "sk-..."
model: claude-opus-4-6
ollama_host: http://localhost:11434
```

On first launch, datasage shows a setup wizard if no config file exists.
