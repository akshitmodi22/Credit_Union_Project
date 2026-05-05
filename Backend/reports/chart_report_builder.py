# ═══════════════════════════════════════════════════════════════
# reports/chart_report_builder.py — Professional BI PDF report
# Auto-generated alongside every chart request
# ═══════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
from datetime import date, datetime
from collections import Counter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image, PageBreak,
    HRFlowable
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart


# ── Brand colors ───────────────────────────────────────────────
BRAND_DARK   = colors.HexColor('#1E293B')
BRAND_PRIMARY= colors.HexColor('#4F46E5')
BRAND_LIGHT  = colors.HexColor('#EEF2FF')
BRAND_GRAY   = colors.HexColor('#64748B')
BRAND_BG     = colors.HexColor('#F8FAFC')
RED          = colors.HexColor('#DC2626')
AMBER        = colors.HexColor('#F59E0B')
GREEN        = colors.HexColor('#16A34A')
BLUE         = colors.HexColor('#0EA5E9')
PURPLE       = colors.HexColor('#9333EA')

TIER_COLORS_RL = {
    'High': RED, 'Medium': AMBER, 'Low': GREEN,
    'Urgent Retention': RED, 'Loan Offer': BLUE,
    'CD Offer': PURPLE, 'Monitor Closely': AMBER, 'Standard': GREEN,
}


