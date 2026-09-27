"""Generate publication-safe synthetic survey data with a fixed seed."""

from __future__ import annotations

from pathlib import Path
import random

import pandas as pd


SEED = 20260927
ROWS = 73
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
INDUSTRIES = ["energy_storage", "coatings", "mobility", "construction", "environmental"]
APPLICATIONS = ["conductive_compound", "durable_coating", "reinforced_polymer", "thermal_material", "adsorbent_media"]
ADOPTION = ["exploring", "pilot_ready", "conditional", "not_planned"]
NEEDS = ["low", "moderate", "high", "critical"]
INDICATORS = ["particle_size", "dispersion", "surface_area", "conductivity", "purity", "durability"]
TESTS = ["dispersion_test", "aging_test", "conductivity_test", "purity_test", "scale_up_test"]
BARRIERS = ["price", "supply_consistency", "qualification_time", "performance_data", "standards"]
COMMENTS = [
    "Need clearer performance data before a pilot.",
    "A consistent supply specification would support adoption.",
    "A shared test method could reduce qualification time.",
    "Pilot pricing and durability evidence are important.",
    "We would evaluate a sample with a practical scale-up plan.",
]


def generate_records() -> list[dict[str, str]]:
    """Return the deterministic synthetic respondent records."""
    rng = random.Random(SEED)
    rows = []
    for index in range(1, ROWS + 1):
        rows.append({
            "respondent_id": f"SYN-{index:04d}",
            "industry_group": rng.choice(INDUSTRIES),
            "application_area": rng.choice(APPLICATIONS),
            "adoption_interest": rng.choice(ADOPTION),
            "standardization_need": rng.choice(NEEDS),
            "management_indicators": "|".join(rng.sample(INDICATORS, k=rng.randint(1, 3))),
            "urgent_test_methods": "|".join(rng.sample(TESTS, k=rng.randint(1, 2))),
            "commercialization_barriers": "|".join(rng.sample(BARRIERS, k=rng.randint(1, 3))),
            "free_text_comment": rng.choice(COMMENTS),
        })
    return rows


def write_dataset(data_dir: Path = DATA_DIR) -> None:
    """Write all public synthetic data files to ``data_dir``."""
    data_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(generate_records()).to_csv(data_dir / "synthetic_survey.csv", index=False)
    pd.DataFrame([
        {"application_area": area, "taxonomy_group": group}
        for area, group in zip(APPLICATIONS, ["electrification", "coatings", "mobility", "thermal_systems", "environmental"])
    ]).to_csv(data_dir / "demand_taxonomy.csv", index=False)
    pd.DataFrame([
        {"field": "respondent_id", "type": "string", "description": "Synthetic stable identifier"},
        {"field": "industry_group", "type": "categorical", "description": "Synthetic industry segment"},
        {"field": "application_area", "type": "categorical", "description": "Synthetic application category"},
        {"field": "adoption_interest", "type": "categorical", "description": "Synthetic adoption stage"},
        {"field": "standardization_need", "type": "ordinal", "description": "Synthetic need level"},
        {"field": "management_indicators", "type": "multi-response", "description": "Pipe-separated synthetic indicators"},
        {"field": "urgent_test_methods", "type": "multi-response", "description": "Pipe-separated synthetic tests"},
        {"field": "commercialization_barriers", "type": "multi-response", "description": "Pipe-separated synthetic barriers"},
        {"field": "free_text_comment", "type": "text", "description": "Synthetic templated comment"},
    ]).to_csv(data_dir / "survey_schema.csv", index=False)


def main() -> None:
    write_dataset()


if __name__ == "__main__":
    main()
