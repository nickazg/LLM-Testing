"""Tests for the DSPy skill compiler module.

Tests SkillDocument, build_failure_analysis, and CLI wiring without
requiring DSPy installed (DSPy-dependent functions are tested with mocks).
"""
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from llm_bench.compiler import (
    SkillDocument,
    SkillSection,
    build_failure_analysis,
    proxy_metric,
)


# --- SkillDocument tests ---

def test_skill_document_to_markdown():
    doc = SkillDocument(
        title="USD Shot Assembly",
        sections=[
            SkillSection(heading="Stage Setup", content="```python\nstage = Usd.Stage.CreateNew('f.usda')\n```"),
            SkillSection(heading="Variants", content="Use `GetVariantEditContext()`."),
        ],
    )
    md = doc.to_markdown()
    assert md.startswith("# USD Shot Assembly")
    assert "## Stage Setup" in md
    assert "## Variants" in md
    assert "GetVariantEditContext" in md


def test_skill_document_from_markdown():
    md = """# My Skill

## Section One

Some content here.

## Section Two

```python
code_here()
```
"""
    doc = SkillDocument.from_markdown(md)
    assert doc.title == "My Skill"
    assert len(doc.sections) == 2
    assert doc.sections[0].heading == "Section One"
    assert doc.sections[1].heading == "Section Two"
    assert "code_here()" in doc.sections[1].content


def test_skill_document_roundtrip():
    original = SkillDocument(
        title="Test Skill",
        sections=[
            SkillSection(heading="A", content="Content A"),
            SkillSection(heading="B", content="Content B"),
        ],
    )
    md = original.to_markdown()
    parsed = SkillDocument.from_markdown(md)
    assert parsed.title == original.title
    assert len(parsed.sections) == len(original.sections)
    assert parsed.sections[0].heading == "A"
    assert parsed.sections[1].heading == "B"


# --- build_failure_analysis tests ---

def test_build_failure_analysis_with_results():
    results = [
        {
            "task_id": "tier3-usd-shot-assembly",
            "model": "glm-4.5-air-free",
            "cli": "claude-code",
            "skill": "usd-composition",
            "scores": {"correctness": 0.2},
            "raw_output": "Error: GetPrototypeStage is not defined",
            "files": [{"content": "stage.GetPrototypeStage()"}],
        },
        {
            "task_id": "tier3-usd-shot-assembly",
            "model": "glm-4.5-air-free",
            "cli": "kilo",
            "skill": None,
            "scores": {"correctness": 0.8},
            "raw_output": "Success",
            "files": [],
        },
    ]
    analysis = build_failure_analysis(results, "tier3-usd-shot-assembly", "glm-4.5-air-free")
    assert "correctness=0.2" in analysis
    assert "correctness=0.8" in analysis
    assert "GetPrototypeStage" in analysis


def test_build_failure_analysis_no_results():
    analysis = build_failure_analysis([], "nonexistent-task", "nonexistent-model")
    assert "No previous results" in analysis


# --- proxy_metric tests ---

def test_proxy_metric_good_skill():
    example = type("Ex", (), {"current_skill": "something different"})()
    pred = type("Pred", (), {"optimized_skill": """# USD Hints

## Stage Setup

```python
stage = Usd.Stage.CreateNew("f.usda")
stage.DefinePrim("/Root", "Xform")
```

## Variants

```python
vset = prim.GetVariantSets().AddVariantSet("myVar")
with vset.GetVariantEditContext():
    child = stage.DefinePrim("/A/B", "Xform")
```

## Transforms

```python
UsdGeom.Xformable(prim).AddTranslateOp().Set(Gf.Vec3d(1,0,0))
stage.GetRootLayer().Save()
```
"""})()
    score = proxy_metric(example, pred)
    assert score >= 0.6  # Should be a good score


def test_proxy_metric_empty_skill():
    example = type("Ex", (), {"current_skill": "x"})()
    pred = type("Pred", (), {"optimized_skill": ""})()
    assert proxy_metric(example, pred) == 0.0


def test_proxy_metric_bootstrap_mode():
    example = type("Ex", (), {"current_skill": "x"})()
    pred = type("Pred", (), {"optimized_skill": ""})()
    # trace is not None → bootstrap mode → returns bool
    assert proxy_metric(example, pred, trace="bootstrap") is False


# --- CLI wiring test ---

def test_compile_skill_help():
    result = subprocess.run(
        [sys.executable, "-m", "llm_bench.cli", "compile-skill", "--help"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0
    assert "--skill" in result.stdout
    assert "--target-model" in result.stdout
    assert "--teacher-model" in result.stdout
    assert "--output-variant" in result.stdout
    assert "--metric" in result.stdout


# --- configure_dspy_lm test (mocked) ---

def test_configure_dspy_lm_openrouter(tmp_path):
    """Test that configure_dspy_lm creates LM with correct params."""
    # Set up mock config
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "models.yaml").write_text("""
defaults:
  provider: openrouter
models:
  glm-4.5-air-free:
    name: GLM 4.5 Air Free
    provider: openrouter
    openrouter_id: zhipu-ai/glm-4.5-air-free
""")
    (config_dir / ".env").write_text("OPENROUTER_API_KEY=test-key-123")

    with patch.dict("sys.modules", {"dspy": MagicMock()}):
        import importlib
        # Need to re-import with mocked dspy
        import llm_bench.compiler as compiler_mod
        mock_dspy = sys.modules["dspy"]
        mock_lm = MagicMock()
        mock_dspy.LM.return_value = mock_lm

        result = compiler_mod.configure_dspy_lm("glm-4.5-air-free", config_dir)

        mock_dspy.LM.assert_called_once()
        call_kwargs = mock_dspy.LM.call_args
        assert "openrouter" in call_kwargs[1].get("model", "") or "openrouter" in call_kwargs[0][0]
