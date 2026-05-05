# ═══════════════════════════════════════════════════════════════
# utils/merger.py — Merges 3 prediction CSVs + raw demographics
#                   into a single master CSV
# ═══════════════════════════════════════════════════════════════

import pandas as pd
import io
import json
from datetime import date
from cos_client import read_csv, write_csv, write_json, read_json
from config import COS_PATHS


def build_master_csv() -> dict:
    """
    Reads raw member demographics from COS (raw_data/cu_members.csv),
    merges with all 3 model prediction CSVs on member_id,
    adds priority scoring, and saves master CSV back to COS.
    """

    # ── Step 1: Load raw member demographics ───────────────────
    print("Loading raw member demographics from COS...")
    df_members = read_csv(COS_PATHS["raw_members"])
    print(f"Raw members loaded: {len(df_members)} rows, columns: {df_members.columns.tolist()}")

    # ── Step 2: Load all 3 prediction CSVs ─────────────────────
    print("Loading attrition predictions...")
    df_atr = read_csv("predictions/attrition/attrition_predictions_latest.csv")

    print("Loading loan predictions...")
    df_loan = read_csv("predictions/loan_offers/loan_predictions_latest.csv")

    print("Loading propensity predictions...")
    df_prop = read_csv("predictions/propensity/propensity_predictions_latest.csv")

    print(f"Loaded: attrition={len(df_atr)}, loan={len(df_loan)}, propensity={len(df_prop)}")

    # ── Step 3: Select demographic columns from raw data ───────
    demo_cols = [
        'member_id',
        'branch_assignment',
        'county',
        'age_band',
        'income_band',
        'life_stage',
        'employment_status',
        'tenure_years',
        'credit_score_band',
    ]
    demo_avail = [c for c in demo_cols if c in df_members.columns]
    df_demo = df_members[demo_avail].copy()
    print(f"Demographics columns used: {demo_avail}")

    # ── Step 4: Prepare prediction columns ─────────────────────

    # Attrition columns
    atr_cols = ['member_id', 'attrition_probability', 'attrition_tier']
    atr_shap = [f'shap_reason_{i}' for i in range(1, 6)]
    atr_shap = [c for c in atr_shap if c in df_atr.columns]
    atr_rename = {f'shap_reason_{i}': f'attrition_shap_{i}' for i in range(1, 6)}

    # Loan columns
    loan_cols = ['member_id', 'loan_offer_score', 'loan_offer_tier']
    loan_shap = [f'shap_reason_{i}' for i in range(1, 6)]
    loan_shap = [c for c in loan_shap if c in df_loan.columns]
    loan_rename = {f'shap_reason_{i}': f'loan_shap_{i}' for i in range(1, 6)}

    # Propensity columns
    prop_cols = ['member_id', 'propensity_probability', 'propensity_tier']
    prop_shap = [f'shap_reason_{i}' for i in range(1, 6)]
    prop_shap = [c for c in prop_shap if c in df_prop.columns]
    prop_rename = {f'shap_reason_{i}': f'propensity_shap_{i}' for i in range(1, 6)}

    # Clean each prediction dataframe
    df_atr_clean = df_atr[atr_cols + atr_shap].copy()
    df_atr_clean = df_atr_clean.rename(columns=atr_rename)

    df_loan_clean = df_loan[loan_cols + loan_shap].copy()
    df_loan_clean = df_loan_clean.rename(columns=loan_rename)

    df_prop_clean = df_prop[prop_cols + prop_shap].copy()
    df_prop_clean = df_prop_clean.rename(columns=prop_rename)

    # ── Step 5: Merge demographics + all 3 predictions ─────────
    print("Merging demographics + predictions...")

    master = df_demo.merge(df_atr_clean,  on='member_id', how='left')
    master = master.merge(df_loan_clean,  on='member_id', how='left')
    master = master.merge(df_prop_clean,  on='member_id', how='left')

    # ── Step 6: Add priority score + action ────────────────────
    master['attrition_probability'] = master['attrition_probability'].fillna(0)
    master['loan_offer_score']       = master['loan_offer_score'].fillna(0)
    master['propensity_probability'] = master['propensity_probability'].fillna(0)

    # Weighted priority score
    master['priority_score'] = (
        master['attrition_probability'] * 0.5 +
        master['loan_offer_score']       * 0.25 +
        master['propensity_probability'] * 0.25
    ).round(4)

    # Priority action
    def get_priority_action(row):
        if row['attrition_probability'] >= 0.7:
            return 'Urgent Retention'
        elif row['loan_offer_score'] >= 0.7:
            return 'Loan Offer'
        elif row['propensity_probability'] >= 0.7:
            return 'CD Offer'
        elif row['priority_score'] >= 0.5:
            return 'Monitor Closely'
        return 'Standard'

    master['priority_action'] = master.apply(get_priority_action, axis=1)

    # Sort by priority score
    master = master.sort_values('priority_score', ascending=False).reset_index(drop=True)

    print(f"Master CSV shape: {master.shape}")
    print(f"Total members: {len(master)}")

    # ── Step 7: Save to COS ────────────────────────────────────
    print("Saving master CSV to COS...")
    write_csv(
        "predictions/master/master_predictions_latest.csv",
        master
    )

    # Save merge tracker
    tracker = {
        "merged_at"        : str(date.today()),
        "total_members"    : len(master),
        "models_included"  : ["attrition", "loan", "propensity"],
        "demographics_src" : "raw_data/cu_members.csv",
        "attrition_count"  : len(df_atr),
        "loan_count"       : len(df_loan),
        "propensity_count" : len(df_prop),
        "columns"          : master.columns.tolist(),
    }
    write_json("predictions/master/merge_tracker.json", tracker)

    print("Master CSV saved successfully!")
    return tracker


def master_exists() -> bool:
    """Check if master CSV exists in COS."""
    try:
        read_json("predictions/master/merge_tracker.json")
        return True
    except:
        return False


def get_merge_info() -> dict:
    """Get info about last merge."""
    try:
        return read_json("predictions/master/merge_tracker.json")
    except:
        return None