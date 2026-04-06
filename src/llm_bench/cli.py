import argparse
import asyncio
import sys
from pathlib import Path

from llm_bench.config import load_models_config
from llm_bench.loader import load_tasks
from llm_bench.runner import run_matrix


def _get_models(config_dir: Path) -> dict[str, str]:
    """Load model registry from models.yaml."""
    config = load_models_config(config_dir)
    return {
        mid: mdef.get("name", mid)
        for mid, mdef in config.get("models", {}).items()
    }


def main():
    parser = argparse.ArgumentParser(
        prog="llm-bench",
        description="Automated LLM coding benchmark harness",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run benchmark tasks")
    run_parser.add_argument("--models", required=True, help="Comma-separated model IDs")
    run_parser.add_argument("--clis", required=True, help="Comma-separated CLI names (claude-code, open-code, kilo)")
    run_parser.add_argument("--tiers", default="1,2,3,4", help="Comma-separated tier numbers")
    run_parser.add_argument("--tasks", help="Comma-separated task IDs (default: all)")
    run_parser.add_argument("--tasks-dir", default="tasks", help="Path to tasks directory")
    run_parser.add_argument("--skills-dir", default="skills", help="Path to skills directory")
    run_parser.add_argument("--results-dir", default="results", help="Path to results directory")
    run_parser.add_argument("--config-dir", default="config", help="Path to config directory")

    dash_parser = subparsers.add_parser("dashboard", help="Launch results dashboard")
    dash_parser.add_argument("--port", type=int, default=8080, help="Port number")
    dash_parser.add_argument("--results-dir", default="results", help="Path to results directory")

    info_parser = subparsers.add_parser("info", help="Show available models, CLIs, tasks, and skills")
    info_parser.add_argument("--tasks-dir", default="tasks", help="Path to tasks directory")
    info_parser.add_argument("--skills-dir", default="skills", help="Path to skills directory")
    info_parser.add_argument("--results-dir", default="results", help="Path to results directory")
    info_parser.add_argument("--config-dir", default="config", help="Path to config directory")

    compile_parser = subparsers.add_parser(
        "compile-skill", help="Optimize a skill for a target model using DSPy"
    )
    compile_parser.add_argument("--skill", required=True, help="Skill domain (e.g., usd-composition)")
    compile_parser.add_argument("--target-model", required=True, help="Model to optimize for")
    compile_parser.add_argument("--teacher-model", required=True, help="Strong model for optimization")
    compile_parser.add_argument("--task", required=True, help="Task ID for training signal")
    compile_parser.add_argument("--output-variant", required=True, help="Name for output variant")
    compile_parser.add_argument("--metric", default="proxy", choices=["proxy", "live"],
                                help="Metric mode: proxy (fast) or live (runs benchmark)")
    compile_parser.add_argument("--iterations", type=int, default=10, help="Optimization iterations")
    compile_parser.add_argument("--cli", default="claude-code", help="CLI for live metric (default: claude-code)")
    compile_parser.add_argument("--skills-dir", default="skills", help="Path to skills directory")
    compile_parser.add_argument("--results-dir", default="results", help="Path to results directory")
    compile_parser.add_argument("--config-dir", default="config", help="Path to config directory")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        _handle_run(args)
    elif args.command == "dashboard":
        _handle_dashboard(args)
    elif args.command == "info":
        _handle_info(args)
    elif args.command == "compile-skill":
        _handle_compile_skill(args)


def _handle_run(args):
    tasks_dir = Path(args.tasks_dir)
    skills_dir = Path(args.skills_dir)
    results_dir = Path(args.results_dir)
    config_dir = Path(args.config_dir)
    tiers = [int(t) for t in args.tiers.split(",")]
    models = args.models.split(",")
    cli_names = args.clis.split(",")
    task_ids = args.tasks.split(",") if args.tasks else None

    tasks = load_tasks(tasks_dir, tiers=tiers, task_ids=task_ids)
    if not tasks:
        print(f"No tasks found in {tasks_dir} for tiers {tiers}")
        sys.exit(1)

    model_registry = _get_models(config_dir)
    total = len(tasks) * len(cli_names) * len(models)
    print("=" * 60)
    print("LLM BENCH RUN")
    print("=" * 60)
    print(f"  Models:  {', '.join(models)}")
    print(f"  CLIs:    {', '.join(cli_names)}")
    print(f"  Tasks:   {', '.join(t.id for t in tasks)}")
    print(f"  Config:  {config_dir}/models.yaml + {config_dir}/.env")
    print(f"  Total:   {total} runs")

    # Warn about unknown models
    for m in models:
        if m not in model_registry:
            print(f"\n  WARNING: '{m}' not in models.yaml — will use defaults")

    print()
    print("-" * 60)

    import time
    start = time.monotonic()

    results = asyncio.run(
        run_matrix(
            tasks=tasks,
            cli_names=cli_names,
            models=models,
            skills_dir=skills_dir,
            results_dir=results_dir,
            config_dir=config_dir,
        )
    )

    elapsed = time.monotonic() - start
    passed = sum(1 for r in results if r.scores.correctness and r.scores.correctness >= 0.5)
    failed = len(results) - passed

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total runs:  {len(results)}")
    print(f"  Passed:      {passed}")
    print(f"  Failed:      {failed}")
    print(f"  Duration:    {elapsed:.1f}s")
    if results_dir.exists():
        print(f"  Results in:  {results_dir}/")
    print()
    print("  Run `llm-bench dashboard` to view results.")


def _handle_dashboard(args):
    try:
        import uvicorn
    except ImportError:
        print("uvicorn not installed. Run: pip install uvicorn[standard]")
        sys.exit(1)

    import llm_bench.dashboard.app as dash_app
    dash_app.RESULTS_DIR = Path(args.results_dir)

    print(f"Starting dashboard on http://localhost:{args.port}")
    print(f"Results directory: {args.results_dir}")
    uvicorn.run(
        "llm_bench.dashboard.app:app",
        host="0.0.0.0",
        port=args.port,
        reload=False,
    )


def _handle_info(args):
    from llm_bench.adapters import ADAPTERS
    from llm_bench.results import load_results

    tasks_dir = Path(args.tasks_dir)
    skills_dir = Path(args.skills_dir)
    results_dir = Path(args.results_dir)
    config_dir = Path(args.config_dir)

    config = load_models_config(config_dir)
    models_def = config.get("models", {})
    defaults = config.get("defaults", {})

    # Models
    print("MODELS (from config/models.yaml)")
    print("-" * 60)
    for model_id, mdef in models_def.items():
        name = mdef.get("name", model_id)
        provider = mdef.get("provider", defaults.get("provider", "openrouter"))
        or_id = mdef.get("openrouter_id", "")
        print(f"  {model_id:<22} {name}")
        print(f"  {'':22} provider={provider}  id={or_id}")
        # Show CLI-specific overrides
        for cli in ADAPTERS:
            if cli in mdef:
                override = mdef[cli]
                print(f"  {'':22} {cli}: {override}")
    print()

    # API Keys
    print("API KEYS (from config/.env)")
    print("-" * 60)
    env_path = config_dir / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                masked = val[:8] + "..." if len(val) > 8 else val
                print(f"  {key.strip():<25} {masked}")
    else:
        print(f"  (not found — create {env_path})")
    print()

    # CLIs
    print("CLIs")
    print("-" * 60)
    for cli_name in ADAPTERS:
        print(f"  {cli_name}")
    print()

    # Tasks
    print("TASKS")
    print("-" * 60)
    if tasks_dir.exists():
        tasks = load_tasks(tasks_dir)
        if tasks:
            by_tier = {}
            for t in tasks:
                by_tier.setdefault(t.tier, []).append(t)
            for tier in sorted(by_tier):
                print(f"  Tier {tier}:")
                for t in by_tier[tier]:
                    skill_tag = f" [skill: {t.skill}]" if t.skill else ""
                    print(f"    {t.id:<30} {t.name}{skill_tag}")
            print(f"\n  Total: {len(tasks)} tasks")
        else:
            print("  (none found)")
    else:
        print(f"  (tasks directory not found: {tasks_dir})")
    print()

    # Skills
    print("SKILLS")
    print("-" * 60)
    if skills_dir.exists():
        skill_dirs = [
            d for d in sorted(skills_dir.iterdir())
            if d.is_dir() and (
                (d / "SKILL.md").exists()
                or (d / "VARIANTS.yaml").exists()
                or any(f.suffix == ".md" for f in d.iterdir() if f.is_file())
            )
        ]
        if skill_dirs:
            for skill_dir in skill_dirs:
                variants_yaml = skill_dir / "VARIANTS.yaml"
                variants = []
                if variants_yaml.exists():
                    import yaml as _yaml
                    meta = _yaml.safe_load(variants_yaml.read_text()) or {}
                    variants = list((meta.get("variants") or {}).keys())
                else:
                    variants = [f.stem for f in skill_dir.glob("*.md")]
                variant_str = f"  variants: {', '.join(variants)}" if variants else ""
                print(f"  {skill_dir.name:<25}{variant_str}")
            print(f"\n  Total: {len(skill_dirs)} skills")
        else:
            print("  (none found)")
    else:
        print(f"  (skills directory not found: {skills_dir})")
    print()

    # Results
    print("RESULTS")
    print("-" * 60)
    results = load_results(results_dir)
    if results:
        models_seen = sorted(set(r["model"] for r in results))
        clis_seen = sorted(set(r["cli"] for r in results))
        tasks_seen = sorted(set(r["task_id"] for r in results))
        print(f"  {len(results)} runs across {len(models_seen)} models, {len(clis_seen)} CLIs, {len(tasks_seen)} tasks")
        print(f"  Models tested: {', '.join(models_seen)}")
        print(f"  CLIs tested:   {', '.join(clis_seen)}")
    else:
        print("  (no results yet)")
    print()

    # Example
    model_ids = ",".join(list(models_def.keys())[:2])
    cli_ids = ",".join(list(ADAPTERS.keys())[:2])
    print("EXAMPLE")
    print("-" * 60)
    print(f"  llm-bench run --models {model_ids} --clis {cli_ids} --tiers 1")


def _handle_compile_skill(args):
    try:
        from llm_bench.compiler import compile_skill
    except ImportError as e:
        print(f'DSPy not installed. Run: pip install -e ".[compile]"')
        print(f"  Import error: {e}")
        sys.exit(1)

    skills_dir = Path(args.skills_dir)
    results_dir = Path(args.results_dir)
    config_dir = Path(args.config_dir)

    print("=" * 60)
    print("LLM BENCH — SKILL COMPILER (DSPy)")
    print("=" * 60)
    print(f"  Skill:          {args.skill}")
    print(f"  Target model:   {args.target_model}")
    print(f"  Teacher model:  {args.teacher_model}")
    print(f"  Task:           {args.task}")
    print(f"  Output variant: {args.output_variant}")
    print(f"  Metric:         {args.metric}")
    print(f"  Iterations:     {args.iterations}")
    print()

    try:
        result = compile_skill(
            skill_domain=args.skill,
            target_model=args.target_model,
            teacher_model=args.teacher_model,
            task_id=args.task,
            skills_dir=skills_dir,
            results_dir=results_dir,
            config_dir=config_dir,
            output_variant=args.output_variant,
            metric_mode=args.metric,
            num_iterations=args.iterations,
            cli_name=args.cli,
        )

        print()
        print("=" * 60)
        print("COMPILATION RESULT")
        print("=" * 60)
        print(f"  Output:     {result.output_path}")
        print(f"  Score:      {result.score:.2f}")
        print(f"  Duration:   {result.duration_s:.1f}s")
        print()
        print(f"  Test it:    llm-bench run --models {args.target_model} --clis claude-code \\")
        print(f"                --tasks {args.task.replace('tier3', 'tier4')} --skills-dir {args.skills_dir}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Compilation failed: {e}")
        raise


if __name__ == "__main__":
    main()
