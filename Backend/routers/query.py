# ═══════════════════════════════════════════════════════════════
# routers/query.py — Smart query and available filters endpoints
# ═══════════════════════════════════════════════════════════════

from fastapi import APIRouter
from typing import Optional
from datetime import date

from cos_client import read_csv, read_json, upload_file, get_presigned_url
from filters import apply_filters, validate_output, get_col_names
from reports.excel_builder import build_excel_with_validation
from reports.pdf_builder import build_pdf
from config import PRED_KEYS, TRACKER_KEYS, FILTER_COLS

router = APIRouter()


@router.post("/smart-query")
def smart_query(
    model       : str            = "attrition",
    tier        : Optional[str]  = None,
    branch      : Optional[str]  = None,
    county      : Optional[str]  = None,
    age_band    : Optional[str]  = None,
    income_band : Optional[str]  = None,
    life_stage  : Optional[str]  = None,
    min_prob    : Optional[float] = None,
    top_n       : Optional[int]  = None
):
    """
    Main query endpoint.
    Loads latest predictions, applies filters,
    validates output, auto-generates Excel + PDF.
    Returns summary + top members + download links.
    Supports model = attrition / loan / propensity / master
    """
    tier_col, prob_col = get_col_names(model)

    # Load latest predictions
    df           = read_csv(PRED_KEYS[model])
    total_before = len(df)

    # Apply filters
    df = apply_filters(
        df, model, tier, branch, county,
        age_band, income_band, life_stage,
        min_prob, top_n
    )

    # Validate
    validation = validate_output(
        df, model, tier, branch, top_n, min_prob
    )

    # ── Build display columns based on model ───────────────────
    if model == "master":
        display_cols = [
            c for c in [
                'member_id', 'priority_score', 'priority_action',
                'attrition_probability', 'attrition_tier',
                'loan_offer_score', 'loan_offer_tier',
                'propensity_probability', 'propensity_tier',
                'branch_assignment', 'county', 'age_band',
                'income_band', 'life_stage', 'employment_status',
                'attrition_shap_1', 'attrition_shap_2', 'attrition_shap_3', 'attrition_shap_4', 'attrition_shap_5',
                'loan_shap_1', 'loan_shap_2', 'loan_shap_3', 'loan_shap_4', 'loan_shap_5',
                'propensity_shap_1', 'propensity_shap_2', 'propensity_shap_3', 'propensity_shap_4', 'propensity_shap_5',
            ]
            if c in df.columns
        ]
    else:
        display_cols = [
            c for c in [
                'member_id', prob_col, tier_col,
                'branch_assignment', 'county', 'age_band',
                'income_band', 'life_stage', 'employment_status',
                'shap_reason_1', 'shap_reason_2', 'shap_reason_3',
                'shap_reason_4', 'shap_reason_5'
            ]
            if c in df.columns
        ]

    top_df = df.head(top_n or 100)[display_cols].fillna('')
    top_members = top_df.to_dict(orient='records')

    # Auto generate Excel
    today      = str(date.today())
    excel_file = f"{model}_{branch or 'all'}_{today}.xlsx"
    build_excel_with_validation(df, excel_file, validation)
    excel_key  = f"reports/excel/{excel_file}"
    upload_file(excel_file, excel_key)
    excel_url  = get_presigned_url(excel_key)

    # ── Model info — master uses merge tracker, others use version tracker
    if model == "master":
        tracker = read_json(TRACKER_KEYS[model])
        model_info = {
            "merged_at"      : tracker.get("merged_at"),
            "total_members"  : tracker.get("total_members"),
            "models_included": tracker.get("models_included"),
        }
        # Skip PDF for master (no single-model version/AUC)
        pdf_url = None
    else:
        tracker  = read_json(TRACKER_KEYS[model])
        latest   = tracker["versions"][-1]
        model_info = {
            "version"   : latest["version"],
            "trained_on": latest["trained_on"],
            "auc"       : latest["auc"]
        }
        # Auto generate PDF
        pdf_file = f"{model}_{branch or 'all'}_{today}.pdf"
        build_pdf(df, model, branch, tier, top_n, tracker, pdf_file)
        pdf_key  = f"reports/pdf/{pdf_file}"
        upload_file(pdf_file, pdf_key)
        pdf_url  = get_presigned_url(pdf_key)

    # ── Build summary ──────────────────────────────────────────
    if model == "master":
        summary = {
            "total_before_filter": total_before,
            "total_returned"     : len(df),
            "urgent_retention"   : int((df['priority_action'] == 'Urgent Retention').sum()),
            "loan_offer"         : int((df['priority_action'] == 'Loan Offer').sum()),
            "cd_offer"           : int((df['priority_action'] == 'CD Offer').sum()),
            "monitor_closely"    : int((df['priority_action'] == 'Monitor Closely').sum()),
            "standard"           : int((df['priority_action'] == 'Standard').sum()),
        }
    else:
        summary = {
            "total_before_filter": total_before,
            "total_returned"     : len(df),
            "high"               : int((df[tier_col] == 'High').sum()),
            "medium"             : int((df[tier_col] == 'Medium').sum()),
            "low"                : int((df[tier_col] == 'Low').sum()),
        }

    return {
        "status"       : "success",
        "model"        : model,
        "filters_used" : {
            "tier"       : tier,
            "branch"     : branch,
            "county"     : county,
            "age_band"   : age_band,
            "income_band": income_band,
            "life_stage" : life_stage,
            "min_prob"   : min_prob,
            "top_n"      : top_n
        },
        "summary"      : summary,
        "top_members"  : top_members,
        "model_info"   : model_info,
        "validation"   : validation,
        "downloads"    : {
            "excel_url" : excel_url,
            "pdf_url"   : pdf_url,
            "expires_in": "24 hours"
        }
    }


@router.get("/available-filters")
def available_filters(model: str = "attrition"):
    """
    Returns unique values for all filterable columns.
    Helps Orchestrate agent know what values are valid.
    """
    df      = read_csv(PRED_KEYS[model])
    filters = {}

    for col in FILTER_COLS:
        if col in df.columns:
            filters[col] = sorted(
                df[col].dropna().unique().tolist()
            )

    return {
        "status"  : "success",
        "model"   : model,
        "filters" : filters
    }