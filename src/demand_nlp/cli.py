"""Command-line entry point for the synthetic demand NLP analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import load_survey, write_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/synthetic_survey.csv"))
    parser.add_argument("--taxonomy", type=Path, default=Path("data/demand_taxonomy.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    frame = load_survey(args.data)
    required = {"free_text_comment", "management_indicators", "industry_group", "adoption_interest"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing synthetic survey columns: {sorted(missing)}")
    write_outputs(frame, load_survey(args.taxonomy), args.output)
    print(f"Analyzed {len(frame)} synthetic respondents")
    print(f"Wrote analysis outputs to {args.output}")


if __name__ == "__main__":
    main()

