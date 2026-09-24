# Learning Guide: Understanding and Defending This Project

This guide is for me, the author. It explains every medical idea, statistical
technique and coding concept in the project in plain language, why each choice
was made, and how to answer questions about it in an interview. It assumes
**no medical background**.

**How to use it:** read Part 1 once so the medical terms stop being a barrier.
Parts 2–5 follow the project from start to finish. Part 6 is interview
practice, and Part 7 is a one-page cheat sheet of numbers to know.

---

## Part 1: The medical background you need

You don't need to be a clinician to analyse this data. You do need to know
what each column measures, so you can explain the results and avoid saying
something wrong.

### 1.1 What "heart disease" means here

The heart is a muscle, and it needs its own blood supply. That supply comes
through the **coronary arteries**, which wrap around the outside of the
heart. In **coronary artery disease**, fatty deposits (plaque) build up inside
these arteries and narrow them, so less blood gets through.

In this dataset, **"disease" means an angiogram showed more than 50%
narrowing in at least one major coronary artery.** That is the outcome
(`disease` = True) everything else is compared against.

### 1.2 The angiogram: where the diagnosis comes from

An **angiogram** (also called *cardiac catheterisation*) is an invasive test.
A thin tube is threaded through a blood vessel to the heart, dye is
injected, and X-ray video shows how well the dye flows through the coronary
arteries. Narrowings show up directly. It was the reference standard for
diagnosing coronary artery disease, which is why it defines the outcome.

**Why this matters for the analysis:** nobody gets an angiogram for fun.
Every patient in this dataset was **referred** because a doctor already
suspected heart disease. So the sample is not "people in general", it's
"people a doctor was worried about". This is called **referral bias** (or
**spectrum bias**), and it explains several results (see 1.5).

### 1.3 Every column, in plain language

| Column | What it is | Plain-language meaning |
|---|---|---|
| `age`, `sex` | Demographics | Self-explanatory |
| `chest_pain_type` | Type of chest pain the patient reported | See the chest pain box below |
| `resting_bp` | Resting blood pressure, in mm Hg (millimetres of mercury, the standard pressure unit) | Measured on admission. Usually read as the *top* number (systolic), though the documentation doesn't say. Around 120 is typical; 140+ is commonly called high |
| `cholesterol` | Total cholesterol in the blood, in mg/dl | A fat-like substance; high levels are a known long-term risk factor. Under 200 is commonly called desirable; 240+ high |
| `fasting_blood_sugar_gt_120` | Blood sugar after not eating, above 120 mg/dl? | A rough marker for diabetes, itself a heart risk factor |
| `resting_ecg` | Resting electrocardiogram result | An **ECG** records the heart's electrical activity as a wavy line. "LV hypertrophy" means the pattern suggests a thickened main pumping chamber (left ventricle), often from long-term high blood pressure. "ST-T abnormality" means part of the wave looks abnormal |
| `max_heart_rate` | Highest heart rate reached on a treadmill **exercise test** | Healthy hearts speed up a lot under exercise; a heart that can't reach a high rate is a warning sign |
| `exercise_angina` | Did the exercise test bring on chest pain? | **Angina** = chest pain caused by the heart muscle not getting enough blood. If exercise triggers it, that's a classic sign of narrowed arteries |
| `st_depression` | How far part of the ECG wave (the "ST segment") drops during exercise compared with rest | When heart muscle is short of oxygen under effort, this part of the tracing dips down. Bigger dip = more concerning. Conventionally measured in mm on the ECG paper (the documentation doesn't state the unit) |
| `st_slope` | Shape of that ST segment at peak exercise: upsloping, flat, downsloping | Upsloping is generally the more reassuring pattern; flat or downsloping more concerning |
| `major_vessels` | Number of major vessels (0–3) coloured by fluoroscopy | **Fluoroscopy** is live X-ray imaging. Commonly interpreted as how many major vessels showed up with dye. It comes from imaging close to the angiogram itself |
| `thallium_result` | Thallium stress test: normal, fixed defect, reversible defect | A nuclear scan: a small radioactive tracer (thallium) shows where blood reaches the heart muscle, under stress and at rest. **Reversible defect** = an area short of blood during stress that recovers at rest (a sign of narrowed arteries). **Fixed defect** = an area with poor blood flow both times, often scar from a past heart attack |
| `severity` | Original 0–4 diagnosis level | 0 = no disease; 1–4 = increasing severity (not comparable across sites, see Part 3) |

**Chest pain types:**
- **Typical angina:** the classic heart pattern. Pressure-like pain behind
  the breastbone, brought on by exertion, relieved by rest.
- **Atypical angina:** some but not all of those features.
- **Non-anginal pain:** chest pain that doesn't look heart-related (for
  example muscular).
