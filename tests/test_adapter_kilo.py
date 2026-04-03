from llm_bench.adapters.kilo import KiloAdapter


def test_build_command():
    adapter = KiloAdapter(model="test-model")
    cmd = adapter.build_command("Fix the bug", model_id="openrouter/qwen/qwen3-coder-30b")
    assert cmd[0] == "kilo"
    assert "run" in cmd
    assert "--format" in cmd
    assert "json" in cmd
    assert "--model" in cmd
    assert "openrouter/qwen/qwen3-coder-30b" in cmd
    assert cmd[-1] == "Fix the bug"


def test_parse_output_real_format():
    """Test parsing actual Kilo --format json output."""
    adapter = KiloAdapter(model="test")
    raw = '\n'.join([
        '{"type":"step_start","timestamp":1000,"sessionID":"s1","part":{"type":"step-start"}}',
        '{"type":"text","timestamp":1001,"sessionID":"s1","part":{"type":"text","text":"Hello world!"}}',
        '{"type":"step_finish","timestamp":1002,"sessionID":"s1","part":{"type":"step-finish","reason":"stop","cost":0.001,"tokens":{"total":500,"input":400,"output":100,"reasoning":0,"cache":{"read":50,"write":0}}}}',
    ])
    output = adapter.parse_output(raw)
    assert output.exit_code == 0
    assert "Hello world!" in output.stdout
    assert output.token_usage.input == 400
    assert output.token_usage.output == 100
    assert output.token_usage.cache_read == 50
    assert output.cost_usd == 0.001
    assert len(output.conversation) == 1
    assert output.conversation[0].role == "response"


def test_parse_output_with_tool_use():
    adapter = KiloAdapter(model="test")
    raw = '\n'.join([
        '{"type":"text","part":{"type":"text","text":"I will create the file."}}',
        '{"type":"tool_call","part":{"tool":"write_to_file","args":{"path":"hello.py","content":"print(1)"}}}',
        '{"type":"tool_result","part":{"tool":"write_to_file","content":"File written"}}',
        '{"type":"text","part":{"type":"text","text":"Done."}}',
        '{"type":"step_finish","part":{"cost":0.002,"tokens":{"total":1000,"input":800,"output":200,"reasoning":50,"cache":{"read":0,"write":0}}}}',
    ])
    output = adapter.parse_output(raw)
    assert "I will create the file." in output.stdout
    assert "Done." in output.stdout
    assert output.token_usage.input == 800
    assert output.token_usage.thinking == 50
    assert len(output.conversation) == 4
    assert output.conversation[1].role == "tool_use"
    assert output.conversation[1].tool_name == "write_to_file"
    assert output.conversation[2].role == "tool_result"


def test_write_kilo_config(tmp_path):
    import json
    adapter = KiloAdapter(model="test")
    adapter._write_kilo_config(tmp_path, "openrouter/qwen/qwen3-coder-30b")
    config = json.loads((tmp_path / "kilo.json").read_text())
    assert config["model"] == "openrouter/qwen/qwen3-coder-30b"
    assert "openrouter" in config["provider"]
