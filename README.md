# Carbon Black Demand NLP

Python-based text analysis of carbon black demand and application data in the context of turquoise hydrogen production. The repository uses a synthetic survey to summarize industrial applications, adoption interest, standardization needs, and free-text comments.

## Overview

- 73 synthetic survey records covering five industry groups and five application areas
- Structured response summaries by industry and adoption interest
- Multi-response counts for management indicators
- Word-frequency and TF-IDF summaries of free-text comments
- Exploratory NMF topic terms
- Rule-based mapping of application areas to a small demand taxonomy
- CSV summaries and five PNG figures

## Analysis

The code reads the files in `data/`, parses pipe-separated response fields, groups categorical responses, counts text tokens, calculates TF-IDF scores, fits a three-topic NMF model, and creates heatmaps and bar charts. The taxonomy is defined in `data/demand_taxonomy.csv`; it is not learned from the text.

NMF topics and text scores are descriptive outputs from the synthetic comments. They are not market estimates, forecasts, or validation of demand.

## Outputs

Running the analysis creates these files in `outputs/`:

- `industry_adoption_summary.csv`
- `management_indicator_summary.csv`
- `taxonomy_summary.csv`
- `industry_comparison.csv`
- `term_frequency.csv`
- `nmf_topic_terms.csv`
- `industry_adoption_heatmap.svg`

Running the visualization module creates these tracked figures in `figures/`:

- `industry_adoption_heatmap.png`
- `industry_taxonomy_heatmap.png`
- `tfidf_top_terms.png`
- `nmf_topic_keywords.png`
- `management_indicator_heatmap.png`

## Repository Structure

```text
carbon-black-demand-nlp/
├── README.md
├── LICENSE
├── pyproject.toml
├── data/
│   ├── synthetic_survey.csv
│   ├── survey_schema.csv
│   └── demand_taxonomy.csv
├── figures/
│   ├── industry_adoption_heatmap.png
│   ├── industry_taxonomy_heatmap.png
│   ├── tfidf_top_terms.png
│   ├── nmf_topic_keywords.png
│   └── management_indicator_heatmap.png
├── scripts/
│   └── generate_synthetic_data.py
├── src/
│   └── demand_nlp/
│       ├── __init__.py
│       ├── analysis.py
│       ├── cli.py
│       └── visualization.py
└── tests/
    └── test_publication_safety.py
```

## Usage

Create an environment and install the package:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pip install -e ".[test]"
```

Regenerate the synthetic data if needed:

```powershell
python scripts/generate_synthetic_data.py
```

Run the CSV analysis:

```powershell
carbon-black-demand-nlp
```

Generate the five figures:

```powershell
python -m demand_nlp.visualization
```

Run the tests:

```powershell
pytest
```

## Data

The repository contains a deterministic synthetic survey generated with seed `20260927`. It has no actual company names, respondent details, contact information, source documents, or original survey responses. The dataset is included to exercise the analysis code; its category frequencies do not represent the carbon black market.

## Limitations

The records and free-text comments are synthetic and templated. The outputs describe this generated dataset only. The code does not estimate market size, adoption probability, or commercial viability.

## License

MIT License.
