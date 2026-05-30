# inference-workbench

A stateful, advisory reasoning environment for inferential statistics.

`inference-workbench` is not a calculator. It runs real code on your data,
holds the analysis as a workflow state, and pushes back on your choices the
way a senior colleague would — surfacing assumption violations, qualifying
conclusions, and suggesting alternatives when methods are inappropriate.

The human stays in the driver's seat. The app advises, the analyst decides.

---

## Project philosophy — advisory, not automated

`inference-workbench` is decision-support, not decision-replacement. It
enforces a reasoning workflow and surfaces evidence; it does not pick the
model, run the analysis end-to-end, and hand the user a conclusion.

This is deliberate. Calculators are a solved problem — JASP, jamovi, SPSS,
statsmodels, and R all fit regressions fine. What is harder, and what this
project encodes, is the *judgment* around the calculation: when an
assumption violation should reroute the analysis, when an unadjusted
finding gets overturned by an adjusted one, when a coefficient should be
qualified rather than asserted.

That judgment lives in the procedural advisory layer, not in user
discretion. The app errs toward pushback, not silence — a wrong nudge
costs the analyst two seconds; a silent omission can corrupt a conclusion.

---

## Status

**v1 scope: binomial logistic regression, end to end.** This is a
deliberate single-family v1. Other regression families (OLS, ordinal,
survival, hierarchical, Bayesian) and broader hypothesis-test
infrastructure are tracked in `FUTURE_FEATURES.md`.

This repo is in active scaffolding. Module directories exist; the
Streamlit app and workflow logic are forthcoming. See `NEXT_TASKS.md`
for the current task list.

---

## Audience

`inference-workbench` is designed for working analysts with baseline
statistical literacy — people who know what a residual is, what a p-value
means, why proportional hazards matters. It does not teach statistics.

Learners and weaker practitioners may find value, but the app is not
designed to hold their hand through fundamentals. Audience choice is
load-bearing — it is why the app can be terse, why it skips remedial
explanations, and why pushback is direct rather than hedged.

---

## What it does

- **Profiles uploaded data.** Surfaces missingness, type mismatches,
  suspicious distributions, near-constant variables, high-cardinality
  categoricals, and likely outliers. Does not fix them — the analyst
  decides what to do.
- **Classifies variables.** Proposes Type (continuous / binary / ordinal /
  nominal / count) and asks the analyst to confirm Role (outcome /
  predictor / control / mediator / fairness variable). This classification
  routes the rest of the workflow.
- **Enforces a workflow.** Sequences the analysis through problem framing,
  data understanding, conceptual modeling, model selection, estimation,
  diagnostics, sensitivity, and conclusion. Steps gate on prior steps.
- **Runs real diagnostics.** Multicollinearity, separation, model
  convergence, ROC-AUC, calibration. Results are computed facts, not
  generated claims.
- **Nests hypothesis tests as evidence checks.** Chi-square, t-tests, and
  related tests appear as screening or confirmatory steps inside the
  workflow — never as destinations. Unadjusted findings are explicitly
  compared against adjusted findings.
- **Pushes back.** When a diagnostic fails or a method choice is
  questionable, the app states the issue plainly and proposes alternatives.
  The analyst can override; overrides are recorded.
- **Exports a reproducible report.** The full reasoning chain — what was
  asked, what was classified, what was checked, what was found, what was
  caveated — is exportable as a single artifact.

## What it does not do

- **It is not a calculator.** Use JASP, jamovi, statsmodels, or R for
  computation without reasoning structure.
- **It is not a tutor.** It assumes baseline statistical literacy. No
  remedial explanations, no glossary tooltips.
- **It is not a decision engine.** It does not pick models, run analyses
  end-to-end, or generate conclusions without analyst input.
- **It is not a data-cleaning tool.** It profiles and surfaces; it does not
  impute, transform, or fix data without explicit direction.
- **It is not domain-specific.** People-analytics examples seeded the
  design (the worked exercises behind v1 come from McNulty's *Handbook of
  Regression Modeling in People Analytics*), but the reasoning core is
  domain-general.

---

## Architecture in brief

Eight modules, each with a single job, imports flowing one direction:

```
app -> workflow -> models -> diagnostics -> data_io
                -> profile -> advise -> report
```

- `data_io/` — the only code that reads or writes data files
- `profile/` — Level 2 data profiling (surface issues; do not fix)
- `workflow/` — the workflow state machine and step gating
- `models/` — model families (binomial logistic for v1)
- `diagnostics/` — assumption checks, evidence tests
- `advise/` — procedural pushback rules
- `report/` — reproducible report export
- `app/` — Streamlit presentation layer

See `ARCHITECTURE.md` for the locked design decisions and module
contracts.

---

## Where to look

| Doc | What's in it |
|---|---|
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | Locked design decisions, module structure, seam rules, design rationale |
| **[NEXT_TASKS.md](./NEXT_TASKS.md)** | Short-horizon task list for v1 |
| **[FUTURE_FEATURES.md](./FUTURE_FEATURES.md)** | Parking lot: anything not in v1 |
| **[REPO_SETUP_PROCEDURE.md](./REPO_SETUP_PROCEDURE.md)** | Personal procedure for creating GitHub-backed repos (generic, not specific to this project) |
| **[SECURE_GIT_WORKFLOW.md](./SECURE_GIT_WORKFLOW.md)** | Personal procedure for authenticated git operations using a gpg-encrypted token (generic) |

For new readers: read this README, then ARCHITECTURE.

---

## Setup and run

Requires [conda](https://docs.conda.io/) (Miniconda or Anaconda) and git.

```bash
# Clone
git clone https://github.com/ARCtechmo/inference-workbench.git
cd inference-workbench

# Create the environment (Python 3.11)
conda create -n inference-workbench python=3.11 -y

# Activate it
conda activate inference-workbench

# Install dependencies
pip install -r requirements.txt
```

The environment must be activated (`conda activate inference-workbench`)
in any new terminal before running the app or the tests.

The Streamlit entry point and run command are added in a later phase, once
the app layer exists. See `NEXT_TASKS.md` for current status.

---

## License

MIT — see `LICENSE`.
