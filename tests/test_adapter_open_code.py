from llm_bench.adapters.open_code import OpenCodeAdapter


def test_build_command():
    adapter = OpenCodeAdapter(model="anthropic/claude-sonnet-4-20250514")
    cmd = adapter.build_command("Fix the bug")
    assert cmd[0] == "opencode"
    assert "run" in cmd
    assert "--model" in cmd
    assert "--format" in cmd
    assert "json" in cmd


def test_parse_output_text():
    adapter = OpenCodeAdapter(model="test")
    output = adapter.parse_output('{"result": "Done fixing the bug."}')
    assert output.exit_code == 0
    assert "Done fixing" in output.stdout
