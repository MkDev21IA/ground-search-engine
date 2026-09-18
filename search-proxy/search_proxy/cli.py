from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from .runner import ADAPTERS, run


def main() -> None:
    """Execute search-proxy against a target engine and save canonical results."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Run search-proxy against a search engine and save canonical results."
    )
    parser.add_argument("--engine", required=True, choices=sorted(ADAPTERS))
    parser.add_argument(
        "--prompts",
        required=True,
        help="Path to prompt file (e.g. ../prompts/prompts_v1.yaml)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory for the run (e.g. ../results/2026-09-17-evaluation)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.5,
        help="Delay in seconds between successive queries (default: 2.5s) to avoid rate limits",
    )
    args = parser.parse_args()

    out_file = run(args.engine, Path(args.prompts), Path(args.out), delay_seconds=args.delay)
    print(f"Results saved to {out_file}")


if __name__ == "__main__":
    main()
