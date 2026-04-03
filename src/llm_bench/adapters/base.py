from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from llm_bench.models import TokenUsage, ConversationMessage


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
    conversation: list[ConversationMessage] = field(default_factory=list)


class CLIAdapter:
    name: str = "base"

    def __init__(self, model: str, env: dict | None = None):
        self.model = model
        self.env = env

    def _get_env(self) -> dict | None:
        """Return the resolved env dict."""
        return self.env

    def _resolve_model_id(self) -> str:
        """Get CLI-specific model ID from env, falling back to self.model."""
        if self.env and "LLM_BENCH_MODEL_ID" in self.env:
            return self.env["LLM_BENCH_MODEL_ID"]
        return self.model

    async def run(self, prompt: str, cwd: str | Path, timeout: int = 300) -> CLIOutput:
        raise NotImplementedError

    def build_command(self, prompt: str) -> list[str]:
        raise NotImplementedError
