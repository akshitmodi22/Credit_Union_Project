# ═══════════════════════════════════════════════════════════════
# routers/health.py — Health check endpoints
# ═══════════════════════════════════════════════════════════════

from fastapi import APIRouter
from datetime import date

from cos_client import read_json
from config import TRACKER_KEYS, PRED_TRACKER_KEYS, AUC_HEALTHY_THRESHOLD

router = APIRouter()


@router.get("/health")
def health():
    """Basic service health check."""
    return {
        "status"  : "ok",
        "service" : "credit-union-skill",
        "version" : "1.0.0"
    }


@router.get("/model-health")
def model_health():
    """
    Returns version, AUC, health status, last trained,
    and last predicted for all models.
    Reads both version tracker (training) and prediction tracker.
    """
    health_info = {}

    for model in ["attrition", "loan", "propensity"]:
        info = {}

        # ── Read version tracker (training info) ───────────────
        try:
            tracker = read_json(TRACKER_KEYS[model])
            latest  = tracker["versions"][-1]
            info["version"]    = latest["version"]
            info["trained_on"] = latest["trained_on"]
            info["auc"]        = latest["auc"]
            info["status"]     = (
                "healthy" if latest["auc"] >= AUC_HEALTHY_THRESHOLD
                else "degraded"
            )
        except Exception as e:
            info["status"] = "error"
            info["error"]  = str(e)

        # ── Read prediction tracker (prediction info) ──────────
        try:
            pred_tracker = read_json(PRED_TRACKER_KEYS[model])
            latest_run   = pred_tracker["runs"][-1] if pred_tracker.get("runs") else None
            if latest_run:
                info["predicted_on"]    = latest_run.get("date")
                info["prediction_run"]  = latest_run.get("run_id")
                info["predicted_count"] = latest_run.get("total_members")
        except:
            info["predicted_on"] = None

        health_info[model] = info

    # ── Master merge info ──────────────────────────────────────
    try:
        merge_tracker = read_json(TRACKER_KEYS.get("master", "predictions/master/merge_tracker.json"))
        master_info = {
            "merged_at"     : merge_tracker.get("merged_at"),
            "total_members" : merge_tracker.get("total_members"),
        }
    except:
        master_info = None

    return {
        "status"  : "success",
        "models"  : health_info,
        "master"  : master_info,
        "checked" : str(date.today())
    }