- **Asymptomatic:** *no chest pain at all.*

### 1.4 The exercise test in one paragraph

The patient walks on a treadmill that gets faster and steeper while an ECG
records their heart. Doctors watch for three things: whether chest pain
appears (`exercise_angina`), how high the heart rate gets (`max_heart_rate`),
and whether the ST segment of the ECG dips (`st_depression`, `st_slope`).
**Four of the columns come from this one test**, which is why they overlap
statistically (Part 4.5).

### 1.5 Two medical-context results you must be able to explain

1. **"Why does *no* chest pain go with *more* disease?"** In the general
   population it wouldn't. But these patients were referred for an
   angiogram. Someone with no chest pain was probably referred because
   something else was already abnormal, such as an exercise test. Someone
   with odd, non-heart-type pain may have been referred "to be safe". So
   within this referred group, "no chest pain" marks a different kind of
   patient. **Say it's a hypothesis:** the data can't prove why.
2. **"Why don't cholesterol and blood pressure matter here? They're famous
   risk factors!"** They *are* risk factors, over years, for developing
   disease in the general population. But this sample is already
   pre-selected as high-suspicion. Inside such a group those factors
   separate patients less well. This is **spectrum bias**, not evidence that
   cholesterol is harmless. The same shrinking happens to any trait when you
   look only among people already selected partly because of it.

### 1.6 How to handle medical questions in an interview

You are an analyst, not a clinician, and that's fine. A good pattern:

> "Clinically I'd defer to a cardiologist, but here's what the data shows and
> how I checked it. And here's the limitation I'd flag before anyone used it."

Never claim a finding is medically true. Claim that it's what the data shows,
with its uncertainty and its limits. Interviewers are testing judgement, and
knowing where your expertise ends is part of that.

---

## Part 2: Getting the data (Phase 1)

### 2.1 Why download from UCI instead of Kaggle
The popular Kaggle `heart.csv` has 1,025 rows, but most are duplicates of the
same ~300 patients. Duplicates inflate sample size and make models look better
than they are, because the same patient can land in both training and test
data. **Interview line:** *"I checked provenance before analysing. The popular
version was mostly duplicates, so I went to the original source."*

### 2.2 Reproducible download: `src/download_data.py`
| Concept | What it is | Why |
|---|---|---|
| **SHA-256 checksum** | A 64-character fingerprint of a file's exact bytes; change one byte and it changes completely | Proves the data I analysed is identical to what anyone else downloads; detects corruption or silent upstream changes |
| **Pinned manifest** (`SHA256SUMS`) | Checksums recorded on first run, verified on every later run | Makes "raw data is never edited" enforceable, not just a promise |
| **Atomic write** | Download to `file.part`, then rename | A crash mid-download never leaves a half-file that looks complete |
| **`raise_for_status()`, timeout** | Fail loudly on HTTP errors, never hang | Silent failures are worse than loud ones |
| **`argparse`** | Standard library for command-line flags (`--verify`, `--force`) | Same script can download, re-download or just verify |
| **`pathlib.Path`** | Object-oriented file paths | `Path(__file__).resolve().parent.parent` finds the project root from any working directory |

### 2.3 Checking structure against documentation: `src/check_structure.py`
Never trust the documentation blindly. Comparing files with their docs found
six problems (Part 3). **Interview line:** *"The documentation said missing
values were -9. The files actually used '?'. If I had trusted the docs, I'd
have treated '?' as text and broken every numeric column."*

