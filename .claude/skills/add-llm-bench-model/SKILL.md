---
name: add-llm-bench-model
description: Use when adding a new model to the llm-bench benchmarking suite. Updates models.yaml and optionally config/.env.
---

# Adding a Model to LLM Bench

Adding a model requires 2 files: `config/models.yaml` (model routing) and `config/.env` (API keys).

## Step 1: Find the OpenRouter Model ID

Search https://openrouter.ai/models for the exact slug. Format: `provider/model-name` (e.g. `qwen/qwen3-coder-next`, `google/gemma-4-31b-it`).

## Step 2: Add to models.yaml

Edit `config/models.yaml` and add the model under `models:`:

```yaml
models:
  my-model-id:                    # Friendly name used on CLI
    name: "Display Name"
    openrouter_id: "provider/model-name"  # Exact OpenRouter slug
```

That's it for most models. The harness auto-routes:
- **Claude Code:** proxy URL + `ANTHROPIC_DEFAULT_*_MODEL` overrides
- **Open Code:** `--model openrouter/{id}` + `OPENROUTER_API_KEY`
- **Kilo CLI:** `kilo.json` + `--model openrouter/{id}` + `OPENROUTER_API_KEY`

### For models with a direct API (not OpenRouter)

Add a CLI-specific override:

```yaml
  glm-5:
    name: "GLM-5"
    openrouter_id: "zhipu/glm-5"          # Fallback for open-code/kilo
    claude-code:                            # Override for claude-code only
      base_url: "https://api.z.ai/api/anthropic"
      auth_env: "GLM_API_KEY"              # Key name in config/.env
      model_id: "glm-5"
```

### For Anthropic-native models

```yaml
  opus4.6:
    name: "Anthropic Opus 4.6"
    provider: anthropic                    # No routing — uses native API
    openrouter_id: "anthropic/claude-opus-4-6"
```

## Step 3: Add API Key (if new provider)

If the model uses a new API key not already in `config/.env`, add it:

```bash
# config/.env
OPENROUTER_API_KEY=sk-or-v1-...
NEW_PROVIDER_KEY=...
```

Most models use `OPENROUTER_API_KEY` which is already there.

## Step 4: Verify

```bash
llm-bench info                    # Model should appear with correct provider/id
llm-bench run --models my-model-id --clis claude-code --tasks tier1-hello-world
```

## Checklist

- [ ] Found exact OpenRouter model ID
- [ ] Added entry to `config/models.yaml`
- [ ] Added API key to `config/.env` (if new provider)
- [ ] Ran `llm-bench info` — model visible
- [ ] Tested with `llm-bench run`
