from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path

from llm_bench.adapters.base import CLIAdapter, CLIOutput


class KiloAdapter(CLIAdapter):
    name = "kilo"

    def build_command(self, prompt: str) -> list[str]:
        return [
            "kilo",
            "run",
            "--auto",
            "--json",
            prompt,
        ]

    def parse_output(self, raw: str) -> CLIOutput:
        lines = raw.strip().splitlines()
        full_output = []
        for line in lines:
            try:
                msg = json.loads(line)
                if msg.get("type") == "assistant":
                    full_output.append(msg.get("content", ""))
            except json.JSONDecodeError:
                full_output.append(line)

        return CLIOutput(
            stdout="\n".join(full_output), stderr="",
            exit_code=0, wall_time_s=0, raw_response=raw,
        )

    async def run(self, prompt: str, cwd: str | Path, timeout: int = 300) -> CLIOutput:
        cmd = self.build_command(prompt)
        env = self._load_env()

        if env is None:
            env = os.environ.copy()
        env["KILOCODE_MODEL"] = self._resolve_model_id(env)

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
        output.exit_code = proc.returncode or 0
        return output
