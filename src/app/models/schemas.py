from pydantic import BaseModel, Field


class SeriesPoint(BaseModel):
    date: str
    value: float


class ModelParams(BaseModel):
    sigma2_obs: float = Field(description="Estimated observation variance")
    sigma2_state: float = Field(description="Estimated state (level) variance")


class ForecastBand(BaseModel):
    dates: list[str]
    mean: list[float]
    lower: list[float]
    upper: list[float]


class SandboxAnalysisResponse(BaseModel):
    filename: str
    n_obs: int
    date_start: str
    date_end: str
    params: ModelParams
    log_likelihood: float
    aic: float
    observed: list[SeriesPoint]
    smoothed: list[SeriesPoint]
    forecast: ForecastBand


class ErrorResponse(BaseModel):
    detail: str
