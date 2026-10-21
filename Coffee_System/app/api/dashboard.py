from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, RedirectResponse


router = APIRouter(
    tags=["Dashboard"]
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

FRONTEND_DIR = PROJECT_ROOT / "frontend"

DASHBOARD_FILE = FRONTEND_DIR / "dashboard.html"


@router.get(
    "/",
    include_in_schema=False
)
def redirect_to_dashboard():
    return RedirectResponse(
        url="/dashboard",
        status_code=307
    )


@router.get(
    "/dashboard",
    include_in_schema=False
)
def get_dashboard():
    if not DASHBOARD_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Το αρχείο του Dashboard δεν βρέθηκε. "
                f"Αναμενόμενη διαδρομή: {DASHBOARD_FILE}"
            )
        )

    return FileResponse(
        path=DASHBOARD_FILE,
        media_type="text/html"
    )


@router.get(
    "/health",
    tags=["System"]
)
def health_check():
    return {
        "status": "online",
        "service": "Voice Order System"
    }