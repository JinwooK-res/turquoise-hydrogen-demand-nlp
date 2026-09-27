from __future__ import annotations

from pathlib import Path

import pandas as pd

from demand_nlp.analysis import fit_topics, map_taxonomy, split_multi
from demand_nlp.visualization import CORE_FIGURES, generate_figures
from scripts.generate_synthetic_data import generate_records, write_dataset


REQUIRED_COLUMNS = {
    "respondent_id", "industry_group", "application_area", "adoption_interest",
    "standardization_need", "management_indicators", "urgent_test_methods",
    "commercialization_barriers", "free_text_comment",
}
CRITICAL_COLUMNS = REQUIRED_COLUMNS - {"free_text_comment"}
PROHIBITED_METADATA_FIELDS = {
    "company_name", "respondent_name", "phone", "email", "company_id", "organization_id",
}


def synthetic_frame(tmp_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    write_dataset(tmp_path)
    return (
        pd.read_csv(tmp_path / "synthetic_survey.csv"),
        pd.read_csv(tmp_path / "demand_taxonomy.csv"),
    )


def test_synthetic_generation_is_deterministic() -> None:
    assert generate_records() == generate_records()


def test_synthetic_ids_and_required_columns(tmp_path: Path) -> None:
    frame, _ = synthetic_frame(tmp_path)
    assert len(frame) == 73
    assert frame["respondent_id"].is_unique
    assert set(frame.columns) == REQUIRED_COLUMNS


def test_no_missing_critical_fields(tmp_path: Path) -> None:
    frame, _ = synthetic_frame(tmp_path)
    assert not frame[list(CRITICAL_COLUMNS)].isna().any().any()
    assert not (frame[list(CRITICAL_COLUMNS)] == "").any().any()


def test_multi_response_parsing() -> None:
    assert split_multi("particle_size | dispersion||") == ["particle_size", "dispersion"]
    assert split_multi(None) == []


def test_tfidf_output_is_valid() -> None:
    result = fit_topics(pd.Series([
        "performance data and pilot pricing",
        "shared test method and performance data",
        "supply consistency and scale up plan",
    ]), n_topics=2, n_terms=3)
    assert not result.empty
    assert set(result.columns) == {"topic", "term", "weight"}
    assert result["term"].notna().all()
    assert (result["weight"] >= 0).all()


def test_configured_nmf_topic_count() -> None:
    result = fit_topics(pd.Series([
        "performance data and pilot pricing",
        "shared test method and performance data",
        "supply consistency and scale up plan",
        "pilot pricing and test method",
    ]), n_topics=2, n_terms=2)
    assert result["topic"].nunique() == 2


def test_taxonomy_mapping_uses_only_defined_categories(tmp_path: Path) -> None:
    frame, taxonomy = synthetic_frame(tmp_path)
    mapped = map_taxonomy(frame, taxonomy)
    assert set(mapped["taxonomy_group"]) <= set(taxonomy["taxonomy_group"])


def test_no_personal_or_company_metadata_fields(tmp_path: Path) -> None:
    frame, _ = synthetic_frame(tmp_path)
    assert PROHIBITED_METADATA_FIELDS.isdisjoint(frame.columns)


def test_figure_generation_creates_all_nonempty_figures(tmp_path: Path) -> None:
    synthetic_frame(tmp_path)
    figure_dir = tmp_path / "figures"
    paths = generate_figures(tmp_path, figure_dir)
    assert [path.name for path in paths] == list(CORE_FIGURES)
    assert all(path.is_file() and path.stat().st_size > 0 for path in paths)