### 2.4 Pinned environment: `requirements.txt`
Exact versions (`pandas==3.0.6`), so results don't change when a library
updates. A virtual environment (`.venv`) keeps project libraries separate
from the system's.

### 2.5 Licensing and ethics
The data is CC BY 4.0: free to share and adapt, with credit. The original
76-column files once contained names and Social Security numbers (since
replaced with dummies). `.gitignore` blocks those files so they can never be
committed. Age and sex are **quasi-identifiers** (combined with other data
they could help re-identify someone), so only aggregate results are reported.

---

## Part 3: Cleaning the data (Phase 2)

### 3.1 The principle: raw is read-only, cleaning is code
Every change is made by `src/clean_data.py`, never by hand, and each maps to a
numbered decision (D1–D8 in the README). Anyone can re-run it and get the
byte-identical file.

### 3.2 Each decision and the concept behind it
| Decision | Concept | What to say |
|---|---|---|
| D1 `?` → missing | **Missing-value encoding**: `pd.read_csv(..., na_values="?")` | "Missing data had a non-standard marker" |
| D2 `0` cholesterol → missing | **Impossible values as disguised missing data** | "A cholesterol of zero means 'not measured'. Left in, 172 zeros would drag every average down" |
| D3 `disease` + `severity` | **Harmonising a target across sources** | "Hungary collapsed severity 1–4 into 1. Only yes/no is comparable, so that's the target. Hungarian severity is left blank rather than wrongly '1'" |
| D4 decode categories | **Categorical data types** with documented order | "Chest pain types stay in the documented 1–4 order, not alphabetical" |
| D6 `record_id` | **Traceability / lineage** | "Every cleaned row links back to its raw line" |
| D7 flag duplicates | **Don't delete what you can't prove** | "Without a patient ID I can't prove they're repeats, so I flagged them and showed results don't change without them" |
| No imputation | **Separation of concerns** | "Filling in missing values depends on the analysis question, so cleaning doesn't do it" |

### 3.3 Code concepts in cleaning
- **Nullable dtypes** (`Int64`, `boolean`): ordinary NumPy integers can't hold
  missing values, so pandas silently turns them into decimals (`125.0`).
  Capital-I `Int64` keeps whole numbers *and* allows missing.
- **`pd.CategoricalDtype(order)`**: a column restricted to known labels, in a
  set order. **Trap:** converting a value not in the list silently turns it
  into missing. `apply_types()` checks missing counts before and after and
  refuses if they change.
- **Why `load_clean()` exists:** a CSV stores only text, so types are lost when
  saving. One function sets types on both the way out and the way in, so
  they can't drift apart.
- **`assert` as a guardrail:** the script stops if rows are lost, a code is
  unmapped, or the saved file doesn't load back identical
  (`pd.testing.assert_frame_equal`).
- **Verification notebook (02):** an independent audit. It reconciles raw and
  clean column by column and proves the only lost values are the zeros.

---

## Part 4: The analysis (Phase 3)

### 4.1 The overall strategy (worth explaining in any interview)
1. **Describe** one variable at a time (notebook 03).
2. **Quantify** size and uncertainty, and correct for many tests (04).
3. **Adjust** predictors for each other (05).
4. **Replicate** on independent patients (06).

