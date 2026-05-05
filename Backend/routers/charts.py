# ═══════════════════════════════════════════════════════════════
# routers/charts.py — Full BI chart generation endpoint
# Supports: bar, horizontal_bar, stacked_bar, pie, donut,
#           heatmap, comparison, distribution, treemap, auto
# ═══════════════════════════════════════════════════════════════

from fastapi import APIRouter
from typing import Optional
from datetime import date

from cos_client import read_csv, upload_file, get_presigned_url
from filters import apply_filters, get_col_names
from reports.chart_builder import (
    build_bar_chart, build_horizontal_bar, build_stacked_bar,
    build_pie_chart, build_donut_chart, build_comparison_bar,
    build_distribution, build_heatmap, build_treemap,
    auto_select_chart_type
)
from reports.chart_report_builder import build_chart_report
from config import PRED_KEYS, TIER_COLS, PROB_COLS

router = APIRouter()


@router.post("/generate-chart")
def generate_chart(
    model      : str           = "attrition",
    group_by   : str           = "branch_assignment",
    tier       : Optional[str] = "High",
    branch     : Optional[str] = None,
    county     : Optional[str] = None,
    chart_type : str           = "auto",
    top_n      : int           = 10,
    query_hint : Optional[str] = None,
):
    """
    Full BI chart generation endpoint.

    chart_type options:
      - auto           : intelligently picks the best chart
      - bar            : vertical bar chart
      - horizontal_bar : horizontal bar chart
      - stacked_bar    : stacked bar with tier/action breakdown
      - pie            : pie chart
      - donut          : donut chart with center total
      - heatmap        : group × tier heatmap matrix
      - comparison     : side-by-side multi-model comparison
      - distribution   : histogram of probability/score spread
      - treemap        : area-based treemap

    query_hint: the natural language query from the user
                (helps auto-select pick the right chart)
    """

    # ── Load data ──────────────────────────────────────────────
    df = read_csv(PRED_KEYS[model])

    tier_col, prob_col = get_col_names(model)

    # Apply filters (don't filter by tier for stacked/heatmap/distribution)
    needs_all_tiers = chart_type in ('stacked_bar', 'heatmap', 'distribution', 'auto')
    filter_tier = None if needs_all_tiers else tier
    df = apply_filters(df, model, filter_tier, branch, county)

    if group_by not in df.columns and chart_type not in ('distribution', 'comparison'):
        return {
            "error": f"Column '{group_by}' not found. "
                     f"Available: {df.columns.tolist()}"
        }

    # ── Auto-select chart type ─────────────────────────────────
    if chart_type == 'auto':
        group_count = df[group_by].nunique() if group_by in df.columns else 0
        is_tier = group_by == tier_col or 'tier' in (query_hint or '').lower()
        is_multi = 'compar' in (query_hint or '').lower() or 'vs' in (query_hint or '').lower()
        chart_type = auto_select_chart_type(query_hint, group_count, is_tier, is_multi)

    # ── Group data for count-based charts ──────────────────────
    if chart_type not in ('distribution', 'comparison'):
        # For stacked/heatmap, filter tier after grouping
        if chart_type in ('stacked_bar', 'heatmap'):
            grouped_dict = None  # these use df directly
        else:
            # Filter to requested tier for simple charts
            if tier and tier_col in df.columns:
                df_filtered = df[df[tier_col] == tier]
            else:
                df_filtered = df

            grouped = (
                df_filtered.groupby(group_by)
                .size()
                .sort_values(ascending=False)
                .head(top_n)
            )
            grouped_dict = grouped.to_dict()

    # ── Build chart ────────────────────────────────────────────
    today    = str(date.today())
    filename = f"{model}_{group_by}_{chart_type}_{today}.png"

    if chart_type == 'bar':
        build_bar_chart(grouped_dict, model, group_by, tier, filename, top_n)

    elif chart_type == 'horizontal_bar':
        build_horizontal_bar(grouped_dict, model, group_by, tier, filename, top_n)

    elif chart_type == 'stacked_bar':
        build_stacked_bar(df, model, group_by, tier_col, filename, top_n)

    elif chart_type == 'pie':
        build_pie_chart(grouped_dict, model, group_by, tier, filename)

    elif chart_type == 'donut':
        build_donut_chart(grouped_dict, model, group_by, tier, filename)

    elif chart_type == 'heatmap':
        build_heatmap(df, group_by, tier_col, model, filename, top_n)

    elif chart_type == 'comparison':
        # Build grouped counts for all 3 individual models
        data_dict = {}
        for m in ['attrition', 'loan', 'propensity']:
            try:
                mdf = read_csv(PRED_KEYS[m])
                m_tier_col = TIER_COLS[m]
                if tier and m_tier_col in mdf.columns:
                    mdf = mdf[mdf[m_tier_col] == tier]
                if group_by in mdf.columns:
                    data_dict[m] = mdf.groupby(group_by).size().to_dict()
            except Exception:
                pass
        build_comparison_bar(data_dict, group_by, filename, top_n)
        grouped_dict = {}
        for d in data_dict.values():
            for k, v in d.items():
                grouped_dict[k] = grouped_dict.get(k, 0) + v

    elif chart_type == 'distribution':
        if prob_col in df.columns:
            values = df[prob_col].dropna().values
            build_distribution(values, model, prob_col, filename)
            grouped_dict = {
                'mean'   : float(values.mean()),
                'median' : float(np.median(values)),
                'std'    : float(values.std()),
                'min'    : float(values.min()),
                'max'    : float(values.max()),
                'count'  : int(len(values)),
            }
        else:
            return {"error": f"Probability column '{prob_col}' not found."}

    elif chart_type == 'treemap':
        build_treemap(grouped_dict, model, group_by, tier, filename, top_n)

    else:
        return {"error": f"Unknown chart_type: {chart_type}. Options: bar, horizontal_bar, stacked_bar, pie, donut, heatmap, comparison, distribution, treemap, auto"}

    # ── Upload chart image ────────────────────────────────────
    cos_key = f"reports/charts/{filename}"
    upload_file(filename, cos_key)
    url = get_presigned_url(cos_key)

    # ── Auto-generate PDF report ───────────────────────────────
    pdf_filename = filename.replace('.png', '_report.pdf')
    try:
        build_chart_report(
            df           = df,
            model        = model,
            group_by     = group_by,
            tier         = tier,
            chart_type   = chart_type,
            breakdown    = grouped_dict if isinstance(grouped_dict, dict) else {},
            chart_image  = filename,
            query_hint   = query_hint or "",
            filename     = pdf_filename,
            tier_col     = tier_col,
            prob_col     = prob_col,
        )
        pdf_cos_key = f"reports/charts/{pdf_filename}"
        upload_file(pdf_filename, pdf_cos_key)
        pdf_url = get_presigned_url(pdf_cos_key)
    except Exception as e:
        print(f"[chart-report] PDF generation failed: {e}")
        pdf_url = None

    # Top group for simple charts
    if isinstance(grouped_dict, dict) and grouped_dict:
        sorted_groups = sorted(grouped_dict.items(), key=lambda x: x[1], reverse=True)
        top_group = str(sorted_groups[0][0])
        top_count = int(sorted_groups[0][1])
    else:
        top_group = None
        top_count = 0

    return {
        "status"      : "success",
        "chart_type"  : chart_type,
        "chart_url"   : url,
        "pdf_url"     : pdf_url,
        "model"       : model,
        "group_by"    : group_by,
        "tier_filter" : tier,
        "top_group"   : top_group,
        "top_count"   : top_count,
        "breakdown"   : grouped_dict,
        "total_rows"  : len(df),
        "expires_in"  : "24 hours"
    }


# Missing import for distribution
import numpy as np