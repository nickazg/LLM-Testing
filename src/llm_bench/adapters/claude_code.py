from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from llm_bench.adapters.base import CLIAdapter, CLIOutput


class ClaudeCodeAdapter(CLIAdapter):
    name = "claude-code"

    def build_command(self, prompt: str) -> list[str]:
        return [
            "claude",
            "-p", prompt,
            "--model", self.model,
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
                exit_code=1, wall_time_s=0,
            )

        usage = data.get("usage", {})
        tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        is_error = data.get("subtype") == "error"

        return CLIOutput(
            stdout=data.get("result", ""),
            stderr="" if not is_error else data.get("result", ""),
            exit_code=1 if is_error else 0,
            wall_time_s=data.get("duration_ms", 0) / 1000.0,
            tokens=tokens,
            tool_calls=data.get("num_turns", 0),
            cost_usd=data.get("total_cost_usd", 0.0),
        )

    async def run(self, prompt: str, cwd: str | Path, timeout: int = 300) -> CLIOutput:
        cmd = self.build_command(prompt)
        env = self._load_env()

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
