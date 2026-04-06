"""DSPy-based skill compiler — optimizes skill documents for target models.

Usage:
    llm-bench compile-skill --skill usd-composition --target-model glm-4.5-air-free \
        --teacher-model opus --task tier3-usd-shot-assembly --output-variant compiled-glm45

Requires: pip install -e ".[compile]"
"""
from __future__ import annotations

import asyncio
import json
import tempfile
import time
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

# DSPy imported lazily in functions that need it to allow module-level
# imports of SkillDocument/SkillSection without dspy installed.


# ---------------------------------------------------------------------------
# Pydantic schema for structured skill output
# ---------------------------------------------------------------------------

class SkillSection(BaseModel):
    """A single section of a skill document."""
    heading: str = Field(description="Section heading (without ## prefix)")
    content: str = Field(description="Markdown body including code blocks")


class SkillDocument(BaseModel):
    """Structured skill document that renders to markdown."""
    title: str = Field(description="Skill document title (without # prefix)")
    sections: list[SkillSection] = Field(description="Ordered sections")

    def to_markdown(self) -> str:
        """Render to markdown string compatible with .claude/skills/ injection."""
        lines = [f"# {self.title}\n"]
        for s in self.sections:
            lines.append(f"## {s.heading}\n\n{s.content}\n")
        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, md: str) -> SkillDocument:
        """Parse a markdown string back into a SkillDocument."""
        lines = md.strip().split("\n")
        title = ""
        sections: list[SkillSection] = []
        current_heading = ""
        current_content: list[str] = []

        for line in lines:
            if line.startswith("# ") and not line.startswith("## "):
                title = line[2:].strip()
            elif line.startswith("## "):
                if current_heading:
                    sections.append(SkillSection(
                        heading=current_heading,
                        content="\n".join(current_content).strip(),
                    ))
                current_heading = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)

        if current_heading:
            sections.append(SkillSection(
                heading=current_heading,
                content="\n".join(current_content).strip(),
            ))

        return cls(title=title or "Untitled Skill", sections=sections)


# ---------------------------------------------------------------------------
# DSPy LM configuration
# ---------------------------------------------------------------------------

def configure_dspy_lm(
    model_id: str,
    config_dir: Path,
) -> "dspy.LM":
    """Create a dspy.LM from the benchmark's models.yaml + .env config.

    Supports OpenRouter and Anthropic providers.
    """
    import dspy
    from llm_bench.config import load_models_config, _load_dotenv

    config = load_models_config(config_dir)
    defaults = config.get("defaults", {})
    models = config.get("models", {})
    keys = _load_dotenv(config_dir / ".env")

    model_def = models.get(model_id, {})
    provider = model_def.get("provider", defaults.get("provider", "openrouter"))
    openrouter_id = model_def.get("openrouter_id", "")

    if provider == "openrouter" and openrouter_id:
        return dspy.LM(
            model=f"openrouter/{openrouter_id}",
            api_key=keys.get("OPENROUTER_API_KEY", ""),
            max_tokens=4000,
        )
    elif provider == "anthropic":
        return dspy.LM(
            model=f"anthropic/{openrouter_id or model_id}",
            api_key=keys.get("ANTHROPIC_API_KEY", ""),
            max_tokens=4000,
        )
    else:
        # Fallback: try as openrouter with model_id as the identifier
        return dspy.LM(
            model=f"openrouter/{model_id}",
            api_key=keys.get("OPENROUTER_API_KEY", ""),
            max_tokens=4000,
        )


# ---------------------------------------------------------------------------
# Training set construction from benchmark results
# ---------------------------------------------------------------------------

