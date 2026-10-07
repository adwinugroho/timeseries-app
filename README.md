### Folder Structure

timeseries-app/
├── src/
│   └── app/                  # Root package aplikasi
│       ├── __init__.py
│       ├── main.py           # Entry point FastAPI & konfigurasi app
│       │
│       ├── api/              # Routing / Endpoints (Interface layer)
│       │   ├── __init__.py
│       │   ├── v1/           # Versioning API (Best practice!)
│       │   │   ├── __init__.py
│       │   │   ├── routes/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── about.py      # GET /about
│       │   │   │   ├── projects.py   # GET /projects
│       │   │   │   ├── contact.py    # GET /contact
│       │   │   │   ├── blog.py    # GET /blog
│       │   │   │   └── blog-archive.py       # GET /blog-archive
│       │   │   ── endpoints.py      # Router aggregator v1
│       │   └── deps.py               # Dependency injection (DB, Auth, etc.)
│       │
│       ├── core/             # Konfigurasi & Core Logic
│       │   ├── __init__.py
│       │   ├── config.py     # Settings (env vars, pydantic-settings)
│       │   ├── security.py   # JWT, OAuth2, dll
│       │   └── logging.py    # Custom logger setup
│       │
│       ├── models/           # Data Models & Schemas
│       │   ├── __init__.py
│       │   ├── db.py         # SQLAlchemy/Base declarative
│       │   └── schemas.py    # Pydantic models (Request/Response)
│       │
│       ├── services/         # Business Logic Layer (PENTING!)
│       │   ├── __init__.py
│       │   ├── forecasting.py# Logic ARIMA/Prophet/LSTM
│       │   ├── data_loader.py# Load CSV/DB processing
│       │   └── anomaly_detection.py
│       │
│       ├── repositories/     # Data Access Layer (Opsional tapi Senior-level)
│       │   ├── __init__.py
│       │   └── timeseries_repo.py  # Query DB khusus time-series
│       │
│       ├── data/     # static json for url blog 
│       │   ├──blog-archive.json 
│       │
        ── utils/            # Helper functions murni
│           ├── __init__.py
│           └── validators.py
│
├── tests/                    # Test suite (Mirror struktur src/app)
│   ├── __init__.py
│   ├── conftest.py           # Fixtures pytest
│   ├── test_api/
│   │   └── test_about.py
│   └── test_services/
│       └── test_forecasting.py
│
├── notebooks/                # Eksperimen R/Python (JANGAN masuk production code)
│   └── eda_timeseries.ipynb
│
├── docker/                   # Docker config terpisah
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
