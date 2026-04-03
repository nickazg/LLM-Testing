from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from llm_bench.adapters.base import CLIAdapter, CLIOutput
from llm_bench.models import TokenUsage


class ClaudeCodeAdapter(CLIAdapter):
    name = "claude-code"

    def build_command(self, prompt: str, model_override: str | None = None) -> list[str]:
        model = model_override or self.model
        return [
            "claude",
            "-p", prompt,
            "--model", model,
            "--output-format", "json",
            "--allowedTools", "Bash,Read,Write,Edit,Glob,Grep",
            "--no-session-persistence",
        ]

    def parse_output(self, raw: str) -> CLIOutput:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return CLIOutput(
                stdout=raw, stderr="Failed to parse JSON output",
                exit_code=1, wall_time_s=0, raw_response=raw,
            )

        usage = data.get("usage", {})
        token_usage = TokenUsage(
            input=usage.get("input_tokens", 0),
            output=usage.get("output_tokens", 0),
            thinking=usage.get("thinking_tokens", 0),
            cache_read=usage.get("cache_read_input_tokens", 0),
        )
        is_error = data.get("subtype") == "error"

        return CLIOutput(
            stdout=data.get("result", ""),
            stderr="" if not is_error else data.get("result", ""),
            exit_code=1 if is_error else 0,
            wall_time_s=data.get("duration_ms", 0) / 1000.0,
            token_usage=token_usage,
            tool_calls=data.get("num_turns", 0),
            cost_usd=data.get("total_cost_usd", 0.0),
            raw_response=raw,
        )

    async def run(self, prompt: str, cwd: str | Path, timeout: int = 300) -> CLIOutput:
        env = self._load_env()

        # When env file overrides model tiers, pass a valid tier name
        if env and any(k.startswith("ANTHROPIC_DEFAULT_") and k.endswith("_MODEL") for k in env):
            cmd = self.build_command(prompt, model_override="sonnet")
        else:
            cmd = self.build_command(prompt)

        start = time.monotonic()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd),
            env=env,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=10)
            except asyncio.TimeoutError:
                proc.kill()
            elapsed = time.monotonic() - start
            return CLIOutput(
                stdout="", stderr="TIMEOUT",
                exit_code=-1, wall_time_s=elapsed,
            )

        elapsed = time.monotonic() - start
        stdout = stdout_bytes.decode("utf-8", errors="replace")

        output = self.parse_output(stdout)
        output.wall_time_s = elapsed
        return output