def _get_styles():
    """Custom professional styles."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'ReportTitle', parent=styles['Title'],
        fontSize=22, textColor=BRAND_DARK,
        spaceAfter=6, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        'ReportSubtitle', parent=styles['Normal'],
        fontSize=10, textColor=BRAND_GRAY,
        spaceAfter=20, fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        'SectionHead', parent=styles['Heading2'],
        fontSize=13, textColor=BRAND_PRIMARY,
        spaceBefore=16, spaceAfter=8,
        fontName='Helvetica-Bold',
        borderPadding=(0, 0, 4, 0),
    ))
    styles.add(ParagraphStyle(
        'BodyText2', parent=styles['Normal'],
        fontSize=9, textColor=BRAND_DARK,
        spaceAfter=8, fontName='Helvetica',
        leading=14
    ))
    styles.add(ParagraphStyle(
        'Footnote', parent=styles['Normal'],
        fontSize=7, textColor=BRAND_GRAY,
        fontName='Helvetica-Oblique'
    ))
    styles.add(ParagraphStyle(
        'KPI', parent=styles['Normal'],
        fontSize=18, textColor=BRAND_DARK,
        fontName='Helvetica-Bold', alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        'KPILabel', parent=styles['Normal'],
        fontSize=8, textColor=BRAND_GRAY,
        fontName='Helvetica', alignment=TA_CENTER
    ))

    return styles


def _divider():
    """Horizontal rule divider."""
    return HRFlowable(
        width="100%", thickness=0.5,
        color=colors.HexColor('#E2E8F0'),
        spaceBefore=10, spaceAfter=10
    )


def _kpi_row(kpis):
    """Build a row of KPI boxes. kpis = list of (value, label) tuples."""
    styles = _get_styles()
    cells = []
    for val, label in kpis:
        cells.append([
            Paragraph(str(val), styles['KPI']),
            Paragraph(label, styles['KPILabel'])
        ])

    col_width = 480 / len(kpis)
    data = [cells]
    t = Table(data, colWidths=[col_width] * len(kpis))
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, -1), BRAND_LIGHT),
        ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',  (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',(0, 0), (-1, -1), 8),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ('BOX',         (0, 0), (-1, -1), 0.5, colors.HexColor('#C7D2FE')),
        ('INNERGRID',   (0, 0), (-1, -1), 0.5, colors.HexColor('#C7D2FE')),
    ]))
    return t


def _data_table(headers, rows, col_widths=None):
    """Build a styled data table."""
    data = [headers] + rows

    if not col_widths:
        col_widths = [480 / len(headers)] * len(headers)

    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        # Header
        ('BACKGROUND',     (0, 0), (-1, 0),  BRAND_PRIMARY),
        ('TEXTCOLOR',      (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',       (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',       (0, 0), (-1, 0),  9),
        # Body
        ('FONTSIZE',       (0, 1), (-1, -1), 8),
        ('FONTNAME',       (0, 1), (-1, -1), 'Helvetica'),
        ('TEXTCOLOR',      (0, 1), (-1, -1), BRAND_DARK),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_BG]),
        ('GRID',           (0, 0), (-1, -1), 0.3, colors.HexColor('#CBD5E1')),
        ('TOPPADDING',     (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING',  (0, 0), (-1, -1), 6),
        ('LEFTPADDING',    (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',   (0, 0), (-1, -1), 8),
        ('ALIGN',          (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN',         (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return t


def build_chart_report(
    df           : pd.DataFrame,
    model        : str,
    group_by     : str,
    tier         : str,
    chart_type   : str,
    breakdown    : dict,
    chart_image  : str,
    query_hint   : str,
    filename     : str,
    tier_col     : str = None,
    prob_col     : str = None,
):
    """
    Builds a professional BI PDF report with:
    - Cover header with query context
    - KPI summary strip
    - Embedded chart image
    - Full breakdown data table
    - Statistical analysis
    - Top SHAP reasons (if available)
    - Methodology footer
    """
    styles = _get_styles()
    doc = SimpleDocTemplate(
        filename, pagesize=letter,
        topMargin=40, bottomMargin=40,
        leftMargin=50, rightMargin=50
    )
    elements = []

    today_str = date.today().strftime('%B %d, %Y')

    # ══════════════════════════════════════════════════════════
    # COVER / HEADER
    # ══════════════════════════════════════════════════════════
    elements.append(Paragraph(
        "Credit Union Intelligence",
        styles['ReportTitle']
    ))
    elements.append(Paragraph(
        f"BI Analytics Report · {today_str}",
        styles['ReportSubtitle']
    ))
    elements.append(_divider())

    # Query context
    elements.append(Paragraph("Report Context", styles['SectionHead']))
    context_rows = [
        ["Field", "Value"],
        ["Query", query_hint or "Manual chart generation"],
        ["Model", model.title()],
        ["Group By", group_by.replace('_', ' ').title()],
        ["Tier Filter", tier or "All"],
        ["Chart Type", chart_type.replace('_', ' ').title()],
        ["Generated", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ["Total Records", f"{len(df):,}"],
    ]
    elements.append(_data_table(
        context_rows[0], context_rows[1:],
        col_widths=[120, 360]
    ))
    elements.append(Spacer(1, 16))

    # ══════════════════════════════════════════════════════════
    # KPI SUMMARY
    # ══════════════════════════════════════════════════════════
    elements.append(Paragraph("Key Metrics", styles['SectionHead']))

    kpis = [
        (f"{len(df):,}", "Total Members"),
    ]

    if tier_col and tier_col in df.columns:
        unique_tiers = df[tier_col].unique()
        if 'High' in unique_tiers:
            high_ct = int((df[tier_col] == 'High').sum())
            kpis.append((f"{high_ct:,}", "High Risk"))
        if 'Urgent Retention' in unique_tiers:
            urg_ct = int((df[tier_col] == 'Urgent Retention').sum())
            kpis.append((f"{urg_ct:,}", "Urgent Retention"))

    if prob_col and prob_col in df.columns:
        avg_score = df[prob_col].mean()
        kpis.append((f"{avg_score:.1%}", "Avg Score"))

    if group_by in df.columns:
        n_groups = df[group_by].nunique()
        kpis.append((str(n_groups), f"Unique {group_by.replace('_', ' ').title()}s"))

    if breakdown:
        top_k = max(breakdown, key=breakdown.get) if breakdown else 'N/A'
        top_v = max(breakdown.values()) if breakdown else 0
        kpis.append((f"{top_v:,}", f"Top: {top_k}"))

    # Limit to 5 KPIs
    kpis = kpis[:5]
    elements.append(_kpi_row(kpis))
    elements.append(Spacer(1, 16))

    # ══════════════════════════════════════════════════════════
    # CHART IMAGE
    # ══════════════════════════════════════════════════════════
    elements.append(Paragraph("Visualization", styles['SectionHead']))
    try:
        img = Image(chart_image, width=6.2*inch, height=3.2*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
    except Exception as e:
        elements.append(Paragraph(
            f"[Chart image could not be embedded: {e}]",
            styles['BodyText2']
        ))
    elements.append(Spacer(1, 16))

    # ══════════════════════════════════════════════════════════
    # BREAKDOWN TABLE
    # ══════════════════════════════════════════════════════════
    if breakdown and chart_type != 'distribution':
        elements.append(Paragraph("Detailed Breakdown", styles['SectionHead']))

        sorted_bd = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
        total = sum(v for _, v in sorted_bd) or 1

        bd_rows = []
        for rank, (name, count) in enumerate(sorted_bd, 1):
            pct = count / total * 100
            bd_rows.append([
                str(rank),
                str(name),
                f"{int(count):,}",
                f"{pct:.1f}%"
            ])

        elements.append(_data_table(
            ["Rank", group_by.replace('_', ' ').title(), "Members", "Share"],
            bd_rows,
            col_widths=[40, 220, 100, 100]
        ))
        elements.append(Spacer(1, 12))

    # ══════════════════════════════════════════════════════════
    # DISTRIBUTION STATS
    # ══════════════════════════════════════════════════════════
    if chart_type == 'distribution' and breakdown:
        elements.append(Paragraph("Statistical Summary", styles['SectionHead']))

        stat_rows = []
        for k, v in breakdown.items():
            if isinstance(v, float):
                stat_rows.append([k.title(), f"{v:.4f}"])
            else:
                stat_rows.append([k.title(), f"{v:,}"])

        elements.append(_data_table(
            ["Statistic", "Value"],
            stat_rows,
            col_widths=[200, 260]
        ))
        elements.append(Spacer(1, 12))

        # Percentile analysis
        if prob_col and prob_col in df.columns:
            vals = df[prob_col].dropna()
            pctiles = [10, 25, 50, 75, 90, 95, 99]
            pct_rows = [[f"{p}th percentile", f"{vals.quantile(p/100):.4f}"] for p in pctiles]

            elements.append(Paragraph("Percentile Analysis", styles['SectionHead']))
            elements.append(_data_table(
                ["Percentile", "Score"],
                pct_rows,
                col_widths=[200, 260]
            ))
            elements.append(Spacer(1, 12))

    # ══════════════════════════════════════════════════════════
    # TIER BREAKDOWN (if stacked/heatmap)
    # ══════════════════════════════════════════════════════════
    if chart_type in ('stacked_bar', 'heatmap') and tier_col and tier_col in df.columns:
        elements.append(Paragraph("Tier Distribution", styles['SectionHead']))

        tier_counts = df[tier_col].value_counts()
        total = len(df)
        tier_rows = []
        for t_name in tier_counts.index:
            ct = int(tier_counts[t_name])
            tier_rows.append([
                str(t_name),
                f"{ct:,}",
                f"{ct/total*100:.1f}%"
            ])

        elements.append(_data_table(
            ["Tier / Action", "Count", "Percentage"],
            tier_rows,
            col_widths=[200, 140, 140]
        ))
        elements.append(Spacer(1, 12))

    # ══════════════════════════════════════════════════════════
    # TOP SHAP REASONS (if available)
    # ══════════════════════════════════════════════════════════
    shap_cols = [c for c in df.columns if 'shap' in c.lower() and 'reason' in c.lower()]
    if not shap_cols:
        shap_cols = [c for c in df.columns if 'shap' in c.lower()]

    if shap_cols:
        elements.append(Paragraph("Key Risk Drivers", styles['SectionHead']))
        elements.append(Paragraph(
            "Top factors driving risk scores across the filtered population, "
            "ranked by frequency of appearance in SHAP explanations.",
            styles['BodyText2']
        ))

        all_reasons = []
        for col in shap_cols[:5]:
            all_reasons.extend(df[col].dropna().astype(str).tolist())

        reason_counts = Counter(all_reasons).most_common(10)
        reason_rows = []
        for rank, (reason, count) in enumerate(reason_counts, 1):
            pct = count / len(df) * 100 if len(df) > 0 else 0
            reason_rows.append([
                f"#{rank}",
                str(reason)[:55],
                f"{count:,}",
                f"{pct:.1f}%"
            ])

        elements.append(_data_table(
            ["#", "Risk Driver", "Occurrences", "% of Population"],
            reason_rows,
            col_widths=[30, 260, 80, 90]
        ))
        elements.append(Spacer(1, 12))

    # ══════════════════════════════════════════════════════════
    # TOP MEMBERS SAMPLE
    # ══════════════════════════════════════════════════════════
    elements.append(Paragraph("Top 15 Members (Highest Risk)", styles['SectionHead']))

    show_cols = ['member_id']
    if prob_col and prob_col in df.columns:
        show_cols.append(prob_col)
    if tier_col and tier_col in df.columns:
        show_cols.append(tier_col)
    if 'branch_assignment' in df.columns:
        show_cols.append('branch_assignment')
    if 'income_band' in df.columns:
        show_cols.append('income_band')

    show_cols = [c for c in show_cols if c in df.columns]
    sample = df.head(15)[show_cols]

    headers = [c.replace('_', ' ').title() for c in show_cols]
    rows = []
    for _, row in sample.iterrows():
        r = []
        for c in show_cols:
            val = row[c]
            if isinstance(val, float) and 0 <= val <= 1:
                r.append(f"{val:.1%}")
            else:
                r.append(str(val)[:30])
        rows.append(r)

    col_w = max(60, 460 / len(show_cols))
    elements.append(_data_table(headers, rows, col_widths=[col_w]*len(show_cols)))
    elements.append(Spacer(1, 16))

    # ══════════════════════════════════════════════════════════
    # FOOTER / METHODOLOGY
    # ══════════════════════════════════════════════════════════
    elements.append(_divider())
    elements.append(Paragraph("Methodology & Disclaimer", styles['SectionHead']))
    elements.append(Paragraph(
        "This report was auto-generated by the Credit Union Intelligence platform "
        "powered by IBM watsonx.ai. Risk scores are derived from XGBoost models trained "
        "on synthetic credit union member data. SHAP (SHapley Additive exPlanations) values "
        "provide model-agnostic feature importance at the individual member level. "
        "Priority scores in the master view are weighted composites: "
        "Attrition (50%) + Loan Offer (25%) + Deposit Propensity (25%). "
        "Charts and data reflect the latest prediction run. "
        "This report is for internal analysis only.",
        styles['BodyText2']
    ))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        f"© {date.today().year} Credit Union Intelligence · IBM watsonx.ai · "
        f"Report ID: {model}_{chart_type}_{date.today().strftime('%Y%m%d_%H%M')}",
        styles['Footnote']
    ))

    # ── Build PDF ──────────────────────────────────────────────
    doc.build(elements)