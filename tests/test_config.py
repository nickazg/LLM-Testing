from pathlib import Path
from llm_bench.config import resolve_model, load_models_config


def _setup_config(tmp_path):
    (tmp_path / "models.yaml").write_text("""
defaults:
  provider: openrouter
  claude_code_proxy: "http://127.0.0.1:3456"

models:
  qwen3-30b:
    name: "Qwen3 Coder 30B"
    openrouter_id: "qwen/qwen3-coder-30b-a3b-instruct"

  opus4.6:
    name: "Opus 4.6"
    provider: anthropic
    openrouter_id: "anthropic/claude-opus-4-6"

  glm-5:
    name: "GLM-5"
    openrouter_id: "zhipu/glm-5"
    claude-code:
      base_url: "https://api.z.ai/api/anthropic"
      auth_env: "GLM_API_KEY"
      model_id: "glm-5"
""")
    (tmp_path / ".env").write_text("""
OPENROUTER_API_KEY=test-or-key
ANTHROPIC_API_KEY=test-ant-key
GLM_API_KEY=test-glm-key
""")
    return tmp_path


def test_load_models_config(tmp_path):
    _setup_config(tmp_path)
    config = load_models_config(tmp_path)
    assert "qwen3-30b" in config["models"]
    assert config["models"]["qwen3-30b"]["name"] == "Qwen3 Coder 30B"


def test_resolve_openrouter_model_for_claude_code(tmp_path):
    _setup_config(tmp_path)
    mc = resolve_model("qwen3-30b", "claude-code", tmp_path)
    assert mc.env["ANTHROPIC_BASE_URL"] == "http://127.0.0.1:3456"
    assert mc.env["ANTHROPIC_AUTH_TOKEN"] == "test-or-key"
    assert mc.env["ANTHROPIC_DEFAULT_SONNET_MODEL"] == "openrouter,qwen/qwen3-coder-30b-a3b-instruct"


def test_resolve_openrouter_model_for_kilo(tmp_path):
    _setup_config(tmp_path)
    mc = resolve_model("qwen3-30b", "kilo", tmp_path)
    assert mc.env["OPENROUTER_API_KEY"] == "test-or-key"
    assert mc.env["LLM_BENCH_MODEL_ID"] == "openrouter/qwen/qwen3-coder-30b-a3b-instruct"


def test_resolve_anthropic_native_for_claude_code(tmp_path):
    _setup_config(tmp_path)
    mc = resolve_model("opus4.6", "claude-code", tmp_path)
    # Native Anthropic — no routing env vars
    assert "ANTHROPIC_DEFAULT_SONNET_MODEL" not in mc.env


def test_resolve_glm_direct_api_for_claude_code(tmp_path):
    _setup_config(tmp_path)
    mc = resolve_model("glm-5", "claude-code", tmp_path)
    assert mc.env["ANTHROPIC_BASE_URL"] == "https://api.z.ai/api/anthropic"
    assert mc.env["ANTHROPIC_AUTH_TOKEN"] == "test-glm-key"
    assert mc.env["ANTHROPIC_DEFAULT_SONNET_MODEL"] == "glm-5"
