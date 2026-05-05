# ═══════════════════════════════════════════════════════════════
# routers/predictions.py — Run predictions and retrain endpoints
# ═══════════════════════════════════════════════════════════════
from fastapi import APIRouter
from jobs.studio_jobs import trigger_model_jobs

router = APIRouter()


@router.post("/run-predictions")
def run_predictions(model: str = "attrition"):
    """
    Triggers Watson Studio batch prediction Job.
    model: attrition / loan / propensity / all
    """
    results = trigger_model_jobs(model, job_type="predict")
    return {
        "status"  : "success",
        "model"   : model,
        "results" : results
    }


@router.post("/retrain")
def retrain(model: str = "attrition"):
    """
    Triggers Watson Studio retraining Job.
    model: attrition / loan / propensity / all
    """
    results = trigger_model_jobs(model, job_type="train")
    return {
        "status"  : "success",
        "model"   : model,
        "results" : results
    }