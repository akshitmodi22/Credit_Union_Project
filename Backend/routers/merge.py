# ═══════════════════════════════════════════════════════════════
# routers/merge.py — Merge predictions endpoint
# ═══════════════════════════════════════════════════════════════

from fastapi import APIRouter, HTTPException
from utils.merger import build_master_csv, master_exists, get_merge_info

router = APIRouter()


@router.post("/merge-predictions")
def merge_predictions():
    """
    Merges latest attrition + loan + propensity CSVs
    into a single master CSV in COS.
    Call this after running all 3 predictions.
    """
    try:
        print("Starting merge...")
        tracker = build_master_csv()
        return {
            "status"          : "success",
            "message"         : "Master predictions CSV created successfully",
            "merged_at"       : tracker["merged_at"],
            "total_members"   : tracker["total_members"],
            "models_included" : tracker["models_included"],
            "cos_path"        : "predictions/master/master_predictions_latest.csv"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merge failed: {str(e)}")


@router.get("/merge-status")
def merge_status():
    """
    Check if master CSV exists and when it was last merged.
    """
    info = get_merge_info()
    if info:
        return {
            "status"        : "exists",
            "merged_at"     : info.get("merged_at"),
            "total_members" : info.get("total_members"),
            "models"        : info.get("models_included"),
        }
    return {
        "status"  : "not_merged",
        "message" : "No master CSV found. Run merge first."
    }
