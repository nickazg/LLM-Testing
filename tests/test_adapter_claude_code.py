from llm_bench.adapters.claude_code import ClaudeCodeAdapter


def test_build_command():
    adapter = ClaudeCodeAdapter(model="opus")
    cmd = adapter.build_command("Fix the bug in main.py")
    assert cmd[0] == "claude"
    assert "-p" in cmd
    assert "--model" in cmd
    assert "opus" in cmd
    assert "--output-format" in cmd
    assert "json" in cmd
    assert "--allowedTools" in cmd


def test_build_command_with_env_file():
    adapter = ClaudeCodeAdapter(model="qwen3-30b", env_file="/path/to/.env.qwen")
    assert adapter.env_file == "/path/to/.env.qwen"


def test_parse_json_output():
    adapter = ClaudeCodeAdapter(model="opus")
    raw = """{
        "type": "result",
        "subtype": "success",
        "result": "Done. Created hello.py.",
        "session_id": "abc-123",
        "total_cost_usd": 0.05,
        "num_turns": 3,
        "duration_ms": 15000,
        "usage": {
            "input_tokens": 2000,
            "output_tokens": 500,
            "cache_read_input_tokens": 100
        }
    }"""
    parsed = adapter.parse_output(raw)
    assert parsed.tokens == 2500
    assert parsed.cost_usd == 0.05
    assert parsed.exit_code == 0
    assert "Done" in parsed.stdout


def test_parse_json_output_error():
    adapter = ClaudeCodeAdapter(model="opus")
    raw = """{
        "type": "result",
        "subtype": "error",
        "result": "Failed to complete task",
        "total_cost_usd": 0.02,
        "num_turns": 1,
        "duration_ms": 5000,
        "usage": {
            "input_tokens": 500,
            "output_tokens": 100
        }
    }"""
    parsed = adapter.parse_output(raw)
    assert parsed.exit_code == 1
    assert "Failed" in parsed.stdout
