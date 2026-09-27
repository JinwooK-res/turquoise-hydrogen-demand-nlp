# Turquoise Hydrogen Demand NLP

Publication-safe demonstration project for demand-survey NLP. All public records in `data/` are synthetic and generated from scratch with fixed seed `20260927`. No actual company or respondent records, names, contact details, source PDFs, notebooks, charts, or response statistics are included. Synthetic frequencies do not represent the original survey, and results are not estimates of the actual market.

## Layout

- `data/synthetic_survey.csv` — synthetic input records
- `data/survey_schema.csv` — field definitions
- `data/demand_taxonomy.csv` — synthetic application-to-taxonomy mapping
- `src/demand_nlp/` — reusable processing and analysis code
- `scripts/generate_synthetic_data.py` — deterministic data generator
- `outputs/` — generated synthetic-derived summaries and heatmap

## Setup and run

```powershell
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -e .
python -m pip install -e ".[test]"
python scripts/generate_synthetic_data.py
turquoise-demand-nlp
```

The pipeline uses multi-response parsing, grouped summaries, standard scikit-learn TF-IDF/NMF topic modeling, taxonomy mapping, industry comparison, and an industry-by-adoption SVG heatmap. Topic modeling is exploratory, not inferential. Taxonomy mapping is human-defined and interpretable; it is not an automatically learned classification.
