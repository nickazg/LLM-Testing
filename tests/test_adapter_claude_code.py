from llm_bench.adapters.claude_code import ClaudeCodeAdapter


def test_build_command():
    adapter = ClaudeCodeAdapter(model="opus")
    cmd = adapter.build_command("Fix the bug in main.py")
    assert cmd[0] == "claude"
    assert "-p" in cmd
    assert "--model" in cmd
    assert "opus" in cmd
    assert "--output-format" in cmd
    assert "stream-json" in cmd
    assert "--allowedTools" in cmd


def test_env_passed_through():
    env = {"ANTHROPIC_BASE_URL": "http://proxy", "OPENROUTER_API_KEY": "test"}
    adapter = ClaudeCodeAdapter(model="qwen3-30b", env=env)
    assert adapter._get_env() == env


def test_parse_single_json_result():
    adapter = ClaudeCodeAdapter(model="opus")
    raw = '{"type":"result","subtype":"success","result":"Done.","total_cost_usd":0.05,"num_turns":3,"duration_ms":15000,"usage":{"input_tokens":2000,"output_tokens":500,"thinking_tokens":100,"cache_read_input_tokens":50}}'
    parsed = adapter.parse_output(raw)
    assert parsed.token_usage.input == 2000
    assert parsed.token_usage.output == 500
    assert parsed.token_usage.thinking == 100
    assert parsed.token_usage.cache_read == 50
    assert parsed.cost_usd == 0.05
    assert parsed.exit_code == 0
    assert "Done" in parsed.stdout


def test_parse_stream_json():
    adapter = ClaudeCodeAdapter(model="opus")
    raw = '\n'.join([
        '{"type":"assistant","message":{"content":[{"type":"thinking","thinking":"Let me think about this..."},{"type":"text","text":"I will create the file."}]}}',
        '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Write","input":{"path":"hello.py","content":"print(\'hello\')"}}]}}',
        '{"type":"tool_result","content":"File written","tool_name":"Write"}',
        '{"type":"result","subtype":"success","result":"Done creating hello.py.","total_cost_usd":0.03,"num_turns":2,"duration_ms":10000,"usage":{"input_tokens":1000,"output_tokens":300,"thinking_tokens":200}}',
    ])
    parsed = adapter.parse_stream_output(raw)
    assert parsed.token_usage.input == 1000
    assert parsed.token_usage.output == 300
    assert parsed.token_usage.thinking == 200
    assert parsed.exit_code == 0
    assert "Done" in parsed.stdout
    assert len(parsed.conversation) == 4
    assert parsed.conversation[0].role == "thinking"
    assert parsed.conversation[1].role == "response"
    assert parsed.conversation[2].role == "tool_use"
    assert parsed.conversation[3].role == "tool_result"


def test_parse_stream_error():
    adapter = ClaudeCodeAdapter(model="opus")
    raw = '{"type":"result","subtype":"error","result":"Failed","total_cost_usd":0.01,"num_turns":0,"duration_ms":2000,"usage":{"input_tokens":500,"output_tokens":50}}'
    parsed = adapter.parse_output(raw)
    assert parsed.exit_code == 1
    assert "Failed" in parsed.stdout