def build_failure_analysis(results: list[dict], task_id: str, model_id: str) -> str:
    """Analyze what a model got wrong on a task from existing results.

    Returns a text summary of failures for the DSPy optimizer to learn from.
    """
    relevant = [
        r for r in results
        if r.get("task_id") == task_id and r.get("model") == model_id
    ]

    if not relevant:
        return "No previous results available for this model+task combination."

    lines = []
    for r in relevant:
        correctness = r.get("scores", {}).get("correctness", 0)
        skill_used = r.get("skill") or "none"
        cli = r.get("cli", "unknown")
        lines.append(f"- {cli} | skill={skill_used} | correctness={correctness}")

        if correctness < 0.5:
            # Extract what went wrong from raw output
            raw = r.get("raw_output", "")
            if raw:
                # Look for error indicators
                for keyword in ["Error", "Traceback", "FAIL", "incorrect", "missing"]:
                    for output_line in raw.split("\n"):
                        if keyword.lower() in output_line.lower():
                            lines.append(f"  Error: {output_line.strip()[:200]}")
                            break

            # Check generated files for common issues
            files = r.get("files", [])
            for f in files:
                content = f.get("content", "")
                if "GetPrototypeStage" in content:
                    lines.append("  Issue: Model hallucinated GetPrototypeStage() (doesn't exist)")
                if ".edit()" in content and "GetVariantEditContext" not in content:
                    lines.append("  Issue: Model used .edit() instead of GetVariantEditContext()")

    return "\n".join(lines) if lines else "No failures detected in previous runs."


def build_trainset(
    results_dir: Path,
    task_id: str,
    model_id: str,
    current_skill: str,
) -> list:
    """Build DSPy training examples from existing benchmark results."""
    import dspy
    from llm_bench.results import load_results

    results = load_results(results_dir)
    relevant = [
        r for r in results
        if r.get("task_id") == task_id and r.get("model") == model_id
    ]

    examples = []
    for r in relevant:
        correctness = r.get("scores", {}).get("correctness", 0) or 0
        skill_used = r.get("skill") or "none"
        prompt = r.get("prompt", "")

        examples.append(dspy.Example(
            task_prompt=prompt,
            current_skill=current_skill,
            model_failures=f"correctness={correctness}, skill={skill_used}",
            optimized_skill=current_skill if correctness >= 0.8 else "",
        ).with_inputs("task_prompt", "current_skill", "model_failures"))

    return examples


# ---------------------------------------------------------------------------
# DSPy Signature and Module
# ---------------------------------------------------------------------------

def _get_signature():
    """Return DSPy signature class (deferred import)."""
    import dspy

    class OptimizeSkill(dspy.Signature):
        """Optimize a coding skill document so a weaker model can use it effectively.

        The current skill may be too verbose, contain irrelevant examples, or use
        patterns the target model can't synthesize. Produce a focused, minimal skill
        that only includes what the model needs for this specific task.
        """
        task_prompt: str = dspy.InputField(
            desc="The exact coding task the model must complete"
        )
        current_skill: str = dspy.InputField(
            desc="Current skill document that may be too complex for the target model"
        )
        model_failures: str = dspy.InputField(
            desc="Analysis of what the target model got wrong with the current skill"
        )
        optimized_skill: str = dspy.OutputField(
            desc="Simplified, task-focused skill markdown with only essential API patterns"
        )

    return OptimizeSkill


def _get_compiler_module():
    """Return DSPy SkillCompiler module (deferred import)."""
    import dspy

    OptimizeSkill = _get_signature()

    class SkillCompiler(dspy.Module):
        def __init__(self):
            super().__init__()
            self.optimize = dspy.ChainOfThought(OptimizeSkill)

        def forward(self, task_prompt, current_skill, model_failures):
            return self.optimize(
                task_prompt=task_prompt,
                current_skill=current_skill,
                model_failures=model_failures,
            )

    return SkillCompiler


# ---------------------------------------------------------------------------
# Metric functions
# ---------------------------------------------------------------------------

def proxy_metric(example, pred, trace=None):
    """Fast proxy metric — evaluates skill quality heuristically.

    Scores on: structure, conciseness, code examples, API coverage.
    In bootstrap mode (trace is not None), returns bool for threshold.
    In evaluation mode, returns float 0-1.
    """
    skill = pred.optimized_skill if hasattr(pred, "optimized_skill") else ""

    if not skill or len(skill) < 20:
        return False if trace is not None else 0.0

    score = 0.0
    # Has markdown structure
    if "## " in skill or "# " in skill:
        score += 0.2
    # Has code examples
    if "```" in skill:
        score += 0.2
    # Is concise (20-80 lines is ideal for weak models)
    line_count = len(skill.strip().split("\n"))
    if 10 <= line_count <= 80:
        score += 0.2
    elif line_count < 10:
        score += 0.1  # Too short
    # Contains key API patterns
    api_patterns = [
        "GetVariantEditContext", "AddVariantSet", "AddTranslateOp",
        "DefinePrim", "CreateNew", "Save",
    ]
    pattern_hits = sum(1 for p in api_patterns if p in skill)
    score += min(0.2, pattern_hits * 0.04)
    # Not too similar to input (actually optimized)
    if hasattr(example, "current_skill") and skill != example.current_skill:
        score += 0.2

    if trace is not None:
        return score >= 0.6
    return min(1.0, score)