Each step checks the previous one. Several "findings" changed along the way
(age disappeared, sex got stronger, typical angina didn't replicate), which
is exactly why the steps exist.

### 4.2 Describing data (notebook 03)
- **Median and IQR, not mean and standard deviation:** the median is the
  middle value, and the **interquartile range (IQR)** is the range of the
  middle 50% of patients. Both ignore extremes. One cholesterol of 564 would
  pull a mean up but not the median. Use them for skewed data.
- **Jittered strip plot + box:** every patient is a dot (spread sideways so
  they don't overlap), with a box for the middle half. It shows the whole
  distribution, not just a summary.
- **Rate per category with counts:** always show *n*. "75% (3 of 4 patients)"
  is noise, not a finding.

### 4.3 Effect sizes, confidence intervals and p-values (notebook 04)
**The distinction interviewers love:**
- **Effect size:** *how big* the difference is.
- **Confidence interval:** *how precisely* we know it.
- **p-value:** *how surprising* the data would be if there were no difference.
  It is **not** the probability the finding is true, and a tiny p-value can
  go with a trivially small effect in a big sample.

| Technique | Plain explanation | Why here |
|---|---|---|
| **Mann–Whitney U test** | Rank all patients; test whether one group's ranks are systematically higher | Doesn't assume bell-shaped data; ST depression piles up at 0 |
| **Probability of superiority (PS)** | Chance a random patient with disease has the higher value than a random one without. 0.5 = no difference | Intuitive; equals U / (n₁·n₂), so the test and the effect size agree |
| **Chi-square test** | Compares observed counts in a table with the counts expected if there were no link | Standard for categorical vs categorical |
| **Expected count < 5 rule** | The chi-square p-value formula is an approximation that breaks down with small cells | Resting ECG had a 4-patient category |
| **Permutation test** | Shuffle the disease labels thousands of times; how often does chance produce a result this extreme? | Assumption-free p-value for small tables |
| **Cramér's V** | Strength of a categorical association, 0 to 1 | Comparable across tables of different sizes |
| **Bootstrap confidence interval** | Resample patients with replacement 2,000 times, recompute, take the middle 95% | No formula needed; works for any statistic |
| **Multiple testing** | 13 tests at 0.05 → about a 49% chance of at least one false alarm (1 − 0.95¹³) | We tested 13 predictors |
| **Holm correction** | Sort p-values; compare the smallest with 0.05/13, the next with 0.05/12, and so on; stop at the first failure | Controls false alarms; always at least as powerful as Bonferroni |

**Key example to remember:** cholesterol had p = 0.035 alone ("significant")
but 0.078 after Holm correction. That is the false alarm the correction
exists to catch.

### 4.4 Logistic regression (notebook 05)
- **Why logistic, not linear:** the outcome is yes/no. Logistic regression
  models the *log-odds* of disease as a straight-line function of the
  predictors, which keeps predicted probabilities between 0 and 1.
- **Odds:** p / (1 − p). A 75% chance = odds of 3 (3 to 1).
- **Odds ratio (OR):** how much the odds multiply when a predictor changes by
  one unit, *holding the others constant*. OR 2 = double the odds; 0.5 =
  half; 1 = no change.
- **Odds ratio ≠ risk ratio.** When disease is common (46% here), an OR
  overstates how much the *probability* changes. Say "odds", not "twice as
  likely".
- **Scaling predictors** (per 10 years, per 10 bpm): makes ORs readable.
- **Reference categories:** each category is compared with a baseline. I chose
  the largest group ("asymptomatic", 144 patients) for stable estimates.
- **Events per variable (EPV):** rule of thumb of about 10 outcome cases per
  coefficient. Models A and B had 9.8 and 8.1, which is borderline, so I
  flagged it.
- **statsmodels formula API:** `smf.logit("disease ~ age_10 + C(chest_pain,
  Treatment('asymptomatic'))", data)`. `C()` marks a categorical variable and
  `Treatment('x')` sets its reference level.
- **Log scale on odds-ratio charts:** ORs are multiplicative, so 0.5 and 2 are
  equally strong in opposite directions and should sit equally far from 1.

### 4.5 Confounding and overlap: why results changed after adjustment
- **Confounding:** a third variable tied to both the predictor and the outcome.
  *Age* looked important alone, but older patients also had lower max heart
  rates and more diseased vessels. Once those were in the model, age added
  nothing of its own.
- **Negative confounding** (effect *grows* after adjustment): *sex* went from
  OR 3.6 to 7.5. Women in the sample were slightly older with higher
  cholesterol, which predict *more* disease, so the raw comparison hid part of
  the gap.
- **Collinearity:** the four exercise-test measures carry overlapping
  information. Together, each gets less individual credit, so wider
  intervals appear even though the group as a whole is predictive.

### 4.6 Judging a model honestly
| Concept | Plain explanation |
|---|---|
| **AUC** (area under the ROC curve) | Chance the model gives a random patient with disease a higher risk than a random patient without. 0.5 = coin toss, 1 = perfect. Same idea as probability of superiority |
| **Over-fitting** | A model partly memorises the quirks of the data it's fitted to, so it looks better on that data than on new data |
| **Cross-validation** | Split into 10 parts; fit on 9 and predict the 10th; rotate. Every patient is scored by a model that never saw them |
| **Stratified folds** | Each part keeps the same share of disease cases as the whole |
| **Repeated CV** | Random splits vary, so repeat 20 times and average |
| **Likelihood-ratio test** | Does a bigger model (B) fit better than a smaller one (A) by more than its extra parameters would by chance? |

**Number to remember:** the AUC on the fitting data was about 0.03 higher
than the cross-validated AUC. That gap is the over-fitting.

### 4.7 Replication and transport (notebook 06)
- **Replication:** same model, different patients. It is the strongest
  defence against one-sample flukes.
- **Site term (fixed effect):** a separate baseline for each hospital, so
  predictors are compared *within* hospitals. Without it, Switzerland's 93%
  disease rate would contaminate every estimate.
- **Interaction term:** lets a predictor's effect *differ* at Cleveland. Its
  test asks "is Cleveland's odds ratio different?"
- **Discrimination vs calibration:** a model can *rank* patients well (high
  AUC) but get the *risk levels* wrong. The Cleveland model predicted 70% for
  Swiss patients when 93% had disease: it inherited Cleveland's baseline.
- **Missing not at random:** at VA, patients without disease were dropped more
  often (41% vs 26%). Dropping incomplete rows is only safe when missingness
  is unrelated to the outcome.
- **Sensitivity analysis:** re-run with a different reasonable choice (here,
  without the duplicates) and show conclusions don't change.

### 4.8 Data-visualisation choices
- **Colour has a job:** blue/orange for no disease vs disease (checked for
  colour-blind separation with a validator); a single-hue ramp for "how
  much" (missing-data heatmap); two shades of one hue for without vs with.
- **Filled vs hollow dots:** significance shown by shape as well as colour,
  so it survives greyscale printing and colour-blindness.
- **Titles state the takeaway** in the story charts ("Four signs stood
  out..."), while analysis charts stay neutral.
- **Honest grouping:** the story chart shows raw percentages, but groups the
  signs by what the *adjusted* analysis concluded, and says so.

---

## Part 5: Engineering practices worth mentioning

- **Scripts for pipeline steps, notebooks for analysis.** Scripts are
  re-runnable and testable; notebooks mix code, output and explanation.
  Notebooks are committed **executed**, so GitHub shows the results.
- **Fixed random seeds** (`np.random.default_rng(42)`): bootstraps and CV
  splits give identical results every run.
- **Every claim is computed in the notebook that makes it.** When I quoted a
  correlation in text, I added a cell that computes it.
- **Small, descriptive git commits per step:** the history shows how the work
  progressed.
- **Reuse over duplication:** notebooks import `load_clean()` from
  `src/clean_data.py`, so there's one definition of the data.

---

## Part 6: Interview questions, with answers

**"Why did you pick this project?"**
> Two reasons. I'm always working to get better at Python and machine
> learning, and the best way I know is to take a real dataset all the way
> from raw files to a finished report. And healthcare hires a lot of data
> analysts, so I wanted to learn how clinical data behaves. I don't have a
> medical background, so I had to learn the terms as I went. That turned out
> to be useful, because it forced me to check what every column meant before
> trusting it.

**"Walk me through the project in two minutes."**
> I took the original UCI heart disease data, 920 patients from four
> hospitals, rather than the popular Kaggle copy, which is mostly duplicates.
> I verified the files against their documentation, found six discrepancies
> (disguised missing values, a collapsed outcome at one site), and fixed them
> in a logged, reproducible cleaning script. Then I analysed Cleveland in
> four stages: describe, test with effect sizes and multiple-testing
> correction, adjust with logistic regression, and replicate at the other
> three hospitals. Four signs held up everywhere: ST depression on the
> exercise ECG, exercise-induced chest pain, male sex, and having no chest
> pain versus atypical pain. Routine measurements alone reached a
> cross-validated AUC of 0.87.

**"What was the most surprising finding?"**
> Patients with no chest pain had the highest disease rate. It's
> counter-intuitive, but it fits the referral context: they were probably
> sent for an angiogram because another test was abnormal. I present it as
> a hypothesis, because the data can't prove the mechanism.

**"Why isn't cholesterol significant? Isn't that wrong?"**
> It's not wrong, it's selection. Everyone here was already referred as
> high-suspicion, which compresses differences in classic risk factors. It
> reached p = 0.035 alone but not after correcting for 13 tests, and its
> effect was small. I'd never tell someone cholesterol doesn't matter from
> this data.

**"Why Mann–Whitney instead of a t-test?"**
> ST depression piles up at zero and cholesterol is right-skewed. Mann–Whitney
> doesn't assume normality, and its statistic converts directly into an
> intuitive effect size, the probability of superiority.

**"What's the difference between a p-value and an effect size?"**
> The effect size is how big the difference is. The p-value is how surprising
> the data would be if there were no difference. With enough data, a tiny,
> useless effect gets a tiny p-value, so I lead with effect sizes and
> intervals.

**"Explain an odds ratio to a non-technical person."**
> Odds compare the chance something happens with the chance it doesn't. An
> odds ratio of 2 for exercise chest pain means that among otherwise-similar
> patients, the odds of disease are twice as high with it. It's not quite
> "twice as likely", especially when disease is common.

**"Why did age stop mattering in the model?"**
> Confounding. Older patients also had lower max heart rates and more
> diseased vessels. Once those were in the model, age had nothing extra to
> contribute.

**"How do you know your model isn't over-fitted?"**
> I scored it with 20-times-repeated stratified 10-fold cross-validation, so
> every patient was predicted by a model that never saw them. The
> cross-validated AUC was about 0.03 below the fitting-data AUC, and I report
> the cross-validated number. I also flagged that events per variable were
> near the rule-of-thumb limit.

**"How did you handle missing data? Would you do anything differently?"**
> Cleveland was almost complete, so its analysis dropped just 6 patients. For
> the four-site check I used complete cases on 7 shared predictors, but I
> found that VA's missingness was related to the outcome, which can bias
> results. Next I'd use multiple imputation and compare.

**"What does AUC 0.87 mean?"**
> If you pick one patient with disease and one without, the model gives the
> patient with disease the higher risk 87% of the time.

**"Would you deploy this model?"**
> No. It's from referred patients before 1988, it's miscalibrated at other
> sites, and it hasn't been clinically validated. It's an analysis of
> associations, not a diagnostic tool. Making it one would need recent data,
> recalibration and clinical oversight.

**"What would you do with more time?"**
> Multiple imputation, penalised regression for stability, calibration curves
> with recalibration per site, and a mixed-effects model with a random effect
> for hospital.

**"How did you make it reproducible?"**
> Checksummed raw data, pinned library versions, scripted cleaning with
> assertions, fixed random seeds, executed notebooks committed with outputs,
> and one command sequence in the report to rebuild everything.

---

## Part 7: Cheat sheet: numbers to know

| Fact | Number |
|---|---|
| Patients / hospitals | 920 / 4 |
| Cleveland patients / with disease | 303 / 139 (46%) |
| Disease rate range across hospitals | 36% (Hungary) to 93% (Switzerland) |
| Predictors | 13 (7 recorded at every site) |
| Significant after Holm correction | 10 of 13 |
| Cholesterol p alone → after Holm | 0.035 → 0.078 |
| Exercise chest pain: disease rate with / without | 77% / 31% |
| ST depression OR, Cleveland / other sites | 1.97 / 1.86 |
| Male OR, unadjusted → adjusted (Model A) | 3.6 → 7.5 |
| Cross-validated AUC, routine only / with imaging | 0.87 / 0.90 |
| Cleveland model AUC at Hungary | 0.87 |
| Swiss predicted vs actual disease | 70% vs 93% |
| Duplicates effect on results | ≤ 3.6% change |
