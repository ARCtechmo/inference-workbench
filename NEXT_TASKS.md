# inference-workbench — Next Tasks

*Just the immediate next session's work. Completed tasks are removed, not
archived — history lives in git and in ARCHITECTURE.md §11.*

*Last updated: 2026-05-30.*

---

## v1 scope reminder

Binomial logistic regression, end to end. One model family, real
reasoning depth, the full workflow scaffolding.

## Done so far

`data_io/` (CSV loader + metadata + load-error handling) and `profile/`
(seven Level-2 checks + orchestrator, 29 tests passing) are built,
tested, committed, and pushed. Environment and README setup complete.
See ARCHITECTURE.md §11 for the as-built contracts.

---

## Next session — workflow state and step engine (`workflow/`)

- [ ] Define the workflow state schema (uploaded data, classifications,
      current step, completed steps, overrides)
- [ ] Implement state persistence within a Streamlit session via
      `st.session_state`
- [ ] Implement step gating logic (cannot advance until prior step is
      complete)
- [ ] Implement variable classification interaction (Type and Role
      proposals, user confirmation) — consumes `profile/` structural type
      proposals; this is where ordinal/nominal and role get pinned down
- [ ] Implement model-family routing logic (for v1: routes binary
      outcomes to `logistic_regression/`)

### Open design questions to settle first

- The state schema is the load-bearing decision (everything consumes it)
  — settle its shape before writing code, same as we did for `data_io`
  and `profile`.
- Step 4 of the 9-step workflow may need an explicit branch on **outcome
  structure** before model-family selection. Decide whether that belongs
  in the workflow's routing logic or earlier.
