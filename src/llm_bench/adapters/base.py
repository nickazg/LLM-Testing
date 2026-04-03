from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CLIOutput:
    stdout: str
    stderr: str
    exit_code: int
    wall_time_s: float
    tokens: int = 0
    tool_calls: int = 0
    cost_usd: float = 0.0


class CLIAdapter:
    name: str = "base"

    def __init__(self, model: str):
        self.model = model

    async def run(self, prompt: str, cwd: str | Path, timeout: int = 300) -> CLIOutput:
        raise NotImplementedError

    def build_command(self, prompt: str) -> list[str]:
        raise NotImplementedError
