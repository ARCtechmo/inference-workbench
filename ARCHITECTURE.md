# inference-workbench — Architecture

*The locked decision record. Each decision is stated with rationale.
Decisions are durable; they retire only if the underlying problem shifts.*

---

## 1. Design notes — what the project is and why

### 1.1 The one-sentence brief

**`inference-workbench` is a stateful, advisory reasoning environment for
inferential statistics.**

Not a calculator. Not a tutor. Not a decision engine. Not a data-cleaning
tool. The reasoning lives in a procedural advisory layer; the analyst
stays in the driver's seat.

### 1.2 What the project demonstrates

The project encodes statistical *judgment*, not just statistical
*methods*. Calculators are commodity infrastructure. What is harder, and
what justifies this project's existence, is the procedural reasoning
around the calculation: when an assumption violation reroutes the
analysis, when an unadjusted finding gets overturned by an adjusted one,
when a coefficient should be qualified rather than asserted.

This is the value an analyst would otherwise carry in their head and lose
under deadline pressure. The app holds it as state.

### 1.3 Audience — analyst-first

The design center is the working analyst with baseline statistical
literacy. Learners and weaker practitioners are a bonus audience, not the
design target. This is load-bearing: it is why the app can be terse, skip
remedial explanations, and push back directly rather than hedge.

A reviewer who is not an analyst is also a real audience for this repo
as a portfolio artifact. The docs (this file, README) carry that load;
the app itself is designed for the user, not the reviewer.

### 1.4 What v1 is

**v1 ships binomial logistic regression, end to end.** Other regression
families and broader test infrastructure are tracked in
`FUTURE_FEATURES.md`. v1 scope is deliberately narrow — one family done
with real reasoning depth is a stronger artifact than five families done
shallowly.

### 1.5 Cross-cutting principles

Earned during design, generalize beyond any specific decision:

- **The app errs toward pushback, not silence.** A wrong nudge costs the
  analyst two seconds; a silent omission can corrupt a conclusion.
- **Computed facts beat generated claims.** Anything reportable that can
  be computed must be computed, not LLM-generated. Generated content is
  reserved for interpretation on top of computed results — and not in
  v1.
- **The workflow knows about model families; model families do not know
  about workflows.** One-way knowledge. Adding a new family is a
  contained operation: a new module under `models/`, a new branch in the
  workflow's routing logic, nothing else.
- **Surface, do not fix.** Data issues are surfaced for analyst decision.
  Imputing or transforming silently is forbidden. (See §6 on data
  handling.)
- **Honest scope is a feature.** Deferrals are stated, not hidden. v1
  scope is narrow on purpose; future features are parked, not denied.

---

## 2. Three-layer mental model

Three conceptual layers with one-way imports:

```
app  ->  workflow  ->  models      ->  diagnostics  ->  data_io
                    ->  profile    ->  advise        ->  report
```

- **`app/`** — Streamlit presentation. Knows the workflow; does not know
  model internals or how data is read.
- **`workflow/`** — the state machine, step sequencing, gating logic, and
  model-family routing. The "smart" layer. Knows about models, profile,
  diagnostics, and advise; does not know about app rendering.
- **`models/`, `profile/`, `diagnostics/`, `advise/`, `report/`** — the
  procedural workers. Each has a contract; none reach across to peers.
- **`data_io/`** — the only code that reads or writes data files. A
  future database swap touches this layer only.

## SEAM RULE

`data_io/` is the only module that names a data path or opens a data
file. A file read anywhere else is an architecture violation.

This mirrors the seam discipline established in the `fanfav-ui` repo.
The same principle, the same enforcement.

---

## 3. Module contracts

### 3.1 `data_io/`

Reads user-uploaded data files (CSV at v1; Parquet, Excel, and database
sources at v2). Returns typed pandas DataFrames. Does not transform or
clean. The sole layer that knows where data physically lives.

### 3.2 `profile/`

Level 2 data profiling. Inspects an uploaded DataFrame and reports:
missingness by column, dtype mismatches, near-constant variables,
high-cardinality categoricals, suspicious distributions, likely outliers.
Returns a structured profile object. Does not fix issues.

### 3.3 `workflow/`

The state machine. Holds the analysis state (uploaded data, variable
classifications, current step, completed steps, recorded overrides).
Sequences the 9-step workflow. Gates steps based on prior completion.
Routes to model families based on variable classification.

The workflow imports from `models/`, `diagnostics/`, `profile/`, and
`advise/`. None of those import from `workflow/`.

### 3.4 `models/`

One subdirectory per regression family. Each family is internally
self-contained:

- `models/logistic_regression/` — v1
- `models/ols/`, `models/ordinal_logistic/`, `models/cox_ph/`,
  `models/multilevel/`, `models/bayesian/` — v2 and beyond

Each family module exposes a standard contract: `fit()`, `diagnose()`,
`interpret()`. The workflow calls the contract; the family knows nothing
about the workflow that called it.

Each family may also house *family-specific* diagnostic checks that are
not meaningful for other families — proportional odds for ordinal
logistic, proportional hazards for Cox, linearity of the logit for
logistic regression. The family's `diagnose()` orchestrates both the
shared diagnostics from `diagnostics/` (multicollinearity, residual
checks, etc.) and its own family-specific checks.

### 3.5 `diagnostics/`

Cross-family assumption checks and evidence tests that are usable across
more than one model family: chi-square, Levene, Shapiro-Wilk,
Breusch-Pagan, VIF, likelihood-ratio tests, log-rank, Kruskal-Wallis,
Dunn's post-hoc, etc.

Each test exposes a consistent contract: input data and parameters,
output a structured result (statistic, p-value, pass/fail, interpretation
hint).

