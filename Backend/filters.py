# ═══════════════════════════════════════════════════════════════
# filters.py — Data filtering and validation logic
# ═══════════════════════════════════════════════════════════════

import pandas as pd
from config import TIER_COLS, PROB_COLS


def get_col_names(model: str):
    """Returns tier and probability column names for a model."""
    tier_col = TIER_COLS.get(model, "attrition_tier")
    prob_col = PROB_COLS.get(model, "attrition_probability")
    return tier_col, prob_col


def apply_filters(
    df          : pd.DataFrame,
    model       : str   = "attrition",
    tier        : str   = None,
    branch      : str   = None,
    county      : str   = None,
    age_band    : str   = None,
    income_band : str   = None,
    life_stage  : str   = None,
    min_prob    : float = None,
    top_n       : int   = None
) -> pd.DataFrame:
    """
    Applies any combination of filters to a predictions DataFrame.
    Returns filtered DataFrame sorted by risk descending.
    """
    tier_col, prob_col = get_col_names(model)

    if tier and tier_col in df.columns:
        df = df[df[tier_col].str.lower() == tier.lower()]

    if branch and 'branch_assignment' in df.columns:
        df = df[df['branch_assignment'].str.lower() == branch.lower()]

    if county and 'county' in df.columns:
        df = df[df['county'].str.lower() == county.lower()]

    if age_band and 'age_band' in df.columns:
        df = df[df['age_band'] == age_band]

    if income_band and 'income_band' in df.columns:
        df = df[df['income_band'].str.lower() == income_band.lower()]

    if life_stage and 'life_stage' in df.columns:
        df = df[df['life_stage'].str.lower() == life_stage.lower()]

    if min_prob and prob_col in df.columns:
        df = df[df[prob_col] >= min_prob]

    if top_n:
        df = df.head(top_n)

    return df.reset_index(drop=True)


def validate_output(
    df       : pd.DataFrame,
    model    : str,
    tier     : str   = None,
    branch   : str   = None,
    top_n    : int   = None,
    min_prob : float = None
) -> dict:
    """
    Validates that filtered output matches requested filters.
    Returns dict of check results with passed/failed status.
    """
    tier_col, prob_col = get_col_names(model)
    checks = {}

    # Count check
    if top_n:
        checks["count"] = {
            "expected" : top_n,
            "actual"   : len(df),
            "passed"   : len(df) <= top_n
        }

    # Branch check
    if branch and 'branch_assignment' in df.columns:
        wrong = df[
            df['branch_assignment'].str.lower() != branch.lower()
        ]
        checks["branch"] = {
            "expected"   : branch,
            "wrong_rows" : len(wrong),
            "passed"     : len(wrong) == 0
        }

    # Tier check
    if tier and tier_col in df.columns:
        wrong = df[df[tier_col].str.lower() != tier.lower()]
        checks["tier"] = {
            "expected"   : tier,
            "wrong_rows" : len(wrong),
            "passed"     : len(wrong) == 0
        }

    # Sort order check
    if prob_col in df.columns and len(df) > 0:
        checks["sorted"] = {
            "passed"      : bool(df[prob_col].is_monotonic_decreasing),
            "highest_risk": float(df[prob_col].iloc[0]),
            "lowest_risk" : float(df[prob_col].iloc[-1])
        }

    # Null member_id check
    checks["no_nulls"] = {
        "null_member_ids" : int(df['member_id'].isnull().sum()),
        "passed"          : int(df['member_id'].isnull().sum()) == 0
    }

    # Min probability check
    if min_prob and prob_col in df.columns:
        wrong = df[df[prob_col] < min_prob]
        checks["min_prob"] = {
            "expected"   : min_prob,
            "wrong_rows" : len(wrong),
            "passed"     : len(wrong) == 0
        }

    # Overall pass/fail
    checks["all_valid"] = all(
        v.get("passed", True)
        for v in checks.values()
        if isinstance(v, dict)
    )

    return checks