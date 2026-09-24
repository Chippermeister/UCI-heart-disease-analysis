"""Clean the raw UCI Heart Disease files into one tidy table.

Usage:
    python src/clean_data.py

Reads the four processed.*.data files from data/raw/ (never modified) and
writes data/processed/heart_clean.csv. Every transformation below corresponds
to a numbered decision in the README's "Cleaning decisions" section.

Deliberately NOT done here, because the right choice depends on the analysis
question: dropping rows, imputing missing values, or choosing which sites to
analyse. Missing stays missing (empty cells in the CSV).
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUT_FILE = ROOT / "data" / "processed" / "heart_clean.csv"

SITES = {
    "cleveland": "processed.cleveland.data",
    "hungarian": "processed.hungarian.data",
    "switzerland": "processed.switzerland.data",
    "va": "processed.va.data",
}

RAW_COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num",
]

# D4: codes -> readable labels, from heart-disease.names.
LABELS = {
    "sex": {0: "female", 1: "male"},
    "cp": {1: "typical angina", 2: "atypical angina", 3: "non-anginal pain", 4: "asymptomatic"},
    "restecg": {0: "normal", 1: "ST-T abnormality", 2: "LV hypertrophy"},
    "slope": {1: "upsloping", 2: "flat", 3: "downsloping"},
    "thal": {3: "normal", 6: "fixed defect", 7: "reversible defect"},
}
BOOLEANS = ["fbs", "exang"]

# D5: clearer names for the analysis phase.
RENAME = {
    "cp": "chest_pain_type",
    "trestbps": "resting_bp",
    "chol": "cholesterol",
    "fbs": "fasting_blood_sugar_gt_120",
    "restecg": "resting_ecg",
    "thalach": "max_heart_rate",
    "exang": "exercise_angina",
    "oldpeak": "st_depression",
    "slope": "st_slope",
    "ca": "major_vessels",
    "thal": "thallium_result",
}

OUTPUT_ORDER = [
    "record_id", "site", "age", "sex", "chest_pain_type", "resting_bp",
    "cholesterol", "fasting_blood_sugar_gt_120", "resting_ecg", "max_heart_rate",
    "exercise_angina", "st_depression", "st_slope", "major_vessels",
    "thallium_result", "disease", "severity", "possible_duplicate",
]


def load_raw() -> pd.DataFrame:
    frames = []
    for site, filename in SITES.items():
        # D1: '?' is the missing-value marker actually used in these files.
        df = pd.read_csv(RAW_DIR / filename, header=None, names=RAW_COLUMNS, na_values="?")
        # D6: a traceable ID; the number is the line in the raw file (1-based).
        df.insert(0, "record_id", [f"{site}-{i:03d}" for i in range(1, len(df) + 1)])
        df.insert(1, "site", site)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # D2: a value of 0 is physiologically impossible for these two measurements;
    # it is how some sites recorded "not measured".
    for col in ["chol", "trestbps"]:
        df.loc[df[col] == 0, col] = pd.NA

    # D3: the target. 'disease' (0 vs >=1) is comparable across all sites.
    # 'severity' keeps 0-4, but the Hungarian file collapsed levels 1-4 into 1,
    # so a Hungarian positive has unknown severity.
    df["disease"] = (df["num"] > 0).astype("boolean")
    df["severity"] = df["num"].astype("Int64")
    df.loc[(df["site"] == "hungarian") & (df["num"] > 0), "severity"] = pd.NA

    # D4: decode categories and yes/no flags; whole numbers become nullable ints.
    for col, mapping in LABELS.items():
        df[col] = df[col].map(mapping).astype("string")
    for col in BOOLEANS:
        df[col] = df[col].map({0: False, 1: True}).astype("boolean")
    for col in ["age", "trestbps", "chol", "thalach", "ca"]:
        df[col] = df[col].round().astype("Int64")

    # D7: identical rows are kept but flagged; with no patient ID we cannot
    # tell a repeated record from two patients with identical measurements.
    df["possible_duplicate"] = df.duplicated(subset=RAW_COLUMNS, keep=False)

    # D8: negative st_depression (oldpeak) is kept as recorded.
    return df.drop(columns="num").rename(columns=RENAME)[OUTPUT_ORDER]


def validate(raw: pd.DataFrame, clean_df: pd.DataFrame) -> None:
    """Fail loudly if cleaning lost rows, invented values, or left a code unmapped."""
    assert len(clean_df) == len(raw) == 920, "row count changed"
    assert clean_df["record_id"].is_unique, "record_id not unique"
    for col, mapping in LABELS.items():
        name = RENAME.get(col, col)
        # a non-missing raw code must never become missing after decoding
        assert (raw[col].notna() == clean_df[name].notna()).all(), f"unmapped code in {col}"
    assert (clean_df["disease"] == (raw["num"] > 0)).all(), "disease flag wrong"
    assert (clean_df["cholesterol"].dropna() > 0).all(), "zero cholesterol remains"
    assert (clean_df["resting_bp"].dropna() > 0).all(), "zero blood pressure remains"


def main() -> None:
    raw = load_raw()
    clean_df = clean(raw)
    validate(raw, clean_df)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(OUT_FILE, index=False)

    print(f"Wrote {len(clean_df)} rows x {clean_df.shape[1]} columns to {OUT_FILE.relative_to(ROOT)}")
    print("\nDisease present, by site:")
    summary = clean_df.groupby("site", sort=False)["disease"].agg(["sum", "count"])
    summary["pct"] = (summary["sum"] / summary["count"] * 100).round(0).astype(int)
    print(summary.rename(columns={"sum": "disease", "count": "rows"}).to_string())
    print(f"\nRows flagged possible_duplicate: {int(clean_df['possible_duplicate'].sum())}")
    complete = clean_df.drop(columns=["severity"]).notna().all(axis=1)
    print(f"Rows with no missing values (ignoring severity): {int(complete.sum())}")


if __name__ == "__main__":
    main()
