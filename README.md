# Which Warning Signs Actually Go With Heart Disease?

*An end-to-end analytics case study on the UCI Heart Disease data: 920 patients, four hospitals, one question.*

Doctors send someone for an angiogram when they're already worried about
that person's heart. So among those patients, which everyday measurements
really separate the people who have heart disease from the people who don't?
And does the answer hold up at a second hospital, or was it a fluke of the
first one?

I built this for two reasons. I'm always pushing to learn more Python and
machine learning, and the best way I know to do that is to pick a real
dataset and see it all the way through. And healthcare hires a lot of data
analysts. I'd like to be one of them, so I wanted to learn how clinical data
actually behaves: the gaps, the odd codes and all.

I took it from raw download to final report in four phases. Each one is its
own set of commits, so the history shows how the work actually unfolded,
mistakes and course corrections included.

> **📄 [Read the report](reports/REPORT.md).** The findings in plain language first, then the full analysis.
>
> **🗂️ [Data and cleaning notes](docs/DATA.md).** Source, data dictionary, what was wrong with the files and how I fixed it.

**The short answer:** four signs held up at every hospital I tested them on.
An abnormal exercise ECG, chest pain brought on by exercise, being male, and
(the one most people wouldn't guess) having no chest pain at all. Routine measurements
alone picked out the patient with disease in 87 of 100 pairs. Meanwhile
cholesterol and blood pressure, two of the most famous risk factors there
are, barely told the groups apart. That's not because they don't matter.
It's because of who ends up getting tested.

I also pitted the simple model against two machine-learning models, a random
forest and gradient boosting. They didn't beat it. On 297 patients, the model
you can explain to a doctor predicted just as well.

![Four signs stood out and held up at other hospitals](reports/figures/story_2_warning_signs.png)

## What's inside

| Step | Notebook | What it answers |
|---|---|---|
| Check | [02 Cleaning check](notebooks/02_cleaning_check.ipynb) | Did cleaning change only what it was supposed to? |
| Describe | [03 Cleveland profile](notebooks/03_cleveland_profile.ipynb) | How do patients with and without disease differ, one measurement at a time? |
| Test | [04 Effect sizes and tests](notebooks/04_cleveland_tests.ipynb) | How big is each difference, and could it be chance? |
| Model | [05 Logistic regression](notebooks/05_cleveland_model.ipynb) | Which signs still matter once the others are accounted for? |
| Replicate | [06 Four-hospital check](notebooks/06_four_site_check.ipynb) | Do the findings hold at three other hospitals? |
| Compare | [07 Machine learning comparison](notebooks/07_model_comparison.ipynb) | Does a random forest or gradient boosting do better? |

**Tools and techniques:** Python, pandas, statsmodels, scikit-learn,
matplotlib. Checksummed data download, scripted and self-verifying cleaning,
Mann–Whitney and chi-square tests with bootstrap confidence intervals and Holm
correction, logistic regression, repeated stratified cross-validation, model
calibration, permutation importance, and out-of-sample replication.

## Run it yourself

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python src/download_data.py        # fetch the raw files and verify their checksums
python src/check_structure.py      # compare the files with their documentation
python src/clean_data.py           # write data/processed/heart_clean.csv
python src/make_report_figures.py  # the plain-language charts in the report
jupyter nbconvert --to notebook --execute --inplace notebooks/0*.ipynb
```

Random seeds are fixed, so every number in the report comes out the same.
Notebook 07 takes about ten minutes; the rest take seconds.

## Repository structure

```
.
├── data/
│   ├── raw/          # original downloads, never edited by hand (checksums in SHA256SUMS)
│   └── processed/    # the cleaned dataset
├── docs/DATA.md      # data source, dictionary and cleaning decisions
├── notebooks/        # verification and analysis notebooks (02–07)
├── src/              # pipeline scripts: download, check, clean, report figures
├── reports/
│   ├── REPORT.md     # final report
│   ├── *.csv         # results tables
│   └── figures/      # all charts
├── requirements.txt  # pinned dependencies
└── LICENSE
```

## Data, license and ethics

The data is the [UCI Heart Disease dataset](https://archive.ics.uci.edu/dataset/45/heart+disease)
(Janosi, Steinbrunn, Pfisterer & Detrano, 1989; DOI
[10.24432/C52P4X](https://doi.org/10.24432/C52P4X)), licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The code in this
repository is under the [MIT License](LICENSE).

I used the original UCI files rather than the popular Kaggle `heart.csv`,
which is mostly the same ~300 patients copied over and over. Duplicates make a
model look smarter than it is.

This is de-identified public data. The original 76-column files once held
patient names and Social Security numbers (since replaced with dummy values),
so this project uses only the 14-column files and `.gitignore` blocks the
originals. Results are reported only in aggregate, and none of it is medical
advice.
