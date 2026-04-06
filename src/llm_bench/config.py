"""Centralized config: loads models.yaml + .env for all model/CLI routing."""
from __future__ import annotations

import os
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ModelConfig:
    """Resolved config for a specific model + CLI combination."""
    model_id: str           # Friendly name (e.g. "qwen3-30b")
    display_name: str       # Human name (e.g. "Qwen3 Coder 30B")
    provider: str           # "openrouter" or "anthropic" or custom
    openrouter_id: str      # e.g. "qwen/qwen3-coder-next"
    env: dict               # Environment vars to pass to subprocess


def _load_dotenv(env_path: Path) -> dict[str, str]:
    """Parse a .env file into a dict."""
    result = {}
    if not env_path.exists():
        return result
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def load_models_config(config_dir: Path) -> dict:
    """Load models.yaml, returns raw dict."""
    yaml_path = config_dir / "models.yaml"
    if not yaml_path.exists():
        return {"defaults": {}, "models": {}}
    with open(yaml_path) as f:
        return yaml.safe_load(f) or {"defaults": {}, "models": {}}


def resolve_model(
    model_id: str,
    cli_name: str,
    config_dir: Path,
) -> ModelConfig:
    """Resolve full config for a model+CLI combo from models.yaml + .env."""
    config = load_models_config(config_dir)
    defaults = config.get("defaults", {})
    models = config.get("models", {})

    model_def = models.get(model_id, {})
    display_name = model_def.get("name", model_id)
    provider = model_def.get("provider", defaults.get("provider", "openrouter"))
    openrouter_id = model_def.get("openrouter_id", "")
    proxy_url = defaults.get("claude_code_proxy", "http://127.0.0.1:3456")

    # Load API keys from config/.env
    keys = _load_dotenv(config_dir / ".env")

    # Start with current env
    env = os.environ.copy()
    env.update(keys)

    # Check for CLI-specific override
    cli_override = model_def.get(cli_name, None)

    # Model-level flags
    if model_def.get("disable_adaptive_thinking"):
        env["CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING"] = "1"

    if cli_name == "claude-code":
        # Check CLI override provider first, fall back to model-level provider
        cc_provider = cli_override.get("provider", provider) if cli_override else provider

        if cli_override and cli_override.get("base_url"):
            # Direct API with custom base URL (e.g. GLM-5 via z.ai)
            base_url = cli_override["base_url"]
            auth_env = cli_override.get("auth_env", "")
            model_override = cli_override.get("model_id", "")
            env["ANTHROPIC_BASE_URL"] = base_url
            if auth_env and auth_env in keys:
                env["ANTHROPIC_AUTH_TOKEN"] = keys[auth_env]
            if model_override:
                env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = model_override
                env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = model_override
                env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = model_override
        elif cc_provider == "openrouter" and openrouter_id:
            # OpenRouter via proxy
            env["ANTHROPIC_BASE_URL"] = proxy_url
            env["ANTHROPIC_AUTH_TOKEN"] = keys.get("OPENROUTER_API_KEY", "")
            or_model = f"openrouter,{openrouter_id}"
            env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = or_model
            env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = or_model
            env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = or_model
        elif cc_provider == "anthropic":
            # Native Anthropic — use model_id override for CC model name
            if cli_override and cli_override.get("model_id"):
                env["LLM_BENCH_CC_MODEL"] = cli_override["model_id"]

    elif cli_name in ("open-code", "kilo"):
        # CLI override can change provider (e.g. GLM via z-ai direct on Kilo)
        cli_provider = cli_override.get("provider", provider) if cli_override else provider

        if cli_provider == "openrouter" and openrouter_id:
            env["OPENROUTER_API_KEY"] = keys.get("OPENROUTER_API_KEY", "")
            env["LLM_BENCH_MODEL_ID"] = f"openrouter/{openrouter_id}"
            env["LLM_BENCH_KILO_PROVIDER"] = "openrouter"
        elif cli_provider in ("z-ai", "openai", "google", "anthropic"):
            # Direct provider routing
            model_id_kilo = cli_override.get("model_id", "") if cli_override else ""
            auth_env_key = cli_override.get("auth_env", "") if cli_override else ""
            if auth_env_key:
                env["LLM_BENCH_PROVIDER_API_KEY"] = keys.get(auth_env_key, "")
            env["LLM_BENCH_MODEL_ID"] = model_id_kilo
            env["LLM_BENCH_KILO_PROVIDER"] = cli_provider

    return ModelConfig(
        model_id=model_id,
        display_name=display_name,
        provider=provider,
        openrouter_id=openrouter_id,
        env=env,
    )
