# ═══════════════════════════════════════════════════════════════
# config.py — All constants and environment variables
# ═══════════════════════════════════════════════════════════════
from dotenv import load_dotenv
from pathlib import Path
import os

# ── Load .env from same directory as this file ─────────────────
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# ── Debug print — remove after confirming it works ─────────────
print(f"[config] .env path   : {env_path}")
print(f"[config] .env exists : {env_path.exists()}")
print(f"[config] COS_API_KEY : {bool(os.environ.get('COS_API_KEY'))}")

# ── COS ────────────────────────────────────────────────────────
BUCKET       = "credit-union-poc-new"          # ← updated
COS_ENDPOINT = os.environ.get(
    "COS_ENDPOINT",
    "https://s3.us-south.cloud-object-storage.appdomain.cloud"
)
COS_API_KEY      = os.environ.get("COS_API_KEY")
COS_INSTANCE_CRN = os.environ.get("COS_INSTANCE_CRN")

# ── Watson Studio ──────────────────────────────────────────────
WATSONX_URL = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_KEY = os.environ.get("WATSONX_APIKEY")
PROJECT_ID  = os.environ.get("PROJECT_ID", "754c80df-c361-4fef-b0a2-ff909ca368ad")

# ── Watson Studio Job IDs ──────────────────────────────────────
JOB_IDS = {
    "attrition_train"   : os.environ.get("ATTRITION_TRAIN_JOB_ID"),
    "attrition_predict" : os.environ.get("ATTRITION_PREDICT_JOB_ID"),
    "loan_train"        : os.environ.get("LOAN_TRAIN_JOB_ID"),
    "loan_predict"      : os.environ.get("LOAN_PREDICT_JOB_ID"),
    "propensity_train"  : os.environ.get("PROPENSITY_TRAIN_JOB_ID"),
    "propensity_predict": os.environ.get("PROPENSITY_PREDICT_JOB_ID"),
}

# ── COS folder paths ───────────────────────────────────────────
COS_PATHS = {
    "attrition_latest"  : "predictions/attrition/attrition_predictions_latest.csv",
    "loan_latest"       : "predictions/loan_offers/loan_predictions_latest.csv",
    "propensity_latest" : "predictions/propensity/propensity_predictions_latest.csv",
    "attrition_tracker" : "trackers/attrition_version_tracker.json",
    "loan_tracker"      : "trackers/loan_version_tracker.json",
    "propensity_tracker": "trackers/propensity_version_tracker.json",
    "excel_reports"     : "reports/excel/",
    "pdf_reports"       : "reports/pdf/",
    "chart_reports"     : "reports/charts/",
    "unified_reports"   : "reports/unified/",
    "raw_members"       : "raw_data/cu_members.csv",
    "master_latest"     : "predictions/master/master_predictions_latest.csv",
    "master_tracker"    : "predictions/master/merge_tracker.json",
}

# ── Column name mappings per model ─────────────────────────────
TIER_COLS = {
    "attrition"  : "attrition_tier",
    "loan"       : "loan_offer_tier",
    "propensity" : "propensity_tier",
    "master"     : "priority_action"
}

PROB_COLS = {
    "attrition"  : "attrition_probability",
    "loan"       : "loan_offer_score",
    "propensity" : "propensity_probability",
    "master"     : "priority_score"
}

PRED_KEYS = {
    "attrition"  : "predictions/attrition/attrition_predictions_latest.csv",
    "loan"       : "predictions/loan_offers/loan_predictions_latest.csv",
    "propensity" : "predictions/propensity/propensity_predictions_latest.csv",
    "master"     : "predictions/master/master_predictions_latest.csv"
}

TRACKER_KEYS = {
    "attrition"  : "trackers/attrition_version_tracker.json",
    "loan"       : "trackers/loan_version_tracker.json",
    "propensity" : "trackers/propensity_version_tracker.json",
    "master"     : "predictions/master/merge_tracker.json"
}

PRED_TRACKER_KEYS = {
    "attrition"  : "trackers/attrition_prediction_tracker.json",
    "loan"       : "trackers/loan_prediction_tracker.json",
    "propensity" : "trackers/propensity_prediction_tracker.json",
}

# ── Report settings ────────────────────────────────────────────
PRESIGNED_URL_EXPIRY = 86400
DEFAULT_TOP_N        = 20
MAX_TOP_N            = 1000

# ── AUC health threshold ───────────────────────────────────────
AUC_HEALTHY_THRESHOLD = 0.75

# ── Demographic filter columns ─────────────────────────────────
FILTER_COLS = [
    'branch_assignment',
    'county',
    'age_band',
    'income_band',
    'life_stage',
    'employment_status'
]