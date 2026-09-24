# UCI Heart Disease — An End-to-End Analytics Case Study

A structured, fully documented case study exploring which clinical measurements
are associated with the presence of heart disease, using the UCI Heart Disease
dataset. The project is deliberately split into four phases, each committed
separately, so the git history shows how the work actually progressed.

## Roadmap

- [ ] **1. Gathering** — download the data reproducibly, verify license and structure *(in progress)*
- [ ] **2. Cleaning** — handle missing values, fix types, decode categories, document every decision
- [ ] **3. Analysis** — exploratory analysis and statistical comparisons
- [ ] **4. Reporting** — findings, limitations, and visual summary

## Repository structure

```
.
├── data/
│   ├── raw/          # original downloads — never edited by hand
│   └── processed/    # outputs of the cleaning phase
├── notebooks/        # exploration and analysis notebooks
├── src/              # reusable scripts (e.g. data download)
├── reports/
│   └── figures/      # final charts
├── requirements.txt  # pinned dependencies
└── README.md
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data source & license

*To be completed during the gathering phase (source URL, DOI, citation, license, download date).*

**Why UCI and not Kaggle?** A widely shared Kaggle version (`heart.csv`, 1,025
rows) consists largely of duplicated records of the same ~300 patients. This
project pulls the original files directly from the UCI Machine Learning
Repository so the sample size and provenance are honest.

## Ethics & sensitivity

This is de-identified, publicly released health data. Even so:

- The original 76-attribute files once contained patient names and Social
  Security numbers (since replaced with dummy values by UCI). This project uses
  only the 14-attribute processed files, and the originals are blocked from
  version control via `.gitignore`.
- Age and sex are quasi-identifiers. They are low-risk here, but the project
  reports only aggregate results and makes no attempt to single out individuals.
- The findings are exploratory and are **not** medical advice.
