"""Make the plain-language "story" charts used at the top of reports/REPORT.md.

Usage:
    python src/make_report_figures.py

The analysis notebooks (03-06) hold the technical charts. These two are for a
reader with no statistics background: simple percentages, direct labels, and a
title that states the takeaway. Every grouping here follows a conclusion
reached in the notebooks; the percentages themselves are simple (unadjusted)
rates, and the chart says so.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from clean_data import load_clean

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "reports" / "figures"

SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE = "#2a78d6"
# Two shades of one hue for "without" -> "with" (validated as an ordinal pair).
LIGHT, DARK = "#86b6ef", "#1c5cab"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "font.size": 10,
    "xtick.color": INK_2, "ytick.color": INK_2,
})


def clean_axes(ax):
    ax.tick_params(length=0)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)


def hospitals_chart(df):
    """Share of patients with heart disease at each hospital."""
    names = {"hungarian": "Budapest, Hungary", "cleveland": "Cleveland, USA",
             "va": "Long Beach VA, USA", "switzerland": "Zurich & Basel, Switzerland"}
    rates = df.groupby("site", observed=True)["disease"].agg(["mean", "count"])
    rates = rates.sort_values("mean")
    y = np.arange(len(rates))

    fig, ax = plt.subplots(figsize=(8, 3.9))
    ax.barh(y, rates["mean"] * 100, height=0.58, color=BLUE)
    for yi, (site, r) in zip(y, rates.iterrows()):
        ax.text(r["mean"] * 100 + 1.5, yi, f"{r['mean']:.0%}", va="center",
                fontsize=11, fontweight="bold", color=INK)
    ax.set_yticks(y, [f"{names[s]}\n{r['count']} patients" for s, r in rates.iterrows()],
                  fontsize=9.5, color=INK)
    ax.set_xlim(0, 118)
    ax.set_xticks([])
    clean_axes(ax)
    ax.spines["bottom"].set_visible(False)
    fig.suptitle("Heart disease was found in 36% to 93% of patients, depending on the hospital",
                 x=0.01, ha="left", fontsize=12, fontweight="bold", color=INK)
    fig.text(0.01, 0.83, "All 920 patients had been referred for a heart X-ray (angiogram). Hospitals referred\n"
             "very different groups of patients, so the analysis compares patients within the same hospital.",
             fontsize=8.5, color=INK_2)
    fig.subplots_adjust(left=0.27, right=0.98, top=0.73, bottom=0.05)
    fig.savefig(FIG_DIR / "story_1_hospitals.png", dpi=200)
    plt.close(fig)


def warning_signs_chart(cle):
    """Disease rate with vs without each sign (Cleveland), grouped by what the
    full analysis concluded about the sign."""
    def rate(mask):
        return cle.loc[mask, "disease"].mean() * 100

    held_up = [
        ("Chest pain brought on by exercise", cle["exercise_angina"] == True,  # noqa: E712
         cle["exercise_angina"] == False),  # noqa: E712
        ("Abnormal exercise ECG\n(ST depression of 1 or more)", cle["st_depression"] >= 1,
         cle["st_depression"] < 1),
        ("No chest pain at rest\n(vs atypical or non-heart-type pain)",
         cle["chest_pain_type"] == "asymptomatic",
         cle["chest_pain_type"].isin(["atypical angina", "non-anginal pain"])),
        ("Male (vs female)", cle["sex"] == "male", cle["sex"] == "female"),
    ]
    faded = [
        ("Age 60 or over", cle["age"] >= 60, cle["age"] < 60),
        ("Blood pressure 140 or higher", cle["resting_bp"] >= 140, cle["resting_bp"] < 140),
        ("Cholesterol 240 or higher", cle["cholesterol"] >= 240, cle["cholesterol"] < 240),
        ("High fasting blood sugar", cle["fasting_blood_sugar_gt_120"] == True,  # noqa: E712
         cle["fasting_blood_sugar_gt_120"] == False),  # noqa: E712
    ]

    fig, axes = plt.subplots(2, 1, figsize=(8.6, 6.8), sharex=True,
                             gridspec_kw={"height_ratios": [len(held_up), len(faded)], "hspace": 0.45})
    sections = [
        (axes[0], held_up, "Strong links, confirmed at the other hospitals"),
        (axes[1], faded, "Smaller gaps that did not hold up once other factors were taken into account"),
    ]
    for ax, rows, title in sections:
        y = np.arange(len(rows))[::-1]
        for yi, (label, with_, without) in zip(y, rows):
            a, b = rate(without), rate(with_)
            ax.plot([a, b], [yi, yi], color=GRID, linewidth=3, zorder=1, solid_capstyle="round")
            ax.scatter([a], [yi], s=90, color=LIGHT, zorder=2)
            ax.scatter([b], [yi], s=90, color=DARK, zorder=2)
            lo, hi = sorted([(a, "without"), (b, "with")])
            for x, kind, ha, dx in [(lo[0], lo[1], "right", -3), (hi[0], hi[1], "left", 3)]:
                ax.text(x + dx, yi, f"{x:.0f}%", ha=ha, va="center", fontsize=9.5,
                        color=INK if kind == "with" else INK_2,
                        fontweight="bold" if kind == "with" else "normal")
        ax.set_yticks(y, [r[0] for r in rows], fontsize=9.5, color=INK)
        ax.set_ylim(-0.6, len(rows) - 0.4)
        ax.set_title(title, loc="left", fontsize=10.5, color=INK, pad=8)
        ax.grid(axis="x", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        clean_axes(ax)
    axes[1].set_xlim(0, 100)
    axes[1].set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    axes[1].set_xlabel("Share of patients with heart disease", color=INK_2, fontsize=9)

    fig.suptitle("Four signs stood out, and they held up at other hospitals",
                 x=0.01, y=0.985, ha="left", fontsize=12, fontweight="bold", color=INK)
    fig.text(0.01, 0.915, "Share of Cleveland patients (303) with heart disease, among those without and "
             "with each sign.\nSimple percentages; which signs hold up comes from the full analysis.",
             fontsize=8.5, color=INK_2, va="center")
    handles = [plt.Line2D([], [], marker="o", linestyle="none", markersize=9, color=c, label=l)
               for c, l in [(LIGHT, "Without the sign"), (DARK, "With the sign")]]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.005, 0.885), ncol=2,
               frameon=False, fontsize=9, handletextpad=0.3, columnspacing=1.2)
    fig.subplots_adjust(left=0.33, right=0.97, top=0.80, bottom=0.08)
    fig.savefig(FIG_DIR / "story_2_warning_signs.png", dpi=200)
    plt.close(fig)


def main():
    df = load_clean()
    hospitals_chart(df)
    warning_signs_chart(df[df["site"] == "cleveland"])
    print("Wrote story_1_hospitals.png and story_2_warning_signs.png to reports/figures/")


if __name__ == "__main__":
    main()
