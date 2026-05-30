# inference-workbench — Next Tasks

*Short-horizon working task list for v1. Items get completed and removed,
not archived. Anything beyond v1 belongs in `FUTURE_FEATURES.md`.*

*Last updated: 2026-05-30.*

---

## v1 scope reminder

Binomial logistic regression, end to end. One model family, real
reasoning depth, the full workflow scaffolding. Other families and
infrastructure are deferred — see `FUTURE_FEATURES.md`.

---

## Phase 1 — Scaffolding complete

- [x] Create local project directory
- [x] Initialize git, connect to GitHub
- [x] Generate fine-grained token, encrypt with gpg
- [x] Scaffold eight module directories with `__init__.py` and placeholder
      `README.md` files
- [x] Commit and push module scaffold
- [x] Write `REPO_SETUP_PROCEDURE.md` and `SECURE_GIT_WORKFLOW.md`
- [x] Write `README.md`
- [x] Write `ARCHITECTURE.md`
- [x] Write `NEXT_TASKS.md` (this file)
- [ ] Write `FUTURE_FEATURES.md`

---

## Phase 2 — Environment and dependencies

- [ ] Create `requirements.txt` with minimum v1 dependencies
      (streamlit, pandas, numpy, scipy, statsmodels, matplotlib)
- [ ] Create `pyproject.toml` or stick with `requirements.txt`
      (decision pending)
- [ ] Set up a virtual environment for development
- [ ] Document the setup procedure in `README.md` under "Setup and run"

## Phase 3 — Data layer (`data_io/`)

- [ ] Define the data-loading contract: input (file path or upload),
      output (typed pandas DataFrame with schema metadata)
- [ ] Implement CSV reader as v1 default
- [ ] Add basic validation (file exists, readable, parseable)
- [ ] Stub for Parquet and Excel readers as future-proofing (deferred,
      not implemented)

## Phase 4 — Profile layer (`profile/`)

- [ ] Define the profile result schema (what `profile()` returns)
- [ ] Implement missingness reporting per column
- [ ] Implement dtype inspection and proposed reclassification
- [ ] Implement constant / near-constant variable detection
- [ ] Implement high-cardinality categorical detection
- [ ] Implement outlier flagging (IQR-based at v1, deferred more
      sophisticated methods)
- [ ] Unit tests for each profile function

## Phase 5 — Workflow state and step engine (`workflow/`)

- [ ] Define the workflow state schema (uploaded data, classifications,
      current step, completed steps, overrides)
- [ ] Implement state persistence within a Streamlit session via
      `st.session_state`
- [ ] Implement step gating logic (cannot advance until prior step is
      complete)
- [ ] Implement variable classification interaction (Type and Role
      proposals, user confirmation)
- [ ] Implement model-family routing logic (for v1: routes binary outcomes
      to `logistic_regression/`)

## Phase 6 — Diagnostics layer (`diagnostics/`)

- [ ] Define the diagnostic result schema (statistic, p-value, pass/fail,
      interpretation hint)
- [ ] Implement chi-square test of independence
- [ ] Implement VIF computation
- [ ] Implement likelihood-ratio test for nested model comparison
- [ ] Unit tests for each diagnostic function

## Phase 7 — Logistic regression family (`models/logistic_regression/`)

- [ ] Create the subdirectory
- [ ] Implement `fit()` (statsmodels-backed binomial logistic)
- [ ] Implement family-specific assumption checks (linearity of the
      logit, separation detection, influential observations)
- [ ] Implement `diagnose()` orchestration (calls shared diagnostics
      and family-specific checks)
- [ ] Implement `interpret()` (coefficient interpretation with odds
      ratios, adjusted vs unadjusted distinction)
- [ ] Unit tests

## Phase 8 — Advisory layer (`advise/`)

- [ ] Define the pushback rule schema
- [ ] Implement rules for logistic-specific scenarios:
      - separation detected → suggest penalized regression
      - high VIF → suggest variable reduction or interpretation caveat
      - significant unadjusted finding overturned by adjusted →
        surface as central finding
      - LRT favors reduced model → flag predictor as non-significant
- [ ] Wire pushback rules into the workflow state

## Phase 9 — Report export (`report/`)

- [ ] Decide output format (HTML preferred for portability; PDF if
      reviewer-facing)
- [ ] Define the report schema (sections, structure)
- [ ] Implement report generation from completed workflow state
- [ ] Include: question, profile, classifications, diagnostics, model
      output, pushback caveats, conclusion

## Phase 10 — Streamlit app (`app/`)

- [ ] Sketch the screen flow on paper before implementing
- [ ] Implement file upload screen
- [ ] Implement variable classification screen with proposed-classification
      confirmation
- [ ] Implement profile display screen
- [ ] Implement workflow step navigation
- [ ] Implement diagnostic results display
- [ ] Implement model results display with pushback panel
- [ ] Implement report export button

## Phase 11 — End-to-end test

- [ ] Run the app against the recruiting process notebook data from the
      original exercises
- [ ] Verify the app reaches the same substantive conclusions as the
      hand-written notebook
- [ ] Verify the pushback surfaces in expected places (e.g., gender
      effect attenuates after adjustment)
- [ ] Document any gaps or unexpected behavior

## Phase 12 — Documentation finalization

- [ ] Update `README.md` "Setup and run" with concrete steps
- [ ] Add a short demo section (screenshot or transcript) to `README.md`
- [ ] Review and refine `ARCHITECTURE.md` against the implemented system
- [ ] Verify all cross-references between docs are accurate
- [ ] Tag v1.0.0 release

---

## Notes

- Phases are *roughly* sequential but not strictly. Phase 4 (profile)
  and Phase 6 (diagnostics) can proceed in parallel. Phase 10 (Streamlit
  app) depends on Phases 3–9 having stable contracts but can be
  scaffolded earlier with stub data.
- Each phase should produce committable work. No phase is "done" until
  the relevant tests pass and the relevant docs are updated.
- The v1 success criterion is Phase 11 passing on real data, not a
  feature count.
