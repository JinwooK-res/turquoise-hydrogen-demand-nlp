"""Generate figures from the synthetic survey data."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .analysis import fit_topics, load_survey, map_taxonomy, split_multi, tfidf_top_terms


CORE_FIGURES = (
    "industry_adoption_heatmap.png",
    "industry_taxonomy_heatmap.png",
    "tfidf_top_terms.png",
    "nmf_topic_keywords.png",
    "management_indicator_heatmap.png",
)


def _heatmap(table: pd.DataFrame, title: str, colorbar_label: str, output_path: Path, as_proportion: bool = False) -> None:
    """Render a compact annotated heatmap with readable labels."""
    values = table.div(table.sum(axis=1), axis=0) if as_proportion else table
    values = values.fillna(0)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    image = ax.imshow(values.to_numpy(), cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(values.columns)), labels=values.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(values.index)), labels=values.index)
    ax.set_title(title)
    ax.set_xlabel(table.columns.name or "Category")
    ax.set_ylabel(table.index.name or "Industry group")
    for row in range(values.shape[0]):
        for col in range(values.shape[1]):
            label = f"{values.iloc[row, col]:.0%}" if as_proportion else f"{int(values.iloc[row, col])}"
            ax.text(col, row, label, ha="center", va="center", fontsize=9)
    fig.colorbar(image, ax=ax, label=colorbar_label)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_industry_adoption(frame: pd.DataFrame, output_dir: Path) -> None:
    table = pd.crosstab(frame["industry_group"], frame["adoption_interest"])
    table.index.name = "Industry group"
    table.columns.name = "Adoption interest"
    _heatmap(table, "Synthetic adoption interest within industry", "Within-industry proportion", output_dir / "industry_adoption_heatmap.png", as_proportion=True)


def plot_industry_taxonomy(frame: pd.DataFrame, taxonomy: pd.DataFrame, output_dir: Path) -> None:
    mapped = map_taxonomy(frame, taxonomy)
    categories = taxonomy["taxonomy_group"].drop_duplicates().tolist()
    table = pd.crosstab(mapped["industry_group"], mapped["taxonomy_group"]).reindex(columns=categories, fill_value=0)
    table.index.name = "Industry group"
    table.columns.name = "Human-defined taxonomy"
    _heatmap(table, "Synthetic responses by industry and human-defined taxonomy", "Synthetic response count", output_dir / "industry_taxonomy_heatmap.png")


def plot_tfidf_terms(frame: pd.DataFrame, output_dir: Path) -> None:
    terms = tfidf_top_terms(frame["free_text_comment"], n_terms=12).sort_values("score")
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.barh(terms["term"], terms["score"], color="#3b6ea8")
    ax.set_title("Top TF-IDF terms in synthetic comments")
    ax.set_xlabel("Mean TF-IDF score")
    ax.set_ylabel("Term")
    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "tfidf_top_terms.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_nmf_topics(frame: pd.DataFrame, output_dir: Path) -> None:
    topics = fit_topics(frame["free_text_comment"], n_topics=3, n_terms=6)
    topic_ids = sorted(topics["topic"].unique())
    fig, axes = plt.subplots(len(topic_ids), 1, figsize=(9, 2.4 * len(topic_ids)), squeeze=False)
    for axis, topic_id in zip(axes.flat, topic_ids):
        subset = topics[topics["topic"] == topic_id].sort_values("weight")
        axis.barh(subset["term"], subset["weight"], color="#6a994e")
        axis.set_title(f"Topic {topic_id}")
        axis.set_xlabel("NMF component weight")
    fig.suptitle("NMF topic keywords in synthetic comments", y=1.01)
    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "nmf_topic_keywords.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_management_indicators(frame: pd.DataFrame, output_dir: Path) -> None:
    rows = []
    for industry, value in zip(frame["industry_group"], frame["management_indicators"]):
        rows.extend({"industry_group": industry, "indicator": indicator} for indicator in split_multi(value))
    exploded = pd.DataFrame(rows)
    table = pd.crosstab(exploded["industry_group"], exploded["indicator"])
    table.index.name = "Industry group"
    table.columns.name = "Management indicator"
    _heatmap(table, "Synthetic management indicators by industry", "Synthetic response count", output_dir / "management_indicator_heatmap.png")


def generate_figures(data_dir: Path = Path("data"), output_dir: Path = Path("figures")) -> list[Path]:
    """Generate the five figures used by the project."""
    frame = load_survey(data_dir / "synthetic_survey.csv")
    taxonomy = load_survey(data_dir / "demand_taxonomy.csv")
    plot_industry_adoption(frame, output_dir)
    plot_industry_taxonomy(frame, taxonomy, output_dir)
    plot_tfidf_terms(frame, output_dir)
    plot_nmf_topics(frame, output_dir)
    plot_management_indicators(frame, output_dir)
    return [output_dir / name for name in CORE_FIGURES]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("figures"))
    args = parser.parse_args()
    paths = generate_figures(args.data, args.output)
    print(f"Generated {len(paths)} figures in {args.output}")


if __name__ == "__main__":
    main()
