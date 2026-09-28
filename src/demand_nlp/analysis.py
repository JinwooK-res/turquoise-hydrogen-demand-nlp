"""Utilities for processing synthetic carbon black demand survey data."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer


def load_survey(path: Path) -> pd.DataFrame:
    """Load a public synthetic CSV and remove empty export columns."""
    frame = pd.read_csv(path)
    return frame.drop(columns=[c for c in frame.columns if str(c).strip() == ""], errors="ignore")


def split_multi(value: object, separator: str = "|") -> list[str]:
    """Parse a pipe-separated multi-response field."""
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split(separator) if part.strip()]


def grouped_summary(frame: pd.DataFrame, group: str, value: str) -> pd.DataFrame:
    """Return response counts grouped by a categorical field."""
    return (frame.groupby([group, value], dropna=False).size().rename("count").reset_index()
            .sort_values([group, "count"], ascending=[True, False]))


def multi_response_summary(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    """Count selections in a pipe-separated response column."""
    values = [item for value in frame[column] for item in split_multi(value)]
    return pd.Series(Counter(values), name="count").rename_axis("selection").reset_index()


def fit_topics(texts: pd.Series, n_topics: int = 3, n_terms: int = 8) -> pd.DataFrame:
    """Fit standard TF-IDF and NMF models and return top terms per topic."""
    vectorizer = TfidfVectorizer(lowercase=True, token_pattern=r"(?u)\b\w+\b")
    matrix = vectorizer.fit_transform(texts.fillna("").astype(str))
    topic_count = min(n_topics, matrix.shape[1])
    model = NMF(n_components=topic_count, init="nndsvda", random_state=17, max_iter=500)
    model.fit_transform(matrix)
    terms = vectorizer.get_feature_names_out()
    rows = []
    for topic_id, topic_weights in enumerate(model.components_, start=1):
        for index in topic_weights.argsort()[-n_terms:][::-1]:
            rows.append({"topic": topic_id, "term": terms[index], "weight": topic_weights[index]})
    return pd.DataFrame(rows)


def tfidf_top_terms(texts: pd.Series, n_terms: int = 12) -> pd.DataFrame:
    """Return the highest mean TF-IDF terms using the project vectorizer."""
    vectorizer = TfidfVectorizer(lowercase=True, token_pattern=r"(?u)\b\w+\b")
    matrix = vectorizer.fit_transform(texts.fillna("").astype(str))
    scores = matrix.mean(axis=0).A1
    terms = vectorizer.get_feature_names_out()
    order = scores.argsort()[-n_terms:][::-1]
    return pd.DataFrame({"term": terms[order], "score": scores[order]})


def map_taxonomy(frame: pd.DataFrame, taxonomy: pd.DataFrame) -> pd.DataFrame:
    """Map application areas to public taxonomy labels."""
    mapping = taxonomy.set_index("application_area")["taxonomy_group"]
    result = frame.copy()
    result["taxonomy_group"] = result["application_area"].map(mapping).fillna("Other")
    return result


def industry_comparison(frame: pd.DataFrame) -> pd.DataFrame:
    """Compare standardization need by industry and adoption interest."""
    need_score = {"low": 1, "moderate": 2, "high": 3, "critical": 4}
    scored = frame.assign(need_score=frame["standardization_need"].map(need_score))
    return (scored.groupby("industry_group").agg(
        respondents=("respondent_id", "count"),
        mean_standardization_need=("need_score", "mean"),
        high_adoption_share=("adoption_interest", lambda s: s.isin(["pilot_ready", "exploring"]).mean()),
    ).reset_index())


def save_heatmap(frame: pd.DataFrame, output_path: Path) -> None:
    """Save an industry-by-adoption-interest heatmap as dependency-free SVG."""
    table = pd.crosstab(frame["industry_group"], frame["adoption_interest"])
    width, height = 180 + len(table.columns) * 130, 100 + len(table.index) * 48
    maximum = max(1, int(table.to_numpy().max()))
    cells = []
    for row, label in enumerate(table.index):
        y = 65 + row * 48
        cells.append(f'<text x="5" y="{y + 22}" font-size="12">{label}</text>')
        for col, column in enumerate(table.columns):
            x = 150 + col * 130
            value = int(table.loc[label, column])
            shade = 255 - int(180 * value / maximum)
            cells.append(f'<rect x="{x}" y="{y}" width="110" height="36" fill="rgb({shade},{shade + 15},255)"/>')
            cells.append(f'<text x="{x + 55}" y="{y + 23}" text-anchor="middle" font-size="12">{value}</text>')
    headers = [f'<text x="{150 + col * 130 + 55}" y="45" text-anchor="middle" font-size="12">{column}</text>' for col, column in enumerate(table.columns)]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
           '<rect width="100%" height="100%" fill="white"/>'
           '<text x="5" y="20" font-size="14">Synthetic survey: industry × adoption interest</text>'
           + "".join(headers + cells) + "</svg>")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")


def extract_terms(texts: pd.Series) -> Counter[str]:
    """Count word-like tokens in synthetic free-text comments."""
    counts: Counter[str] = Counter()
    for text in texts.fillna("").astype(str):
        counts.update(re.findall(r"[A-Za-z][A-Za-z-]+", text.lower()))
    return counts


def write_outputs(frame: pd.DataFrame, taxonomy: pd.DataFrame, output_dir: Path) -> None:
    """Write analysis summaries derived from the survey data."""
    output_dir.mkdir(parents=True, exist_ok=True)
    grouped_summary(frame, "industry_group", "adoption_interest").to_csv(output_dir / "industry_adoption_summary.csv", index=False)
    multi_response_summary(frame, "management_indicators").to_csv(output_dir / "management_indicator_summary.csv", index=False)
    map_taxonomy(frame, taxonomy).groupby("taxonomy_group").size().rename("count").to_csv(output_dir / "taxonomy_summary.csv")
    industry_comparison(frame).to_csv(output_dir / "industry_comparison.csv", index=False)
    pd.DataFrame(extract_terms(frame["free_text_comment"]).most_common(), columns=["term", "count"]).to_csv(output_dir / "term_frequency.csv", index=False)
    fit_topics(frame["free_text_comment"]).to_csv(output_dir / "nmf_topic_terms.csv", index=False)
    save_heatmap(frame, output_dir / "industry_adoption_heatmap.svg")
