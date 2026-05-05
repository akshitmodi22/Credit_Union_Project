# ═══════════════════════════════════════════════════════════════
# reports/pdf_builder.py — PDF report generation
# ═══════════════════════════════════════════════════════════════

import pandas as pd
from collections import Counter
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from filters import get_col_names


def build_pdf(
    df       : pd.DataFrame,
    model    : str,
    branch   : str,
    tier     : str,
    top_n    : int,
    tracker  : dict,
    filename : str
):
    """
    Builds a formatted PDF report and saves locally.
    Contains: title, summary table, top members, SHAP reasons.
    """
    tier_col, prob_col = get_col_names(model)
    latest             = tracker["versions"][-1]
    doc                = SimpleDocTemplate(filename, pagesize=letter)
    styles             = getSampleStyleSheet()
    elements           = []

    # ── Title ──────────────────────────────────────────────────
    elements.append(Paragraph(
        f"Credit Union {model.title()} Risk Report",
        styles['Title']
    ))
    elements.append(Paragraph(
        f"Branch: {branch or 'All'} | "
        f"Tier: {tier or 'All'} | "
        f"Generated: {date.today()} | "
        f"Model v{latest['version']} | "
        f"AUC: {latest['auc']}",
        styles['Normal']
    ))
    elements.append(Spacer(1, 12))

    # ── Summary table ──────────────────────────────────────────
    elements.append(Paragraph("Summary", styles['Heading2']))
    summary_data = [
        ["Metric",        "Count"],
        ["Total Members", str(len(df))],
        ["High Risk",     str((df[tier_col] == 'High').sum())],
        ["Medium Risk",   str((df[tier_col] == 'Medium').sum())],
        ["Low Risk",      str((df[tier_col] == 'Low').sum())],
    ]
    t = Table(summary_data, colWidths=[200, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND',     (0, 0), (-1, 0),  colors.darkblue),
        ('TEXTCOLOR',      (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',       (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',       (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightblue]),
        ('GRID',           (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING',        (0, 0), (-1, -1), 8),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))

    # ── Top members table ──────────────────────────────────────
    show_n = min(top_n or 20, len(df))
    elements.append(Paragraph(
        f"Top {show_n} Members by Risk",
        styles['Heading2']
    ))
    table_data = [["Member ID", "Risk %", "Tier", "Top Reason"]]
    for _, row in df.head(show_n).iterrows():
        table_data.append([
            str(row['member_id']),
            f"{row[prob_col] * 100:.1f}%",
            str(row[tier_col]),
            str(row.get('shap_reason_1', ''))[:45]
        ])

    mt = Table(table_data, colWidths=[80, 60, 60, 250])
    mt.setStyle(TableStyle([
        ('BACKGROUND',     (0, 0), (-1, 0),  colors.darkblue),
        ('TEXTCOLOR',      (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',       (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',       (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('GRID',           (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING',        (0, 0), (-1, -1), 6),
    ]))
    elements.append(mt)
    elements.append(Spacer(1, 12))

    # ── Top SHAP reasons ───────────────────────────────────────
    elements.append(Paragraph(
        "Top Reasons Driving Risk",
        styles['Heading2']
    ))
    all_reasons = []
    for j in range(1, 11):
        col = f'shap_reason_{j}'
        if col in df.columns:
            all_reasons.extend(df[col].dropna().tolist())

    reason_counts = Counter(all_reasons).most_common(10)
    reason_data   = [["Rank", "Reason", "Members Affected"]]
    for rank, (reason, count) in enumerate(reason_counts, 1):
        pct = count / len(df) * 100 if len(df) > 0 else 0
        reason_data.append([
            f"#{rank}",
            str(reason)[:50],
            f"{count:,} ({pct:.1f}%)"
        ])

    rt = Table(reason_data, colWidths=[40, 280, 130])
    rt.setStyle(TableStyle([
        ('BACKGROUND',     (0, 0), (-1, 0),  colors.darkblue),
        ('TEXTCOLOR',      (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',       (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',       (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ('GRID',           (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING',        (0, 0), (-1, -1), 6),
    ]))
    elements.append(rt)

    doc.build(elements)