# ═══════════════════════════════════════════════════════════════
# routers/unified.py — Unified report endpoint (all 3 models)
# ═══════════════════════════════════════════════════════════════

from fastapi import APIRouter
from typing import Optional
from datetime import date

from cos_client import read_csv, upload_file, get_presigned_url
from config import PRED_KEYS

router = APIRouter()


@router.post("/unified-report")
def unified_report(
    branch : Optional[str] = None,
    county : Optional[str] = None,
    top_n  : Optional[int] = None
):
    """
    Merges all 3 model predictions on member_id.
    Adds priority_action flag.
    Returns unified Excel with all 3 scores per member.
    """
    # Load all 3 latest prediction CSVs
    attrition = read_csv(PRED_KEYS["attrition"])[[
        "member_id", "attrition_probability",
        "attrition_tier", "shap_reason_1"
    ]].rename(columns={"shap_reason_1": "attrition_top_reason"})

    loan = read_csv(PRED_KEYS["loan"])[[
        "member_id", "loan_offer_score",
        "loan_offer_tier", "shap_reason_1"
    ]].rename(columns={"shap_reason_1": "loan_top_reason"})

    propensity = read_csv(PRED_KEYS["propensity"])[[
        "member_id", "propensity_probability",
        "propensity_tier", "shap_reason_1"
    ]].rename(columns={"shap_reason_1": "propensity_top_reason"})

    # Merge all 3 on member_id
    report = (
        attrition
        .merge(loan,       on="member_id", how="inner")
        .merge(propensity, on="member_id", how="inner")
    )

    # Priority flag — high on all 3 models
    report["priority_action"] = (
        (report["attrition_probability"] >= 0.70) &
        (report["loan_offer_score"]       >= 0.60) &
        (report["propensity_probability"] >= 0.60)
    ).map({True: "HIGH — contact now", False: "standard"})

    # Apply filters
    if branch and 'branch_assignment' in report.columns:
        report = report[
            report['branch_assignment'].str.lower() == branch.lower()
        ]
    if county and 'county' in report.columns:
        report = report[
            report['county'].str.lower() == county.lower()
        ]
    if top_n:
        report = report.head(top_n)

    # Save Excel
    today    = str(date.today())
    filename = f"unified_report_{branch or 'all'}_{today}.xlsx"
    report.to_excel(filename, index=False)

    cos_key = f"reports/unified/{filename}"
    upload_file(filename, cos_key)
    url     = get_presigned_url(cos_key)

    priority_count = int(
        (report["priority_action"] == "HIGH — contact now").sum()
    )

    top_priority = (
        report[report["priority_action"] == "HIGH — contact now"]
        [[
            "member_id", "attrition_probability",
            "loan_offer_score", "propensity_probability",
            "priority_action"
        ]]
        .head(10)
        .to_dict(orient="records")
    )

    return {
        "status"           : "success",
        "total_members"    : len(report),
        "priority_actions" : priority_count,
        "standard_members" : len(report) - priority_count,
        "top_priority"     : top_priority,
        "downloads"        : {
            "excel_url" : url,
            "expires_in": "24 hours"
        }
    }