def make_live_metric(
    task_id: str,
    target_model: str,
    cli_name: str,
    skills_dir: Path,
    config_dir: Path,
):
    """Create a live metric that actually runs the benchmark.

    Returns a metric function that:
    1. Writes candidate skill to a temp file
    2. Runs the target model with that skill through the benchmark
    3. Returns the validator's correctness score
    """
    def live_metric(example, pred, trace=None):
        from llm_bench.loader import load_tasks
        from llm_bench.runner import run_single_task

        skill_content = pred.optimized_skill if hasattr(pred, "optimized_skill") else ""
        if not skill_content or len(skill_content) < 20:
            return False if trace is not None else 0.0

        # Write candidate skill to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, prefix="dspy-skill-"
        ) as f:
            f.write(skill_content)
            temp_skill_path = Path(f.name)

        try:
            # Load the task config
            tasks_dir = skills_dir.parent / "tasks"
            tasks = load_tasks(tasks_dir, task_ids=[task_id])
            if not tasks:
                return False if trace is not None else 0.0
            task = tasks[0]

            # Run the benchmark with candidate skill (override the resolved path)
            result = asyncio.run(run_single_task(
                task=task,
                cli_name=cli_name,
                model=target_model,
                skills_dir=skills_dir,
                config_dir=config_dir,
                skill_path_override=temp_skill_path,
            ))

            correctness = result.scores.correctness or 0.0
            if trace is not None:
                return correctness >= 0.5
            return correctness

        except Exception as e:
            print(f"  Live metric error: {e}")
            return False if trace is not None else 0.0
        finally:
            temp_skill_path.unlink(missing_ok=True)

    return live_metric


# ---------------------------------------------------------------------------
# Main compilation orchestrator
# ---------------------------------------------------------------------------

@dataclass
class CompileResult:
    """Result of a skill compilation run."""
    output_path: Path
    score: float
    iterations: int
    duration_s: float


