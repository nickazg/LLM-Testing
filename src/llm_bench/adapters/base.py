from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from llm_bench.models import TokenUsage


@dataclass
class CLIOutput:
    stdout: str
    stderr: str
    exit_code: int
    wall_time_s: float
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    tool_calls: int = 0
    cost_usd: float = 0.0
    raw_response: str = ""


class CLIAdapter:
    name: str = "base"

    def __init__(self, model: str, env_file: str | None = None):
        self.model = model
        self.env_file = env_file

    def _load_env(self) -> dict | None:
        """Load env file into a copy of the current environment."""
        if not self.env_file:
            return None
        import os
        env_path = Path(self.env_file)
        if not env_path.exists():
            return None
        env = os.environ.copy()
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
        return env

    def _resolve_model_id(self, env: dict | None) -> str:
        """Get the CLI-specific model ID from env, falling back to self.model."""
        if env and "LLM_BENCH_MODEL_ID" in env:
            return env["LLM_BENCH_MODEL_ID"]
        return self.model

    async def run(self, prompt: str, cwd: str | Path, timeout: int = 300) -> CLIOutput:
        raise NotImplementedError

    def build_command(self, prompt: str) -> list[str]:
        raise NotImplementedError
