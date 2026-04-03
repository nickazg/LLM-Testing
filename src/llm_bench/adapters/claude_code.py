from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from llm_bench.adapters.base import CLIAdapter, CLIOutput
from llm_bench.models import TokenUsage, ConversationMessage


class ClaudeCodeAdapter(CLIAdapter):
    name = "claude-code"

    def build_command(self, prompt: str, model_override: str | None = None) -> list[str]:
        model = model_override or self.model
        return [
            "claude",
            "-p", prompt,
            "--model", model,
            "--output-format", "stream-json",
            "--verbose",
            "--allowedTools", "Bash,Read,Write,Edit,Glob,Grep",
            "--no-session-persistence",
        ]

    def parse_stream_output(self, raw: str) -> CLIOutput:
        conversation: list[ConversationMessage] = []
        token_usage = TokenUsage()
        cost_usd = 0.0
        num_turns = 0
        final_result = ""
        is_error = False
        duration_ms = 0

        for line in raw.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type", "")

            if msg_type == "assistant":
                content = msg.get("message", {})
                if isinstance(content, dict):
                    for block in content.get("content", []):
                        block_type = block.get("type", "")
                        if block_type == "thinking":
                            conversation.append(ConversationMessage(
                                role="thinking", content=block.get("thinking", ""),
                            ))
                        elif block_type == "text":
                            conversation.append(ConversationMessage(
                                role="response", content=block.get("text", ""),
                            ))
                        elif block_type == "tool_use":
                            conversation.append(ConversationMessage(
                                role="tool_use",
                                content=json.dumps(block.get("input", {}), indent=2),
                                tool_name=block.get("name", "unknown"),
                            ))
                elif isinstance(content, str) and content:
                    conversation.append(ConversationMessage(role="response", content=content))

            elif msg_type == "tool_result":
                content = msg.get("content", "")
                if isinstance(content, list):
                    content = "\n".join(b.get("text", "") for b in content if isinstance(b, dict))
                elif not isinstance(content, str):
                    content = str(content)
                conversation.append(ConversationMessage(
                    role="tool_result", content=content[:2000],
                    tool_name=msg.get("tool_name", ""),
                ))

            elif msg_type == "result":
                final_result = msg.get("result", "")
                is_error = msg.get("subtype") == "error"
                duration_ms = msg.get("duration_ms", 0)
                cost_usd = msg.get("total_cost_usd", 0.0)
                num_turns = msg.get("num_turns", 0)
                usage = msg.get("usage", {})
                token_usage = TokenUsage(
                    input=usage.get("input_tokens", 0),
                    output=usage.get("output_tokens", 0),
                    thinking=usage.get("thinking_tokens", 0),
                    cache_read=usage.get("cache_read_input_tokens", 0),
                )

        return CLIOutput(
            stdout=final_result,
            stderr=final_result if is_error else "",
            exit_code=1 if is_error else 0,
            wall_time_s=duration_ms / 1000.0,
            token_usage=token_usage,
            tool_calls=num_turns,
            cost_usd=cost_usd,
            raw_response=raw,
            conversation=conversation,
        )

    def parse_output(self, raw: str) -> CLIOutput:
        stripped = raw.strip()
        if "\n" not in stripped:
            try:
                data = json.loads(stripped)
                if data.get("type") == "result":
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
            except json.JSONDecodeError:
                pass
        return self.parse_stream_output(raw)

    async def run(self, prompt: str, cwd: str | Path, timeout: int = 300) -> CLIOutput:
        env = self._get_env()

        # When env overrides model tiers, pass a valid tier name
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
            return CLIOutput(stdout="", stderr="TIMEOUT", exit_code=-1, wall_time_s=elapsed)

        elapsed = time.monotonic() - start
        stdout = stdout_bytes.decode("utf-8", errors="replace")
        output = self.parse_stream_output(stdout)
        output.wall_time_s = elapsed
        return output
