from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path

from llm_bench.adapters.base import CLIAdapter, CLIOutput
from llm_bench.models import TokenUsage, ConversationMessage


class KiloAdapter(CLIAdapter):
    name = "kilo"

    def build_command(self, prompt: str, model_id: str | None = None, skip_model_flag: bool = False) -> list[str]:
        cmd = [
            "kilo",
            "run",
            "--auto",
            "--format", "json",
        ]
        if model_id and not skip_model_flag:
            cmd += ["--model", model_id]
        cmd.append(prompt)
        return cmd

    # Provider config templates for kilo.json
    # Note: z-ai is registered in Kilo's global config (~/.config/kilo/kilo.jsonc)
    # so it's NOT listed here — we just set the model and let global config handle auth
    _PROVIDER_CONFIGS = {
        "openrouter": lambda env: {
            "openrouter": {"env": ["OPENROUTER_API_KEY"]}
        },
        "openai": lambda env: {
            "openai": {"options": {
                "apiKey": env.get("LLM_BENCH_PROVIDER_API_KEY", ""),
                **({"baseUrl": env["LLM_BENCH_PROVIDER_BASE_URL"]} if env.get("LLM_BENCH_PROVIDER_BASE_URL") else {}),
            }}
        },
        "google": lambda env: {
            "google": {"options": {"apiKey": env.get("LLM_BENCH_PROVIDER_API_KEY", "")}}
        },
        "anthropic": lambda env: {
            "anthropic": {"options": {"apiKey": env.get("LLM_BENCH_PROVIDER_API_KEY", "")}}
        },
    }

    def _write_kilo_config(self, cwd: Path, model_id: str):
        env = self._get_env() or {}
        provider_name = env.get("LLM_BENCH_KILO_PROVIDER", "openrouter")

        # For providers registered in Kilo's global config (e.g. z-ai),
        # only set the model — don't write a provider block that would
        # override the global config's API keys
        if provider_name not in self._PROVIDER_CONFIGS:
            config = {"model": model_id}
        else:
            provider_factory = self._PROVIDER_CONFIGS.get(
                provider_name, self._PROVIDER_CONFIGS["openrouter"]
            )
            config = {
                "model": model_id,
                "provider": provider_factory(env),
            }
        (Path(cwd) / "kilo.json").write_text(json.dumps(config, indent=2))

    @staticmethod
    def ensure_kilo_token():
        """Ensure kilocodeToken exists in secrets.json.

        Kilo CLI --auto mode hangs without this token, even when using
        OpenRouter. The token doesn't need to be valid — just present.
        See: https://github.com/Kilo-Org/kilocode/issues/3668
        """
        secrets_dir = Path.home() / ".kilocode" / "cli" / "global"
        secrets_file = secrets_dir / "secrets.json"

        if secrets_file.exists():
            try:
                data = json.loads(secrets_file.read_text())
                if data.get("kilocodeToken"):
                    return  # Already set
            except (json.JSONDecodeError, KeyError):
                data = {}
        else:
            secrets_dir.mkdir(parents=True, exist_ok=True)
            data = {}

        data["kilocodeToken"] = "llm-bench-placeholder"
        secrets_file.write_text(json.dumps(data, indent=2))

    def parse_output(self, raw: str) -> CLIOutput:
        conversation: list[ConversationMessage] = []
        token_usage = TokenUsage()
        cost_usd = 0.0
        final_text = []

        for line in raw.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type", "")
            part = msg.get("part", {})

            if msg_type == "text":
                text = part.get("text", "")
                if text:
                    final_text.append(text)
                    conversation.append(ConversationMessage(role="response", content=text))

            elif msg_type in ("tool_call", "tool_use"):
                tool_name = part.get("tool", "unknown")
                state = part.get("state", {})
                tool_input = state.get("input", part.get("args", part.get("input", {})))
                tool_output = state.get("output", "")
                if isinstance(tool_input, dict):
                    tool_input = json.dumps(tool_input, indent=2)
                conversation.append(ConversationMessage(
                    role="tool_use", content=str(tool_input), tool_name=tool_name,
                ))
                if tool_output:
                    conversation.append(ConversationMessage(
                        role="tool_result", content=str(tool_output)[:2000], tool_name=tool_name,
                    ))

            elif msg_type == "tool_result":
                content = part.get("content", part.get("text", ""))
                if isinstance(content, list):
                    content = "\n".join(b.get("text", "") for b in content if isinstance(b, dict))
                conversation.append(ConversationMessage(
                    role="tool_result", content=str(content)[:2000], tool_name=part.get("tool", ""),
                ))

            elif msg_type == "thinking":
                text = part.get("text", part.get("thinking", ""))
                if text:
                    conversation.append(ConversationMessage(role="thinking", content=text))

            elif msg_type == "error":
                error = msg.get("error", {})
                error_msg = error.get("data", {}).get("message", error.get("name", "Unknown error"))
                conversation.append(ConversationMessage(role="error", content=error_msg))
                return CLIOutput(
                    stdout=error_msg, stderr=error_msg,
                    exit_code=1, wall_time_s=0,
                    raw_response=raw, conversation=conversation,
                )

            elif msg_type == "step_finish":
                tokens = part.get("tokens", {})
                token_usage = TokenUsage(
                    input=tokens.get("input", 0),
                    output=tokens.get("output", 0),
                    thinking=tokens.get("reasoning", 0),
                    cache_read=tokens.get("cache", {}).get("read", 0),
                )
                cost_usd += part.get("cost", 0.0)

        return CLIOutput(
            stdout="\n".join(final_text), stderr="",
            exit_code=0, wall_time_s=0,
            token_usage=token_usage, cost_usd=cost_usd,
            raw_response=raw, conversation=conversation,
        )

    async def run(self, prompt: str, cwd: str | Path, timeout: int = 300) -> CLIOutput:
        self.ensure_kilo_token()

        env = self._get_env()
        if env is None:
            env = os.environ.copy()

        model_id = self._resolve_model_id()
        # Skip --model flag for custom providers (model set in kilo.json instead)
        skip_model_flag = self.env and self.env.get("LLM_BENCH_KILO_PROVIDER") not in (None, "", "openrouter")
        cmd = self.build_command(prompt, model_id=model_id, skip_model_flag=skip_model_flag)
        self._write_kilo_config(cwd, model_id)

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
