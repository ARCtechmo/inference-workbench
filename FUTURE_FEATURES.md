# inference-workbench — Future Features

*The parking lot. Everything that is not in v1 lives here.
A feature on this list is not denied — it is deferred with reasoning.
Items move from here to `NEXT_TASKS.md` only when a v1+ phase is opened
and they are explicitly scoped in.*

---

## Model families beyond binomial logistic

v1 ships binomial logistic regression only. The deferred families,
each one a future subdirectory under `models/`:

- **`models/ols/`** — ordinary least squares regression. Continuous
  outcomes. The McNulty graduate-salaries exercise is the natural seed.
- **`models/poisson/`** — Poisson and related count-outcome regression
  (Poisson, negative binomial, zero-inflated variants). Count outcomes
  (events per unit time or exposure).
- **`models/ordinal_logistic/`** — proportional-odds ordinal logistic.
  Ordinal outcomes. The McNulty employee-performance exercise seed.
- **`models/cox_ph/`** — Cox proportional hazards survival model.
  Time-to-event outcomes. The McNulty promotion-timing exercise seed.
- **`models/multilevel/`** — hierarchical / multilevel logistic and
  linear. Nested data structures. The McNulty learning-programs
  exercise seed.
- **`models/bayesian/`** — Bayesian inference. A separate track from
  the regression families above; covers priors, likelihoods,
  posteriors, MCMC.

Each family follows the same module contract as logistic regression:
`fit()`, `diagnose()`, `interpret()`, with family-specific assumption
checks living inside the family module.

**Trigger to start:** v1 ships and is observed in real use; the
logistic-regression family's contract is stable enough to template
from.

---

## Broader hypothesis test infrastructure

The diagnostics layer at v1 includes the tests needed to support
logistic regression workflows (chi-square, VIF, LRT). The broader test
infrastructure that nests into other workflows is deferred:

- **t-tests** (one-sample, two-sample, paired)
- **One-way and multi-way ANOVA**
- **Kruskal-Wallis and Dunn's post-hoc with Bonferroni**
- **Shapiro-Wilk, Levene, Breusch-Pagan** for assumption screening
- **Log-rank test** (paired with the future Cox PH family)
- **Standalone hypothesis-testing workflow** for analyses that do not
  require a regression destination

**Trigger to start:** when a model family that uses one of these tests
is being implemented.

---

## LLM integration

Deferred from v1 with reasoning in `ARCHITECTURE.md` §5. The eventual
shape:

- Per-step grounded LLM calls invoked with the workflow state, model
  output, and diagnostic results as structured input.
- Structured outputs — natural-language interpretation, advisory
  pushback, conclusion drafting — never free-form chat.
- Provider abstraction so the backend can be swapped.
- API-based with explicit API key requirement documented.
- LLM contributes interpretation *on top of* computed results; never
  replaces them.

**Trigger to revisit:** v1 ships and the procedural advisory layer is
observed in real use. The LLM extension becomes a v2 candidate at that
point.

---

## Higher levels of data handling

v1 implements Level 2 (profile and surface, do not fix). Higher levels
are deferred:

- **Level 3 — guided cleaning.** The app surfaces issues and offers
  remediation options (impute, drop, encode); the analyst picks; the
  app applies the chosen transformation and records the decision in
  the report.
- **Level 4 — automated cleaning with audit.** The app applies sensible
  defaults on upload and shows the analyst what was done. The analyst
  can override. Fast but high-risk; only appropriate for specific
  well-scoped operations.

**Trigger to start:** when a specific cleaning operation is needed
often enough that surfacing-only feels like artificial friction. The
candidate operations to consider first: missing-value imputation
strategies, type coercion, encoding of categorical variables.

---

## Cross-session persistence

v1 holds the analysis state only within a Streamlit session. Refreshing
the browser loses the analysis. Deferred:

- **Save analysis to disk.** Export the workflow state as a serialized
  artifact (JSON or pickle); reload to resume.
- **Named analyses.** Maintain a library of past analyses with metadata
  (date, data file, model family, conclusion summary).
- **Cross-session diffing.** Compare two runs of the same workflow on
  different data or with different overrides.

**Trigger to start:** when the typical analysis session begins to
exceed a single sitting and resumption becomes a recurring need.

---

## Database-backed data sources

v1 reads CSV from local disk. Deferred:

- **Parquet and Excel readers** as common analyst formats.
- **SQL database connectors** (Postgres, SQLite, etc.) for analysts
  whose data lives in databases.
- **Cloud storage** (S3, GCS) for distributed data.

The `data_io/` seam is designed to make this swap clean — the rest of
the system reads typed DataFrames and is indifferent to source.

**Trigger to start:** when a real use case demands a non-CSV source.

---

## Domain modules beyond people-analytics

v1 uses people-analytics worked examples as the seed for documentation
and case material. Other domains are deferred:

- **Science** — biological, physical, social science worked examples.
- **Economics** — econometric specifications, instrumental variables,
  difference-in-differences (the last requires causal-inference
  infrastructure).
- **Causal inference layer** — DAG-based reasoning, identification
  assumptions, confounding analysis. This is a substantial expansion;
  the McNulty book touches it but does not exhaust it.

**Trigger to start:** when v1 is stable and personal interest pulls
toward a specific domain.

---

## Deployment beyond local development

v1 runs locally via `streamlit run`. Deferred:

- **Self-hosted deployment** to a VPS for personal remote access.
- **Public-facing deployment** with authentication (if ever desired).
- **Docker packaging** for reproducible deployment.

**Trigger to start:** when remote access to the app becomes a recurring
need.

---

## UI framework migration

v1 uses Streamlit. The decision is documented in `ARCHITECTURE.md` §4
with an explicit exit condition: if Streamlit's layout and state
constraints become binding, presentation can be swapped across the
`app/` seam.

The migration candidates if this happens:

- **Dash** — more powerful state and callbacks; heavier code.
- **Flask + frontend** — full custom UI; significant engineering
  investment.
- **Other Python interactive frameworks** as the landscape evolves.

**Trigger to start:** when a specific UI requirement cannot be met by
Streamlit and the workaround cost exceeds the migration cost.

---

## Reproducible-research extras

Quality-of-life features for analysts who want to share or version
their analyses:

- **Embedded data snapshot** in the report (so the report is fully
  self-contained).
- **Reproducibility manifest** — Python version, library versions,
  random seeds — embedded in the report.
- **Citation generator** for the methods used.
- **Diff view** between two versions of the same analysis.

**Trigger to start:** when the analyses being produced need to be
shared or audited beyond personal use.

---

## Testing and CI infrastructure

v1 will have unit tests for the procedural layers (profile,
diagnostics, models, advise). Deferred:

- **Integration tests** running the full workflow on canonical
  datasets.
- **CI pipeline** (GitHub Actions) running tests on every push.
- **Coverage reporting.**
- **Property-based testing** for the diagnostic functions.

**Trigger to start:** when the codebase is large enough that
regressions are a real risk, or when contributors join the project.

---

## Notes

- Items on this list are not promises. They are reasoned deferrals.
- An item moves from here to `NEXT_TASKS.md` only when a future phase
  is opened and the item is explicitly scoped in.
- New items can be added freely. The discipline is *not* in keeping
  the list short, but in keeping items off `NEXT_TASKS.md` until they
  are genuinely scoped.
