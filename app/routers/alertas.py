import json
from fastapi import APIRouter

router = APIRouter(prefix="/api/alertas", tags=["Alertas"])

@router.get("/inconsistencias")
def get_inconsistencias():
    """Reads processing_report.json and returns log of issues."""
    try:
        with open("processing_report.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
