from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.services.bbt_model import BBTStateSpaceModel

DEFAULT_FORECAST_STEPS = 7
MAX_FORECAST_STEPS = 60


@dataclass
class BBTAnalysis:
    observed: pd.Series
    smoothed: pd.Series
    sigma2_obs: float
    sigma2_state: float
    log_likelihood: float
    aic: float
    forecast_mean: pd.Series
    forecast_lower: pd.Series
    forecast_upper: pd.Series


def analyze_bbt(
    df: pd.DataFrame, forecast_steps: int = DEFAULT_FORECAST_STEPS
) -> BBTAnalysis:
    """Fit the local-level BBT state-space model and return smoothed + forecast series."""
    steps = max(1, min(int(forecast_steps), MAX_FORECAST_STEPS))
    series = df["temperature"].astype(float)

    model = BBTStateSpaceModel(series.to_numpy())
    results = model.fit(disp=False)

    smoothed = pd.Series(
        np.asarray(results.smoothed_state[0]), index=series.index, name="temperature"
    )

    forecast = results.get_forecast(steps=steps)
    forecast_index = pd.date_range(
        start=series.index[-1] + pd.Timedelta(days=1),
        periods=steps,
        freq="D",
    )
    mean = pd.Series(np.asarray(forecast.predicted_mean), index=forecast_index)
    interval = np.asarray(forecast.conf_int())
    lower = pd.Series(interval[:, 0], index=forecast_index)
    upper = pd.Series(interval[:, 1], index=forecast_index)

    params = np.asarray(results.params)
    return BBTAnalysis(
        observed=series,
        smoothed=smoothed,
        sigma2_obs=float(params[0]),
        sigma2_state=float(params[1]),
        log_likelihood=float(results.llf),
        aic=float(results.aic),
        forecast_mean=mean,
        forecast_lower=lower,
        forecast_upper=upper,
    )
