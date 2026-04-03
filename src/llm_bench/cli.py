import argparse
import asyncio
import sys
from pathlib import Path

from llm_bench.loader import load_tasks
from llm_bench.runner import run_matrix


# Models available for benchmarking
MODELS = {
    "opus4.6": "Anthropic Opus 4.6 (frontier)",
    "qwen3-30b": "Qwen3 Coder 30B",
    "minimax-m2.7": "MinimaxM2.7",
    "glm-5": "GLM-5",
    "gemma-4-31b": "Google Gemma 4 31B",
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

    dash_parser = subparsers.add_parser("dashboard", help="Launch results dashboard")
    dash_parser.add_argument("--port", type=int, default=8080, help="Port number")
    dash_parser.add_argument("--results-dir", default="results", help="Path to results directory")

    info_parser = subparsers.add_parser("info", help="Show available models, CLIs, tasks, and skills")
    info_parser.add_argument("--tasks-dir", default="tasks", help="Path to tasks directory")
    info_parser.add_argument("--skills-dir", default="skills", help="Path to skills directory")
    info_parser.add_argument("--results-dir", default="results", help="Path to results directory")

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


def _handle_run(args):
    tasks_dir = Path(args.tasks_dir)
    skills_dir = Path(args.skills_dir)
    results_dir = Path(args.results_dir)
    tiers = [int(t) for t in args.tiers.split(",")]
    models = args.models.split(",")
    cli_names = args.clis.split(",")
    task_ids = args.tasks.split(",") if args.tasks else None

    tasks = load_tasks(tasks_dir, tiers=tiers, task_ids=task_ids)
    if not tasks:
        print(f"No tasks found in {tasks_dir} for tiers {tiers}")
        sys.exit(1)

    total = len(tasks) * len(cli_names) * len(models)
    print(f"Running {len(tasks)} tasks x {len(cli_names)} CLIs x {len(models)} models = {total} runs")

    results = asyncio.run(
        run_matrix(
            tasks=tasks,
            cli_names=cli_names,
            models=models,
            skills_dir=skills_dir,
            results_dir=results_dir,
        )
    )

    passed = sum(1 for r in results if r.scores.correctness and r.scores.correctness >= 0.5)
    print(f"\nComplete: {len(results)} runs, {passed} passed")


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

    # Models
    print("MODELS")
    print("-" * 50)
    for model_id, desc in MODELS.items():
        print(f"  {model_id:<20} {desc}")
    print()

    # CLIs
    print("CLIs")
    print("-" * 50)
    for cli_name in ADAPTERS:
        print(f"  {cli_name}")
    print()

    # Tasks
    print("TASKS")
    print("-" * 50)
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
    print("-" * 50)
    if skills_dir.exists():
        skill_dirs = [d for d in sorted(skills_dir.iterdir()) if d.is_dir() and (d / "SKILL.md").exists()]
        if skill_dirs:
            for skill_dir in skill_dirs:
                # Read first line of description from SKILL.md
                skill_md = skill_dir / "SKILL.md"
                desc = ""
                for line in skill_md.read_text().splitlines():
                    line = line.strip()
                    if line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"').strip("'")
                        break
                print(f"  {skill_dir.name:<25} {desc}")
            print(f"\n  Total: {len(skill_dirs)} skills")
        else:
            print("  (none found)")
    else:
        print(f"  (skills directory not found: {skills_dir})")
    print()

    # Results summary
    print("RESULTS")
    print("-" * 50)
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

    # Example command
    model_ids = ",".join(list(MODELS.keys())[:2])
    cli_ids = ",".join(list(ADAPTERS.keys())[:2])
    print("EXAMPLE")
    print("-" * 50)
    print(f"  llm-bench run --models {model_ids} --clis {cli_ids} --tiers 1")


if __name__ == "__main__":
    main()
