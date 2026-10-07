from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.models.schemas import (
    ErrorResponse,
    ForecastBand,
    ModelParams,
    SandboxAnalysisResponse,
    SeriesPoint,
)
from app.services.data_loader import CSVValidationError, load_bbt_csv
from app.services.forecasting import analyze_bbt

router = APIRouter(prefix="/sandbox", tags=["sandbox"])

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
SAMPLE_CSV = Path(__file__).resolve().parents[3] / "data" / "bbt_sample.csv"


def _to_points(series) -> list[SeriesPoint]:
    return [
        SeriesPoint(date=index.strftime("%Y-%m-%d"), value=float(value))
        for index, value in series.items()
    ]


@router.post(
    "/upload",
    response_model=SandboxAnalysisResponse,
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def upload_bbt_csv(
    file: UploadFile = File(...),
    horizon: int = Form(7),
) -> SandboxAnalysisResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB).")

    try:
        df = load_bbt_csv(raw)
    except CSVValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        analysis = analyze_bbt(df, forecast_steps=horizon)
    except Exception as exc:  # noqa: BLE001 - report fitting failures to the client
        raise HTTPException(
            status_code=422, detail=f"Model fitting failed: {exc}"
        ) from exc

    return SandboxAnalysisResponse(
        filename=file.filename,
        n_obs=int(len(analysis.observed)),
        date_start=analysis.observed.index[0].strftime("%Y-%m-%d"),
        date_end=analysis.observed.index[-1].strftime("%Y-%m-%d"),
        params=ModelParams(
            sigma2_obs=analysis.sigma2_obs,
            sigma2_state=analysis.sigma2_state,
        ),
        log_likelihood=analysis.log_likelihood,
        aic=analysis.aic,
        observed=_to_points(analysis.observed),
        smoothed=_to_points(analysis.smoothed),
        forecast=ForecastBand(
            dates=[d.strftime("%Y-%m-%d") for d in analysis.forecast_mean.index],
            mean=[float(v) for v in analysis.forecast_mean],
            lower=[float(v) for v in analysis.forecast_lower],
            upper=[float(v) for v in analysis.forecast_upper],
        ),
    )


@router.get("/sample-csv", include_in_schema=False)
def download_sample_csv() -> FileResponse:
    if not SAMPLE_CSV.exists():
        raise HTTPException(status_code=404, detail="Sample CSV not available.")
    return FileResponse(
        SAMPLE_CSV,
        media_type="text/csv",
        filename="bbt_sample.csv",
    )
