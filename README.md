# UCI Heart Disease — An End-to-End Analytics Case Study

A structured, fully documented case study exploring which clinical measurements
are associated with the presence of heart disease, using the UCI Heart Disease
dataset. The project is deliberately split into four phases, each committed
separately, so the git history shows how the work actually progressed.

## Roadmap

- [x] **1. Gathering** — download the data reproducibly, verify license and structure
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

python src/download_data.py      # fetch raw files into data/raw/ and verify checksums
python src/check_structure.py    # read-only report comparing the files to the documentation
```

## Data source & license

| | |
|---|---|
| **Dataset** | Heart Disease, UCI Machine Learning Repository (dataset #45) |
| **Page** | https://archive.ics.uci.edu/dataset/45/heart+disease |
| **Files from** | https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/ |
| **DOI** | [10.24432/C52P4X](https://doi.org/10.24432/C52P4X) |
| **License** | [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) — sharing and adaptation allowed for any purpose with appropriate credit |
| **Collected at** | Cleveland Clinic Foundation; Hungarian Institute of Cardiology, Budapest; University Hospitals of Zurich and Basel; V.A. Medical Center, Long Beach |
| **Donated** | July 1988 |
| **Downloaded** | 2026-09-24 |

**Citation** (as given by UCI):

> Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). Heart Disease
> [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C52P4X.

Because the license is CC BY 4.0, the raw files are redistributed in
`data/raw/` with this attribution. Their SHA-256 checksums are pinned in
`data/raw/SHA256SUMS`; `python src/download_data.py --verify` confirms a copy
is byte-for-byte identical to the one analysed here.

### Files used

| File | Site | Rows |
|---|---|---|
| `processed.cleveland.data` | Cleveland Clinic Foundation | 303 |
| `processed.hungarian.data` | Hungarian Institute of Cardiology | 294 |
| `processed.switzerland.data` | University Hospitals Zurich & Basel | 123 |
| `processed.va.data` | V.A. Medical Center, Long Beach | 200 |
| `heart-disease.names` | Documentation | — |

920 rows in total. Each file is comma-separated with no header row and 14
columns; missing values are written as `?`.

### Data dictionary

From `heart-disease.names`, which documents 76 original attributes; the
processed files keep these 14.

| Column | Meaning | Values |
|---|---|---|
| `age` | Age | years |
| `sex` | Sex | 1 = male, 0 = female |
| `cp` | Chest pain type | 1 = typical angina, 2 = atypical angina, 3 = non-anginal pain, 4 = asymptomatic |
| `trestbps` | Resting blood pressure on admission | mm Hg |
| `chol` | Serum cholesterol | mg/dl |
| `fbs` | Fasting blood sugar > 120 mg/dl | 1 = true, 0 = false |
| `restecg` | Resting ECG result | 0 = normal, 1 = ST-T wave abnormality, 2 = probable/definite left ventricular hypertrophy |
| `thalach` | Maximum heart rate achieved | beats per minute |
| `exang` | Exercise-induced angina | 1 = yes, 0 = no |
| `oldpeak` | ST depression induced by exercise relative to rest | unit not stated (conventionally mm) |
| `slope` | Slope of the peak exercise ST segment | 1 = upsloping, 2 = flat, 3 = downsloping |
| `ca` | Major vessels coloured by fluoroscopy | 0–3 |
| `thal` | Thallium stress test result | 3 = normal, 6 = fixed defect, 7 = reversible defect |
| `num` | Angiographic diagnosis (the target) | 0 = < 50% narrowing (no disease); 1–4 = disease present |

### Where the files differ from the documentation

`src/check_structure.py` compared the files against `heart-disease.names`.
Row counts and all categorical codes match, except for the points below. None
are fixed here — raw data stays untouched — they are inputs to the cleaning
phase.

1. **Missing-value marker.** The documentation says `-9.0`; the processed files
   use `?` and contain no `-9` at all.
2. **Diagnosis levels.** The documentation describes `num` as 0/1, but its own
   class-distribution table and three of the files use 0–4. The **Hungarian**
   file uses only 0/1: its 106 cases coded `1` equal the 37 + 26 + 28 + 15
   documented for levels 1–4, so severity was collapsed there. Only
   presence/absence (0 vs. ≥ 1) is comparable across all four sites.
3. **Zeros that mean "not recorded".** `chol` is `0` for all 123 Switzerland
   rows and 49 VA rows, and `trestbps` is `0` for one VA row. These are not
   physiological values and must be treated as missing.
4. **Unevenly missing columns.** Cleveland is nearly complete. At the other
   sites `ca` is 96–99% missing, `thal` 42–90%, and `slope` 14–65%.
5. **Negative `oldpeak`.** 12 rows (11 Switzerland, 1 VA) have ST *elevation*
   recorded as negative depression. Plausible, but worth noting.
6. **Duplicates.** Two pairs of identical rows (one pair within Hungarian, one
   within VA). With no patient ID they may be repeated records or two patients
   with identical measurements.

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
