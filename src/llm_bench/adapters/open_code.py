from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from llm_bench.adapters.base import CLIAdapter, CLIOutput


class OpenCodeAdapter(CLIAdapter):
    name = "open-code"

    def build_command(self, prompt: str, model_id: str | None = None) -> list[str]:
        return [
            "opencode",
            "run",
            "--model", model_id or self.model,
            "--format", "json",
            "-q",
            prompt,
        ]

    def parse_output(self, raw: str) -> CLIOutput:
        try:
            data = json.loads(raw)
            result_text = data.get("result", raw)
        except json.JSONDecodeError:
            result_text = raw

        return CLIOutput(
            stdout=result_text, stderr="",
            exit_code=0, wall_time_s=0, raw_response=raw,
        )

    async def run(self, prompt: str, cwd: str | Path, timeout: int = 300) -> CLIOutput:
        env = self._get_env()
        model_id = self._resolve_model_id()
        cmd = self.build_command(prompt, model_id=model_id)

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
            return CLIOutput(stdout="", stderr="TIMEOUT", exit_code=-1, wall_time_s=elapsed)

        elapsed = time.monotonic() - start
        stdout = stdout_bytes.decode("utf-8", errors="replace")
        output = self.parse_output(stdout)
        output.wall_time_s = elapsed
        output.exit_code = proc.returncode or 0
        return output
