"""Check that the raw files match the structure documented in heart-disease.names.

Usage:
    python src/check_structure.py

This is a read-only inspection of data/raw/: it changes nothing. It loads the
four processed files with the column names from the documentation, then
reports, per site and per column, the row counts, missing values, and whether
every value falls inside the documented codes or plausible ranges. Anything
unexpected is listed at the end as a finding for the cleaning phase.
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

SITES = {
    "cleveland": "processed.cleveland.data",
    "hungarian": "processed.hungarian.data",
    "switzerland": "processed.switzerland.data",
    "va": "processed.va.data",
}

# Documented row counts (heart-disease.names, section 5).
EXPECTED_ROWS = {"cleveland": 303, "hungarian": 294, "switzerland": 123, "va": 200}

# The 14 attributes used in the processed files, in file order
# (heart-disease.names, section 7, "Only 14 used").
COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num",
]

# Allowed codes for categorical columns, as documented.
CODES = {
    "sex": {0, 1},
    "cp": {1, 2, 3, 4},
    "fbs": {0, 1},
    "restecg": {0, 1, 2},
    "exang": {0, 1},
    "slope": {1, 2, 3},
    "ca": {0, 1, 2, 3},
    "thal": {3, 6, 7},
    "num": {0, 1},
}

# Physiologically plausible ranges for numeric columns. These are not from the
# documentation; they are loose sanity bounds to flag obvious recording errors.
RANGES = {
    "age": (18, 100),
    "trestbps": (60, 250),
    "chol": (80, 700),
    "thalach": (50, 250),
    "oldpeak": (-5, 10),
}


def load() -> pd.DataFrame:
    """Load all four sites into one frame. '?' is the missing-value marker
    actually used in the processed files (the docs say -9.0, which never occurs)."""
    frames = []
    for site, filename in SITES.items():
        df = pd.read_csv(RAW_DIR / filename, header=None, names=COLUMNS, na_values="?")
        df.insert(0, "site", site)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    df = load()
    findings = []

    print("Rows per site (actual vs documented):")
    for site, n in df["site"].value_counts(sort=False).items():
        flag = "OK" if n == EXPECTED_ROWS[site] else "MISMATCH"
        print(f"  {site:<12}{n:>5}  expected {EXPECTED_ROWS[site]:>4}  {flag}")
        if flag != "OK":
            findings.append(f"{site}: {n} rows, documentation says {EXPECTED_ROWS[site]}")

    non_numeric = [c for c in COLUMNS if not pd.api.types.is_numeric_dtype(df[c])]
    if non_numeric:
        findings.append(f"columns not parsed as numbers: {non_numeric}")

    print("\nMissing values (% of rows) by site:")
    missing = df.drop(columns="site").isna().groupby(df["site"], sort=False).mean().mul(100).round(0)
    print(missing.T.astype(int).to_string())

    print("\nValues outside documented codes / plausible ranges:")
    for col in COLUMNS:
        values = df[col].dropna()
        if col in CODES:
            bad = values[~values.isin(CODES[col])]
            rule = f"codes {sorted(CODES[col])}"
        elif col in RANGES:
            lo, hi = RANGES[col]
            bad = values[(values < lo) | (values > hi)]
            rule = f"range {lo}-{hi}"
        else:
            continue
        if bad.empty:
            print(f"  {col:<9} OK ({rule})")
        else:
            counts = bad.value_counts().sort_index()
            summary = ", ".join(f"{v:g}: {c}" for v, c in counts.items())
            print(f"  {col:<9} {len(bad)} outside {rule} -> {summary}")
            findings.append(f"{col}: {len(bad)} values outside {rule} ({summary})")

    exact_dupes = df.duplicated(subset=COLUMNS).sum()
    print(f"\nExact duplicate rows across all sites: {exact_dupes}")
    if exact_dupes:
        findings.append(f"{exact_dupes} exact duplicate row(s)")

    print(f"\nTotal: {len(df)} rows x {len(COLUMNS)} columns")
    print("\nFindings for the cleaning phase:")
    for f in findings or ["none"]:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
