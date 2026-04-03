from llm_bench.adapters import get_adapter
from llm_bench.adapters.claude_code import ClaudeCodeAdapter
from llm_bench.adapters.open_code import OpenCodeAdapter
from llm_bench.adapters.kilo import KiloAdapter


def test_get_claude_code_adapter():
    adapter = get_adapter("claude-code", model="opus")
    assert isinstance(adapter, ClaudeCodeAdapter)
    assert adapter.model == "opus"


def test_get_open_code_adapter():
    adapter = get_adapter("open-code", model="test")
    assert isinstance(adapter, OpenCodeAdapter)


def test_get_kilo_adapter():
    adapter = get_adapter("kilo", model="test")
    assert isinstance(adapter, KiloAdapter)


def test_get_unknown_adapter():
    try:
        get_adapter("unknown-cli", model="test")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_env_passed_to_adapter():
    env = {"OPENROUTER_API_KEY": "test-key"}
    adapter = get_adapter("claude-code", model="test", env=env)
    assert adapter._get_env() == env