def compile_skill(
    skill_domain: str,
    target_model: str,
    teacher_model: str,
    task_id: str,
    skills_dir: Path,
    results_dir: Path,
    config_dir: Path,
    output_variant: str,
    metric_mode: str = "proxy",
    num_iterations: int = 10,
    cli_name: str = "claude-code",
    log=print,
) -> CompileResult:
    """Compile an optimized skill variant using DSPy.

    Args:
        skill_domain: Skill domain (e.g., 'usd-composition')
        target_model: Model to optimize for (e.g., 'glm-4.5-air-free')
        teacher_model: Strong model for optimization (e.g., 'opus')
        task_id: Task to optimize against (e.g., 'tier3-usd-shot-assembly')
        skills_dir: Path to skills/ directory
        results_dir: Path to results/ directory
        config_dir: Path to config/ directory
        output_variant: Name for output variant (e.g., 'compiled-glm45')
        metric_mode: 'proxy' (fast heuristic) or 'live' (runs benchmark)
        num_iterations: Number of optimization iterations
        cli_name: CLI to use for live metric (default: claude-code)
        log: Logging function

    Returns:
        CompileResult with output path and metadata
    """
    import dspy
    from dspy.teleprompt import BootstrapFewShot
    from llm_bench.runner import resolve_skill_path
    from llm_bench.results import load_results

    start_time = time.monotonic()

    # 1. Load current skill content
    log(f"Loading skill: {skill_domain}")
    skill_path = resolve_skill_path(skills_dir, skill_domain)
    if not skill_path:
        raise FileNotFoundError(f"Skill not found: {skill_domain}")
    current_skill = skill_path.read_text()
    log(f"  Current skill: {skill_path.name} ({len(current_skill.splitlines())} lines)")

    # 2. Load existing results for failure analysis
    log(f"Analyzing failures for {target_model} on {task_id}...")
    results = load_results(results_dir)
    failure_analysis = build_failure_analysis(results, task_id, target_model)
    log(f"  {failure_analysis.count(chr(10)) + 1} lines of failure data")

    # 3. Configure DSPy LMs
    log(f"Configuring models...")
    log(f"  Teacher: {teacher_model}")
    log(f"  Target:  {target_model}")
    teacher_lm = configure_dspy_lm(teacher_model, config_dir)
    dspy.configure(lm=teacher_lm)

    # 4. Build training set
    trainset = build_trainset(results_dir, task_id, target_model, current_skill)
    if not trainset:
        # Create a minimal synthetic example if no results exist
        log("  No existing results — using synthetic training example")
        trainset = [dspy.Example(
            task_prompt="(see task prompt in current_skill context)",
            current_skill=current_skill,
            model_failures=failure_analysis,
            optimized_skill="",
        ).with_inputs("task_prompt", "current_skill", "model_failures")]

    # 5. Select metric
    if metric_mode == "live":
        log(f"Using LIVE metric (running {target_model} per iteration — this will be slow)")
        metric = make_live_metric(task_id, target_model, cli_name, skills_dir, config_dir)
    else:
        log(f"Using PROXY metric (heuristic evaluation)")
        metric = proxy_metric

    # 6. Run optimization
    log(f"Starting BootstrapFewShot optimization ({num_iterations} max rounds)...")
    SkillCompiler = _get_compiler_module()
    compiler = SkillCompiler()

    optimizer = BootstrapFewShot(
        metric=metric,
        max_bootstrapped_demos=min(4, len(trainset)),
        max_labeled_demos=min(4, len(trainset)),
        max_rounds=num_iterations,
    )

    optimized = optimizer.compile(
        student=compiler,
        trainset=trainset,
    )

    # 7. Generate the optimized skill
    log("Generating optimized skill with compiled program...")

    # Find a task prompt from results or trainset
    task_prompt = ""
    for r in results:
        if r.get("task_id") == task_id:
            task_prompt = r.get("prompt", "")
            break
    if not task_prompt and trainset:
        task_prompt = trainset[0].task_prompt

    result = optimized(
        task_prompt=task_prompt,
        current_skill=current_skill,
        model_failures=failure_analysis,
    )

    optimized_skill = result.optimized_skill
    log(f"  Generated skill: {len(optimized_skill.splitlines())} lines")

    # 8. Validate with Pydantic schema
    try:
        doc = SkillDocument.from_markdown(optimized_skill)
        # Re-render for consistent formatting
        optimized_skill = doc.to_markdown()
        log(f"  Validated: {doc.title} ({len(doc.sections)} sections)")
    except Exception as e:
        log(f"  Warning: could not parse as SkillDocument ({e}), using raw output")

    # 9. Score the result
    final_score = proxy_metric(
        type("Ex", (), {"current_skill": current_skill})(),
        type("Pred", (), {"optimized_skill": optimized_skill})(),
    )
    log(f"  Proxy score: {final_score:.2f}")

    # 10. Write output
    output_path = skills_dir / skill_domain / f"{output_variant}.md"
    output_path.write_text(optimized_skill)
    log(f"  Written to: {output_path}")

    # 11. Update VARIANTS.yaml
    variants_path = skills_dir / skill_domain / "VARIANTS.yaml"
    if variants_path.exists():
        meta = yaml.safe_load(variants_path.read_text()) or {}
    else:
        meta = {"default": "reference", "variants": {}}

    if "variants" not in meta:
        meta["variants"] = {}
    meta["variants"][output_variant] = {
        "description": f"DSPy-compiled for {target_model} (score={final_score:.2f})"
    }
    variants_path.write_text(yaml.dump(meta, default_flow_style=False, sort_keys=False))
    log(f"  Updated VARIANTS.yaml")

    # 12. Save compilation cache
    cache_dir = skills_dir / skill_domain / ".compile-cache" / output_variant
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_config = {
        "skill_domain": skill_domain,
        "target_model": target_model,
        "teacher_model": teacher_model,
        "task_id": task_id,
        "metric_mode": metric_mode,
        "num_iterations": num_iterations,
        "final_score": final_score,
        "output_lines": len(optimized_skill.splitlines()),
    }
    (cache_dir / "config.yaml").write_text(
        yaml.dump(cache_config, default_flow_style=False)
    )

    duration = time.monotonic() - start_time
    log(f"\nCompilation complete in {duration:.1f}s")

    return CompileResult(
        output_path=output_path,
        score=final_score,
        iterations=num_iterations,
        duration_s=duration,
    )