Tests are *not* model families. They serve two roles in the workflow:

- **Evidence checks** — nested into workflows as screening or
  confirmatory steps (chi-square as a fairness pre-screen; LRT to
  compare nested models). Never destinations.
- **Shared assumption checks** — called by model families via their
  `diagnose()` orchestration.

Family-specific assumption checks (proportional odds, proportional
hazards, etc.) live inside the relevant `models/<family>/` module, not
here. The principle: `diagnostics/` holds what is shared; `models/<family>/`
holds what is specific.

### 3.6 `advise/`

Procedural pushback rules. Given the workflow state, the diagnostic
results, and the chosen model, what alternatives or caveats should the
app surface? Rules are deterministic: if proportional hazards is
violated, the hazard-ratio interpretation is qualified; if normality
fails for an OLS residual, Kruskal-Wallis is suggested.

Pushback content is computed from rules, not generated by an LLM. No LLM
in v1.

### 3.7 `report/`

Reproducible report export. Given the completed workflow state, produces
a single exportable artifact (HTML or PDF; format choice deferred to
implementation) capturing: the question, the data profile, the variable
classifications, the diagnostic results, the model output, the flagged
caveats, and the conclusion.

### 3.8 `app/`

Streamlit UI. Renders the workflow state, captures user input, displays
diagnostic results and pushback. Does not contain analysis logic.

---

## 4. Framework — Streamlit

**T1. Streamlit for the v1 UI.**

Streamlit is Python-native, declarative, state-aware via `session_state`,
and matches the application shape: structured forms and tabular/plot
output, not bespoke pixel-precise layouts. Other Python-interactive
options (Gradio, Dash, Shiny for Python, Flask + frontend) were
considered.

Flask was rejected for v1: it is a web framework, not a UI framework.
Using it would mean building all the UI affordances (forms, state,
display) from scratch in HTML and JavaScript before any analysis logic
could be written. The cost-benefit at v1 scope does not justify it.

The migration path is real but deferred: if v2 or v3 outgrows
Streamlit's layout and state constraints, presentation can be swapped
across the `app/` seam. The workflow, models, diagnostics, advise, and
report modules are framework-agnostic.

---

## 5. LLM integration — deferred to v2

**T2. No LLM in v1.**

LLM integration was considered and deferred. Reasons:

- Adds real complexity (API key handling, prompt design, structured
  output, failure modes, cost) for value that is not core to v1's
  reasoning differentiator.
- The procedural advisory layer is the core differentiator and stands
  without LLM assistance. Computed pushback rules driven by diagnostic
  results deliver the "co-worker checking your work" promise on their
  own.

Trigger to revisit: when v1 is shipped and the procedural advisory layer
is observed in real use, LLM integration becomes a candidate for v2 as
an *interpretation layer on top of* (never replacing) computed results.

---

## 6. Data handling — Level 2

**T3. Level 2 data handling: profile and surface, do not fix.**

The app inspects uploaded data and reports issues. It does not impute
missing values, coerce types, drop outliers, or transform variables
without explicit analyst direction.

The reasoning: cleaning decisions are high-judgment decisions disguised
as mechanical ones. Whether to impute a missing variable depends on
*why* it is missing, what role it plays in the analysis, and what the
analytical question is. An app that imputes silently is doing analysis
the analyst did not authorize.

Level 1 (clean data required) was rejected as too restrictive.
Level 3 and Level 4 (guided cleaning, automated cleaning with audit) are
deferred — they may be appropriate for specific, well-scoped operations
in a future version, but not at v1.

The honest contract surfaced to users: *the app reasons about the
analysis, not about the data. Bring data that is mostly clean; the app
will tell you if it is not.*

---

## 7. Domain posture — domain-general core, people-analytics seed

**T4. Domain-general reasoning core; people-analytics as the seed module
for examples and templates.**

The reasoning patterns (workflow, diagnostics, advisory rules,
unadjusted-vs-adjusted comparison) are domain-independent. Worked
examples drawn from McNulty's *Handbook of Regression Modeling in People
Analytics* seed the documentation and any future case-study material,
because those examples are at hand. Science and economics domains are
deferred parking-lot items.

---

## 8. Module structure

Eight modules at v1, all created as empty packages with placeholder
`README.md` files:

```
inference-workbench/
├── app/
├── workflow/
├── models/
│   └── logistic_regression/    (v1 implementation; v2+ adds siblings)
├── diagnostics/
├── profile/
├── advise/
├── report/
├── data_io/
├── README.md
├── ARCHITECTURE.md             (this file)
├── NEXT_TASKS.md
├── FUTURE_FEATURES.md
├── REPO_SETUP_PROCEDURE.md     (personal, generic)
├── SECURE_GIT_WORKFLOW.md      (personal, generic)
├── LICENSE
└── .gitignore
```

---

## 9. What is deferred to v2 and beyond

Captured for reference here; the working list lives in
`FUTURE_FEATURES.md`:

- Model families beyond binomial logistic regression
- LLM integration as an interpretation layer
- Higher levels of data handling (Level 3+)
- Domain modules beyond people-analytics seed examples
- Database-backed data sources
- Cross-session persistence (analysis save/resume)
- Deployment beyond local development
- UI framework migration (only if Streamlit's constraints bind)

---

## 10. Related documents

- `README.md` — the project's front door, written for both users and
  reviewers
- `NEXT_TASKS.md` — the working task list for v1
- `FUTURE_FEATURES.md` — the parking lot
- `REPO_SETUP_PROCEDURE.md`, `SECURE_GIT_WORKFLOW.md` — personal,
  generic procedure docs; not specific to this project
