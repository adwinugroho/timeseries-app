import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.v1.endpoints import router as api_v1_router

app = FastAPI()
app.include_router(api_v1_router)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
DATA_FILE = BASE_DIR / "data" / "blog-archive.json"


@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    blog_items = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            blog_items = json.load(f)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "site_title": "Timeseries Lab — Biomedical & Healthcare Informatics",
            "blog_items": blog_items,
            "projects": [
                {
                    "title": "FertilityShift: BBT Ovulation & Thermal Shift Detection",
                    "dataset": "Sympto-Thermal Daily Logs / Pandas Time-Series",
                    "metrics": ["3-over-6 Rule", "Rolling Baseline Analysis"],
                    "description": "Automated time-series pipeline designed to parse daily basal body temperature records, smooth physiological noise, and reliably identify post-ovulatory thermal shifts for menstrual cycle tracking.",
                    "highlights": [
                        "6-day rolling baseline and coverline thresholding",
                        "Consecutive thermal shift verification to confirm ovulation",
                        "Clinical telemetry visualization with Matplotlib",
                    ],
                    "tags": ["Python", "Pandas", "NumPy", "SciPy"],
                    "github_url": "https://github.com",
                },
                {
                    "title": "CardioPulse: Arrhythmia Early Detection via Multi-lead ECG Transformer",
                    "dataset": "PTB-XL / PhysioNet",
                    "metrics": ["AUC 0.984", "500 Hz Multi-Lead"],
                    "description": "Temporal self-attention architectures designed to isolate premature ventricular contractions (PVCs) and paroxysmal atrial fibrillation across asynchronous 12-lead vectors with calibrated confidence intervals.",
                    "highlights": [
                        "Self-attention weight visualization over QRS-T morphology",
                        "Bandpass 0.5–45 Hz Butterworth IIR digital filtering",
                        "Sub-15ms inference latency per 10-second cardiac frame",
                    ],
                    "tags": ["PyTorch", "SciPy", "FastAPI"],
                    "github_url": "https://github.com",
                },
            ],
            "researcher": {
                "name": "Adwin Nugroho",
                "role": "Backend Engineer & Healthcare Enthusiast",
                "email": "adwinnugroho16@gmail.com",
                "bio": "Backend engineer with a keen passion for healthcare technology and sequential data. Archiving past academic data science research and reproducible time-series pipelines.",
            },
        },
    )


@app.get("/blog-archive", response_class=HTMLResponse)
def read_blog_archive(request: Request):
    monographs = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            monographs = json.load(f)

    return templates.TemplateResponse(
        request=request,
        name="blog-archive.html",
        context={
            "page_title": "Blog Archive — Timeseries Lab",
            "monographs": monographs,
            "total_count": len(monographs),
        },
    )
