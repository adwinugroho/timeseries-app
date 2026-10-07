# Fix `BBTStateSpaceModel.update` override warning

## Goal
Silence the "Method \"update\" overrides class \"MLEModel\" in an incompatible manner"
diagnostic in `src/app/services/bbt_model.py` without changing model behavior.

## Root cause (verified)
- Base method `statsmodels/tsa/statespace/mlemodel.py:2060` is:
  ```python
  def update(self, params, transformed=True, includes_fixed=False, complex_step=False):
      return self.handle_params(
          params=params, transformed=transformed, includes_fixed=includes_fixed
      )
  ```
  It returns the (possibly transformed) params array (`mlemodel.py:2092`, `handle_params` at `2025-2058`).
- The current override in `bbt_model.py:39-51` has the **correct signature** but no `return`,
  so its inferred return type is `None`, which is incompatible with the base `ndarray` return.
  This is what raises `reportIncompatibleMethodOverride`.
- Runtime already works (aider run returned `[1.42650353 0.01927445]`); statsmodels ignores the
  return value of internal `self.update(...)` calls. The fix is type-contract only.

## Change
File: `src/app/services/bbt_model.py`

Append `return params` at the end of `update` so the override honors the parent contract:

```python
    def update(self, params, transformed=True, includes_fixed=False, complex_step=False):
        params = super().update(
            params,
            transformed=transformed,
            includes_fixed=includes_fixed,
            complex_step=complex_step,
        )

        # Observation variance
        self.ssm["obs_cov", 0, 0] = params[0]

        # State variance
        self.ssm["state_cov", 0, 0] = params[1]

        return params
```

Do NOT fall back to `def update(self, params, **kwargs)` — that was the earlier cause of the
signature-mismatch warning. Keep the explicit parameters.

## Out of scope
- `transform_params` / `untransform_params` and matrix setup are already consistent with the base
  API; no change needed.
- Refactoring the model math (e.g. switching square/sqrt to log/exp, adding exog, etc.).

## Validation
1. Static: reopen the file in Pylance/Mypy — the override diagnostic on `update` should disappear.
   If no CLI type-checker is configured, confirm the squiggle is gone in the editor.
2. Runtime smoke test:
   ```bash
   uv run python -c "import numpy as np; from src.app.services.bbt_model import BBTStateSpaceModel; m = BBTStateSpaceModel(np.random.randn(50)); print(m.fit().params)"
   ```
   Expect the two fitted variances to print as before (values will differ from the earlier run
   due to random input), with no new warnings/errors.

## Risk
Minimal. Returning `params` matches the documented parent contract and is a no-op for all internal
statsmodels callers, which discard the return value.
