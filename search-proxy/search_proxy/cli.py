from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from .runner import ADAPTERS, run


def main() -> None:
    """Execute search-proxy CLI commands: serve or benchmark."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Search-proxy: Grounded search engine service and evaluation runner."
    )
    subparsers = parser.add_subparsers(dest="command")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start the FastAPI backend service")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    serve_parser.add_argument("--reload", action="store_true", help="Enable live auto-reload")

    # benchmark command
    bench_parser = subparsers.add_parser("benchmark", help="Run benchmark queries against an engine")
    bench_parser.add_argument("--engine", required=True, choices=sorted(ADAPTERS))
    bench_parser.add_argument("--prompts", required=True, help="Path to prompt file")
    bench_parser.add_argument("--out", required=True, help="Output directory")
    bench_parser.add_argument("--delay", type=float, default=2.5, help="Delay between queries")

    # Maintain backwards compatibility for direct arguments without subcommand
    parser.add_argument("--engine", choices=sorted(ADAPTERS), help=argparse.SUPPRESS)
    parser.add_argument("--prompts", help=argparse.SUPPRESS)
    parser.add_argument("--out", help=argparse.SUPPRESS)
    parser.add_argument("--delay", type=float, default=2.5, help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.command == "serve":
        import uvicorn
        print(f"Starting Ground Search Engine API server on http://{args.host}:{args.port}")
        uvicorn.run("search_proxy.api.app:app", host=args.host, port=args.port, reload=args.reload)
    elif args.command == "benchmark" or args.engine:
        out_file = run(args.engine, Path(args.prompts), Path(args.out), delay_seconds=args.delay)
        print(f"Results saved to {out_file}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
