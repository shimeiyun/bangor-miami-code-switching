from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import run_pipeline


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="bangor-miami",
        description="Reproducible conservative Spanish-English code-switch analysis.",
    )
    subcommands = root.add_subparsers(dest="command", required=True)
    run = subcommands.add_parser("run", help="Run the pipeline on local corpus files.")
    run.add_argument("--chats-dir", type=Path, required=True)
    run.add_argument("--tsvs-dir", type=Path, required=True)
    run.add_argument("--metadata", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, required=True)
    demo = subcommands.add_parser("demo", help="Run the bundled synthetic example.")
    demo.add_argument("--output-dir", type=Path, default=Path("results/demo"))
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "demo":
        project = Path(__file__).resolve().parents[2]
        chats = project / "data" / "sample" / "chats"
        tsvs = project / "data" / "sample" / "tsvs"
        metadata = project / "data" / "sample" / "sample_metadata.csv"
    else:
        chats, tsvs, metadata = args.chats_dir, args.tsvs_dir, args.metadata
    summary = run_pipeline(chats, tsvs, metadata, args.output_dir)
    print(json.dumps(summary, indent=2))
    return 0

