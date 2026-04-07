#!/usr/bin/env python3
"""Full benchmark orchestrator: parallel DSPy compilation + benchmark run.

Usage:
    python scripts/full_benchmark.py --phase compile --concurrency 4
    python scripts/full_benchmark.py --phase create-tasks
    python scripts/full_benchmark.py --phase run
    python scripts/full_benchmark.py --phase all --concurrency 4

Checkpoints saved to .claude/benchmark-checkpoint.json — safe to interrupt and resume.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
import time
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
CHECKPOINT_FILE = ROOT / ".claude" / "benchmark-checkpoint.json"
SKILLS_DIR = ROOT / "skills"
TASKS_DIR = ROOT / "tasks"
CONFIG_DIR = ROOT / "config"
RESULTS_DIR = ROOT / "results"

# All heavy skills to compile, mapped to their tier3 training task
SKILLS_HEAVY = {
    # Novel
    "usd-composition": "tier3-usd-shot-assembly",
    "houdini-solaris": "tier3-houdini-solaris",
    "usd-render-settings": "tier3-usd-render-settings",
    "usd-procedural-animation": "tier3-usd-procedural-animation",
    "usd-stage-layers": "tier3-usd-stage-layers",
    "usd-shader-graph": "tier3-usd-shader-graph",
    "usd-custom-schema": "tier3-usd-custom-schema",
    "houdini-pdg": "tier3-houdini-pdg",
    "houdini-solaris-instancing": "tier3-houdini-solaris-instancing",
    "houdini-solaris-render": "tier3-houdini-solaris-render",
    "houdini-solaris-light-linking": "tier3-houdini-solaris-light-linking",
    # Workflow
    "lru-cache-pattern": "tier3-lru-cache",
    "recursive-descent-parser": "tier3-expression-parser",
    # Context
    "git-hook-context-heavy": "tier3-git-hook",
    "service-generator-context-heavy": "tier3-service-generator",
}

# Skill type mapping for task.yaml metadata
SKILL_TYPES = {
    "usd-composition": "novel",
    "houdini-solaris": "novel",
    "usd-render-settings": "novel",
    "usd-procedural-animation": "novel",
    "usd-stage-layers": "novel",
    "usd-shader-graph": "novel",
    "usd-custom-schema": "novel",
    "houdini-pdg": "novel",
    "houdini-solaris-instancing": "novel",
    "houdini-solaris-render": "novel",
    "houdini-solaris-light-linking": "novel",
    "lru-cache-pattern": "workflow",
    "recursive-descent-parser": "workflow",
    "git-hook-context-heavy": "context",
    "service-generator-context-heavy": "context",
}

# Map skill domain -> base task name for skill_pair field
SKILL_PAIRS = {
    "usd-composition": "usd-shot-assembly",
    "houdini-solaris": "houdini-solaris",
    "usd-render-settings": "usd-render-settings",
    "usd-procedural-animation": "usd-procedural-animation",
    "usd-stage-layers": "usd-stage-layers",
    "usd-shader-graph": "usd-shader-graph",
    "usd-custom-schema": "usd-custom-schema",
    "houdini-pdg": "houdini-pdg",
    "houdini-solaris-instancing": "houdini-solaris-instancing",
    "houdini-solaris-render": "houdini-solaris-render",
    "houdini-solaris-light-linking": "houdini-solaris-light-linking",
    "lru-cache-pattern": "lru-cache",
    "recursive-descent-parser": "expression-parser",
    "git-hook-context-heavy": "git-hook",
    "service-generator-context-heavy": "service-generator",
}

ALL_BUDGET_MODELS = [
    "qwen3-30b", "gemma-4-31b", "gemma-4-27b", "devstral",
    "gpt-oss-120b", "gpt-oss-20b", "glm-5", "glm-4.5-air-free",
    "glm-4.7-flash", "minimax-m2.7",
]

TEACHER_MODEL = "glm-5"

# 5 models to compile for (15 skills × 5 = 75 compilations)
COMPILE_MODELS = [
    "qwen3-30b",     # Mid-tier, high variance — compilation could stabilize
    "gemma-4-31b",   # Was 0% CC Phase 2, now works — test if compilation helps
    "gemma-4-27b",   # Small MoE — good test of compilation on small models
    "devstral",      # New, untested on hard tasks
    "glm-4.7-flash", # Weaker GLM, compilation previously helped
]


# ---------------------------------------------------------------------------
# Checkpoint management
# ---------------------------------------------------------------------------

def load_checkpoint() -> dict:
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text())
    return {"compiled": {}, "tasks_created": [], "run_complete": False}


def save_checkpoint(cp: dict):
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(cp, indent=2))


# ---------------------------------------------------------------------------
# Phase 1: Parallel DSPy compilation
# ---------------------------------------------------------------------------

def compile_one(skill: str, model: str, task_id: str) -> dict:
    """Run a single compilation via subprocess. Returns result dict."""
    variant = f"compiled-{model}"
    output_path = SKILLS_DIR / skill / f"{variant}.md"

    # Skip if already compiled
    if output_path.exists():
        return {
            "skill": skill, "model": model, "status": "skipped",
            "message": f"Already exists: {output_path}",
        }

    print(f"  [COMPILE] {skill} -> {model} (variant: {variant})")
    start = time.monotonic()

    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "llm_bench.cli", "compile-skill",
                "--skill", skill,
                "--target-model", model,
                "--teacher-model", TEACHER_MODEL,
                "--task", task_id,
                "--output-variant", variant,
                "--metric", "proxy",
                "--iterations", "10",
                "--skills-dir", str(SKILLS_DIR),
                "--results-dir", str(RESULTS_DIR),
                "--config-dir", str(CONFIG_DIR),
            ],
            capture_output=True, text=True, timeout=600,  # 10 min max per compilation
            cwd=str(ROOT),
        )
        elapsed = time.monotonic() - start

        if result.returncode == 0 and output_path.exists():
            # Extract score from output
            score = 0.0
            for line in result.stdout.splitlines():
                if "Score:" in line:
                    try:
                        score = float(line.split("Score:")[1].strip())
                    except (ValueError, IndexError):
                        pass
            return {
                "skill": skill, "model": model, "status": "success",
                "score": score, "duration_s": round(elapsed, 1),
                "output": str(output_path),
            }
        else:
            error = result.stderr[-500:] if result.stderr else result.stdout[-500:]
            return {
                "skill": skill, "model": model, "status": "failed",
                "error": error, "duration_s": round(elapsed, 1),
            }
    except subprocess.TimeoutExpired:
        return {
            "skill": skill, "model": model, "status": "timeout",
            "duration_s": 600,
        }
    except Exception as e:
        return {
            "skill": skill, "model": model, "status": "error",
            "error": str(e),
        }


def run_compilations(concurrency: int = 4):
    """Run all compilations in parallel with checkpointing."""
    cp = load_checkpoint()

    # Build work queue — skip already-completed
    work = []
    for skill, task_id in SKILLS_HEAVY.items():
        for model in COMPILE_MODELS:
            key = f"{skill}:{model}"
            if key in cp["compiled"] and cp["compiled"][key].get("status") in ("success", "skipped"):
                continue
            work.append((skill, model, task_id))

    total = len(SKILLS_HEAVY) * len(COMPILE_MODELS)
    done = total - len(work)
    print(f"\n{'='*60}")
    print(f"COMPILATION PHASE")
    print(f"{'='*60}")
    print(f"  Total:       {total}")
    print(f"  Completed:   {done}")
    print(f"  Remaining:   {len(work)}")
    print(f"  Concurrency: {concurrency}")
    print(f"  Teacher:     {TEACHER_MODEL}")
    print()

    if not work:
        print("All compilations complete!")
        return

    start = time.monotonic()
    completed = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {
            executor.submit(compile_one, skill, model, task_id): (skill, model)
            for skill, model, task_id in work
        }

        for future in as_completed(futures):
            skill, model = futures[future]
            key = f"{skill}:{model}"
            try:
                result = future.result()
                cp["compiled"][key] = result
                save_checkpoint(cp)

                status = result["status"]
                if status == "success":
                    completed += 1
                    print(f"  [{done+completed+failed}/{total}] OK  {skill} -> {model} "
                          f"(score={result.get('score', 0):.2f}, {result.get('duration_s', 0):.0f}s)")
                elif status == "skipped":
                    completed += 1
                    print(f"  [{done+completed+failed}/{total}] SKIP {skill} -> {model}")
                else:
                    failed += 1
                    print(f"  [{done+completed+failed}/{total}] FAIL {skill} -> {model}: "
                          f"{result.get('error', result.get('status', 'unknown'))[:100]}")
            except Exception as e:
                failed += 1
                cp["compiled"][key] = {"skill": skill, "model": model, "status": "error", "error": str(e)}
                save_checkpoint(cp)
                print(f"  [{done+completed+failed}/{total}] ERROR {skill} -> {model}: {e}")

    elapsed = time.monotonic() - start
    print(f"\nCompilation complete: {completed} success, {failed} failed in {elapsed:.0f}s")


# ---------------------------------------------------------------------------
# Phase 2: Create tier4 task.yaml for each compiled variant
# ---------------------------------------------------------------------------

def create_compiled_tasks():
    """Create tier4 task.yaml + validate.py for each compiled skill variant."""
    cp = load_checkpoint()
    created = 0
    skipped = 0

    print(f"\n{'='*60}")
    print(f"CREATING TIER4 TASKS FOR COMPILED VARIANTS")
    print(f"{'='*60}")

    for skill, task_id in SKILLS_HEAVY.items():
        # Load the tier3 baseline task to copy prompt/tags/scoring
        tier3_dir = TASKS_DIR / task_id.replace("tier3-", "tier3/")
        # Handle the directory name mapping
        for tier_dir in TASKS_DIR.glob("tier3/*"):
            yaml_path = tier_dir / "task.yaml"
            if yaml_path.exists():
                data = yaml.safe_load(yaml_path.read_text())
                if data.get("id") == task_id:
                    tier3_dir = tier_dir
                    break

        tier3_yaml = tier3_dir / "task.yaml"
        if not tier3_yaml.exists():
            print(f"  WARN: Tier3 task not found for {task_id}, skipping")
            continue

        tier3_data = yaml.safe_load(tier3_yaml.read_text())
        tier3_validate = tier3_dir / "validate.py"
        base_name = SKILL_PAIRS[skill]
        skill_type = SKILL_TYPES[skill]

        for model in COMPILE_MODELS:
            variant = f"compiled-{model}"
            compiled_skill_path = SKILLS_DIR / skill / f"{variant}.md"

            if not compiled_skill_path.exists():
                continue  # Compilation didn't succeed for this one

            # Create task directory
            task_dir_name = f"{base_name}-compiled-{model}"
            task_dir = TASKS_DIR / "tier4" / task_dir_name

            if task_dir.exists() and (task_dir / "task.yaml").exists():
                # Check if already in checkpoint
                key = f"task:{task_dir_name}"
                if key not in cp.get("tasks_created", []):
                    cp.setdefault("tasks_created", []).append(key)
                    save_checkpoint(cp)
                skipped += 1
                continue

            task_dir.mkdir(parents=True, exist_ok=True)

            # Write task.yaml
            task_data = {
                "id": f"tier4-{task_dir_name}",
                "name": f"{tier3_data['name']} (compiled-{model})",
                "tier": 4,
                "prompt": tier3_data["prompt"],
                "timeout": tier3_data["timeout"],
                "skill": f"{skill}:{variant}",
                "difficulty": 3,
                "skill_type": skill_type,
                "skill_intensity": "heavy",
                "skill_pair": base_name,
                "tags": tier3_data.get("tags", []),
                "scoring": tier3_data.get("scoring", {
                    "automated": ["correctness", "completion", "efficiency"],
                    "flagged": ["quality", "instruction_following"],
                }),
            }
            (task_dir / "task.yaml").write_text(
                yaml.dump(task_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
            )

            # Copy validate.py
            if tier3_validate.exists():
                (task_dir / "validate.py").write_text(tier3_validate.read_text())

            cp.setdefault("tasks_created", []).append(f"task:{task_dir_name}")
            save_checkpoint(cp)
            created += 1

    print(f"  Created: {created} new task directories")
    print(f"  Skipped: {skipped} (already exist)")


# ---------------------------------------------------------------------------
# Phase 3: Full benchmark run (parallel by model)
# ---------------------------------------------------------------------------

def _run_model_benchmark(model: str, cli: str, log_dir: Path) -> dict:
    """Run all tasks for a single model×CLI combo. Returns summary dict."""
    log_file = log_dir / f"{model}_{cli}.log"

    cmd = [
        sys.executable, "-m", "llm_bench.cli", "run",
        "--models", model,
        "--clis", cli,
        "--tiers", "1,2,3,4",
        "--tasks-dir", str(TASKS_DIR),
        "--skills-dir", str(SKILLS_DIR),
        "--results-dir", str(RESULTS_DIR),
        "--config-dir", str(CONFIG_DIR),
    ]

    start = time.monotonic()
    try:
        with open(log_file, "w") as lf:
            result = subprocess.run(
                cmd, stdout=lf, stderr=subprocess.STDOUT,
                text=True, timeout=7200,  # 2hr max per model×cli
                cwd=str(ROOT),
            )
        elapsed = time.monotonic() - start
        return {
            "model": model, "cli": cli, "status": "done",
            "exit_code": result.returncode, "duration_s": round(elapsed, 1),
            "log": str(log_file),
        }
    except subprocess.TimeoutExpired:
        return {"model": model, "cli": cli, "status": "timeout", "log": str(log_file)}
    except Exception as e:
        return {"model": model, "cli": cli, "status": "error", "error": str(e)}


def run_benchmark(concurrency: int = 4):
    """Run the full benchmark with parallel model×CLI workers."""
    print(f"\n{'='*60}")
    print(f"FULL BENCHMARK RUN (parallel, concurrency={concurrency})")
    print(f"{'='*60}")

    # Build work queue: each model×CLI is an independent unit
    all_models = list(ALL_BUDGET_MODELS) + ["opus4.6", "gpt-5.4", "gemini-3.1-pro"]
    clis = ["claude-code", "kilo"]

    # Check which model×CLI combos already have results (skip completed)
    cp = load_checkpoint()
    completed_combos = set(cp.get("run_combos_done", []))

    work = []
    for model in all_models:
        for cli in clis:
            key = f"{model}:{cli}"
            if key in completed_combos:
                continue
            work.append((model, cli))

    total = len(all_models) * len(clis)
    done = total - len(work)
    print(f"  Models:      {len(all_models)} ({', '.join(all_models)})")
    print(f"  CLIs:        {', '.join(clis)}")
    print(f"  Combos:      {total} total, {done} done, {len(work)} remaining")
    print(f"  Concurrency: {concurrency}")
    print()

    if not work:
        print("All model×CLI combos complete!")
        cp["run_complete"] = True
        save_checkpoint(cp)
        return

    log_dir = Path("/tmp/llm-bench-logs")
    log_dir.mkdir(exist_ok=True)

    completed = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {
            executor.submit(_run_model_benchmark, model, cli, log_dir): (model, cli)
            for model, cli in work
        }

        for future in as_completed(futures):
            model, cli = futures[future]
            try:
                result = future.result()
                key = f"{model}:{cli}"
                status = result["status"]

                if status == "done":
                    completed += 1
                    cp.setdefault("run_combos_done", []).append(key)
                    save_checkpoint(cp)
                    print(f"  [{done+completed+failed}/{total}] OK   {model} × {cli} "
                          f"({result.get('duration_s', 0):.0f}s)")
                else:
                    failed += 1
                    print(f"  [{done+completed+failed}/{total}] FAIL {model} × {cli}: {status}")
            except Exception as e:
                failed += 1
                print(f"  [{done+completed+failed}/{total}] ERROR {model} × {cli}: {e}")

    cp["run_complete"] = (failed == 0)
    save_checkpoint(cp)

    results_count = len(list(RESULTS_DIR.glob("*.json"))) if RESULTS_DIR.exists() else 0
    print(f"\nBenchmark complete: {completed} done, {failed} failed")
    print(f"Total results: {results_count}")
    print(f"Logs in: {log_dir}/")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Full benchmark orchestrator")
    parser.add_argument("--phase", required=True,
                        choices=["compile", "create-tasks", "run", "all", "status"],
                        help="Which phase to run")
    parser.add_argument("--concurrency", type=int, default=4,
                        help="Parallel compilation workers (default: 4)")
    parser.add_argument("--reset", action="store_true",
                        help="Reset checkpoint and start fresh")
    args = parser.parse_args()

    if args.reset:
        CHECKPOINT_FILE.unlink(missing_ok=True)
        print("Checkpoint reset.")

    if args.phase == "status":
        cp = load_checkpoint()
        compiled = cp.get("compiled", {})
        success = sum(1 for v in compiled.values() if v.get("status") in ("success", "skipped"))
        failed = sum(1 for v in compiled.values() if v.get("status") == "failed")
        total = len(SKILLS_HEAVY) * len(COMPILE_MODELS)
        print(f"Compilation: {success}/{total} done, {failed} failed, {total-success-failed} remaining")
        print(f"Tasks created: {len(cp.get('tasks_created', []))}")
        print(f"Run complete: {cp.get('run_complete', False)}")
        results_count = len(list(RESULTS_DIR.glob("*.json"))) if RESULTS_DIR.exists() else 0
        print(f"Results: {results_count}")
        return

    if args.phase in ("compile", "all"):
        run_compilations(concurrency=args.concurrency)

    if args.phase in ("create-tasks", "all"):
        create_compiled_tasks()

    if args.phase in ("run", "all"):
        run_benchmark(concurrency=args.concurrency)


if __name__ == "__main__":
    main()
