"""Regenerate human-readable ``REPORT.md`` files from ``summary.json``."""

from __future__ import annotations

import argparse
from pathlib import Path

from experiments.run_report_md import find_summary_files, load_summary_and_write_report


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Write REPORT.md next to each experiment summary.json (phase0_lbp, phase0_mini_swe, …)."
    )
    p.add_argument(
        "--root",
        type=Path,
        default=Path("outputs/experiments"),
        help="Directory to scan for **/summary.json (default: outputs/experiments)",
    )
    p.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Only process this single run directory (must contain summary.json)",
    )
    return p


def main() -> None:
    args = _build_parser().parse_args()
    if args.run_dir is not None:
        rd = args.run_dir.resolve()
        sp = rd / "summary.json"
        if not sp.is_file():
            raise SystemExit(f"Missing summary.json: {sp}")
        out = load_summary_and_write_report(rd)
        print(out.resolve())
        return

    root = args.root.resolve()
    paths = find_summary_files(root)
    if not paths:
        print(f"No summary.json files under {root}")
        return
    for summary_path in paths:
        out = load_summary_and_write_report(summary_path.parent)
        print(out.resolve())


if __name__ == "__main__":
    main()
