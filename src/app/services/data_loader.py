import io

import pandas as pd

REQUIRED_COLUMNS = ("date", "temperature")
MAX_ROWS = 5000
MIN_OBS = 10


class CSVValidationError(ValueError):
    """Raised when an uploaded CSV cannot be used for BBT analysis."""


def load_bbt_csv(raw: bytes) -> pd.DataFrame:
    """Parse and validate a ``date,temperature`` CSV into a daily indexed frame.

    The returned frame has a :class:`pandas.DatetimeIndex` named ``date`` and a
    single float column ``temperature``. Gaps in the calendar are linearly
    interpolated so the state-space time index is evenly spaced.
    """
    if not raw or not raw.strip():
        raise CSVValidationError("Uploaded file is empty.")

    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as exc:  # noqa: BLE001 - surface any parser error to the client
        raise CSVValidationError(f"Could not parse CSV: {exc}") from exc

    df.columns = [str(col).strip().lower() for col in df.columns]
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise CSVValidationError(
            "CSV must contain columns 'date,temperature'. "
            f"Missing: {', '.join(missing)}."
        )

    df = df[list(REQUIRED_COLUMNS)].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df = df.dropna(subset=["date", "temperature"])

    if df.empty:
        raise CSVValidationError("No rows with a valid date and numeric temperature.")
    if len(df) > MAX_ROWS:
        raise CSVValidationError(f"Too many rows (limit is {MAX_ROWS}).")

    df = df.sort_values("date").drop_duplicates(subset="date", keep="last")
    df = df.set_index("date")

    daily_index = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(daily_index)
    df["temperature"] = df["temperature"].interpolate(
        method="linear", limit_direction="both"
    )
    df = df.dropna(subset=["temperature"])
    df.index.name = "date"

    if len(df) < MIN_OBS:
        raise CSVValidationError(
            f"Need at least {MIN_OBS} daily observations to fit the model."
        )
    if float(df["temperature"].std()) == 0.0:
        raise CSVValidationError("Temperature series is constant; nothing to model.")

    return df
