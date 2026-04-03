---
name: add-llm-bench-model
description: Use when adding a new model to the llm-bench benchmarking suite. Handles model registry, env files for all CLIs, and OpenRouter model ID lookup.
---

# Adding a Model to LLM Bench

Adding a model requires 3 things: register it in the code, create env files for each CLI, and verify it works.

## Step 1: Find the OpenRouter Model ID

Before anything else, find the exact model ID on OpenRouter. This is critical — a wrong ID means silent failures.

Search the web or check https://openrouter.ai/models for the exact slug. The format is `provider/model-name` (e.g. `qwen/qwen3-coder-30b-a3b-instruct`, `google/gemma-4-31b-it`).

**Important:** The model ID varies per CLI:
- **Claude Code:** Uses `openrouter,{provider/model}` in env vars (comma-separated, note the proxy)
- **Open Code:** Uses `openrouter/{provider/model}` in `--model` flag (slash-separated)
- **Kilo CLI:** Uses `openrouter/{provider/model}` in `--model` flag and `kilo.json`

## Step 2: Register the Model

Add the model to the `MODELS` dict in `src/llm_bench/cli.py`:

```python
MODELS = {
    # ... existing models ...
    "my-model-id": "Display Name (description)",
}
```

The key (`my-model-id`) is the friendly name used on the command line: `llm-bench run --models my-model-id`

**Naming convention:** lowercase, kebab-case, short. Examples: `qwen3-30b`, `gemma-4-31b`, `opus4.6`

## Step 3: Create Env Files

Create one env file per CLI in `config/`. Naming: `config/{cli-name}.{model-id}.env`

### Claude Code (via OpenRouter proxy)

```
config/claude-code.{model-id}.env
```

```bash
# Claude Code — {Model Name} via OpenRouter
ANTHROPIC_BASE_URL=http://127.0.0.1:3456
ANTHROPIC_AUTH_TOKEN={openrouter-api-key}

ANTHROPIC_DEFAULT_HAIKU_MODEL="openrouter,{provider/model-name}"
ANTHROPIC_DEFAULT_SONNET_MODEL="openrouter,{provider/model-name}"
ANTHROPIC_DEFAULT_OPUS_MODEL="openrouter,{provider/model-name}"
```

All three `ANTHROPIC_DEFAULT_*_MODEL` vars must be set to the same value — this overrides every model tier to route to the target model. The adapter passes `--model sonnet` to Claude Code so the `SONNET` override takes effect.

**Note:** If the model has its own API (not OpenRouter), use that provider's base URL and auth token instead. See `config/claude-code.glm-5.env` for an example using a direct API.

### Open Code (via OpenRouter)

```
config/open-code.{model-id}.env
```

```bash
# Open Code — {Model Name} via OpenRouter
OPENROUTER_API_KEY={openrouter-api-key}
LLM_BENCH_MODEL_ID=openrouter/{provider/model-name}
```

`LLM_BENCH_MODEL_ID` is read by the harness and passed to `opencode run --model {value}`.

### Kilo CLI (via OpenRouter)

```
config/kilo.{model-id}.env
```

```bash
# Kilo CLI — {Model Name} via OpenRouter
OPENROUTER_API_KEY={openrouter-api-key}
LLM_BENCH_MODEL_ID=openrouter/{provider/model-name}
```

The adapter also writes a `kilo.json` into the workspace with the provider config, so the env file just needs the key and model ID.

### For Anthropic-native models (Opus, Sonnet, etc.)

Claude Code doesn't need env overrides — just skip the routing vars or leave the file empty.

Open Code and Kilo use the Anthropic provider directly:

```bash
# config/open-code.opus4.6.env
ANTHROPIC_API_KEY={anthropic-api-key}
LLM_BENCH_MODEL_ID=anthropic/claude-opus-4-6
```

## Step 4: Verify

Run `llm-bench info` to check:
- Model appears in the MODELS section
- Env files show as `[ready]` (not `[needs key]`)

Then test with a quick run:

```bash
llm-bench run --models {model-id} --clis claude-code --tasks tier1-hello-world
```

Check the dashboard for the result. If it fails fast (<5s) with no tokens, the env/routing is misconfigured.

## Known Compatibility Issues

Not all models work with all CLIs:
- **Claude Code:** Most models work via OpenRouter proxy. The proxy translates the API format.
- **Open Code:** Requires models that support OpenRouter's tool-calling format.
- **Kilo CLI:** Requires models that support structured tool calls. Models that output XML tool syntax as text (e.g. Qwen3 Coder) will fail to execute tools — this is a valid benchmark finding, not a harness bug.

Record which CLI+model combinations work in the dashboard. Non-working combos are data.

## Checklist

- [ ] Found exact OpenRouter model ID (or direct API endpoint)
- [ ] Added to `MODELS` dict in `src/llm_bench/cli.py`
- [ ] Created `config/claude-code.{id}.env`
- [ ] Created `config/open-code.{id}.env`
- [ ] Created `config/kilo.{id}.env`
- [ ] Ran `llm-bench info` — model and configs visible
- [ ] Tested with `llm-bench run --models {id} --clis claude-code --tasks tier1-hello-world`
- [ ] Verified result in dashboard
