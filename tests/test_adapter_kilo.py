from llm_bench.adapters.kilo import KiloAdapter


def test_build_command():
    adapter = KiloAdapter(model="anthropic/claude-sonnet-4-20250514")
    cmd = adapter.build_command("Fix the bug")
    assert cmd[0] == "kilo"
    assert "run" in cmd
    assert "--auto" in cmd
    assert "--json" in cmd


def test_parse_output():
    adapter = KiloAdapter(model="test")
    output = adapter.parse_output('{"type": "assistant", "content": "Done."}')
    assert output.exit_code == 0
    assert "Done." in output.stdout
