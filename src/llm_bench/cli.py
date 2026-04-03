import argparse
import asyncio
import sys
from pathlib import Path

from llm_bench.loader import load_tasks
from llm_bench.runner import run_matrix


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

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        _handle_run(args)
    elif args.command == "dashboard":
        _handle_dashboard(args)


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


if __name__ == "__main__":
    main()
