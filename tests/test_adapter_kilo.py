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
    # Prompt should be last
    assert cmd[-1] == "Fix the bug"


def test_build_command_no_model():
    adapter = KiloAdapter(model="test")
    cmd = adapter.build_command("Hello")
    assert "--model" not in cmd
    assert cmd[-1] == "Hello"


def test_parse_output():
    adapter = KiloAdapter(model="test")
    output = adapter.parse_output('{"type": "assistant", "content": "Done."}')
    assert output.exit_code == 0
    assert "Done." in output.stdout


def test_write_kilo_config(tmp_path):
    adapter = KiloAdapter(model="test")
    adapter._write_kilo_config(tmp_path, "openrouter/qwen/qwen3-coder-30b", None)
    import json
    config = json.loads((tmp_path / "kilo.json").read_text())
    assert config["model"] == "openrouter/qwen/qwen3-coder-30b"
    assert "openrouter" in config["provider"]
