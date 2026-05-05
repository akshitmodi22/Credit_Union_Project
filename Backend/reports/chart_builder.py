# ═══════════════════════════════════════════════════════════════
# reports/chart_builder.py — Full BI chart generation
# Supports: bar, horizontal_bar, stacked_bar, pie, donut,
#           heatmap, comparison, distribution, treemap
# ═══════════════════════════════════════════════════════════════

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np
from datetime import date


# ── Brand color palette ────────────────────────────────────────
COLORS = {
    'primary'   : '#4F46E5',
    'danger'    : '#DC2626',
    'warning'   : '#F59E0B',
    'success'   : '#16A34A',
    'info'      : '#0EA5E9',
    'purple'    : '#9333EA',
    'pink'      : '#EC4899',
    'teal'      : '#14B8A6',
    'slate'     : '#64748B',
    'orange'    : '#EA580C',
}

TIER_COLORS = {
    'High'              : '#DC2626',
    'Medium'            : '#F59E0B',
    'Low'               : '#16A34A',
    'Urgent Retention'  : '#DC2626',
    'Loan Offer'        : '#0EA5E9',
    'CD Offer'          : '#9333EA',
    'Monitor Closely'   : '#F59E0B',
    'Standard'          : '#16A34A',
}

PALETTE = list(COLORS.values())


def _style_chart(fig, ax, title, subtitle=None):
    """Apply consistent professional styling."""
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#FAFAFA')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors='#475569', labelsize=9)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.grid(axis='y', alpha=0.3, color='#CBD5E1', linestyle='--')

    ax.set_title(title, fontsize=14, fontweight='bold', color='#1E293B',
                 pad=20, loc='left')
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes,
                fontsize=9, color='#94A3B8', style='italic')

    # Watermark
    fig.text(0.99, 0.01, f'Credit Union Intelligence · {date.today()}',
             fontsize=7, color='#CBD5E1', ha='right', va='bottom')


# ═══════════════════════════════════════════════════════════════
# 1. VERTICAL BAR CHART
# ═══════════════════════════════════════════════════════════════
def build_bar_chart(grouped, model, group_by, tier, filename, top_n=10):
    """Standard vertical bar chart — member counts by group."""
    series = pd.Series(grouped).sort_values(ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(range(len(series)), series.values,
                  color=TIER_COLORS.get(tier, COLORS['primary']),
                  edgecolor='white', width=0.7, zorder=3)

    ax.set_xticks(range(len(series)))
    ax.set_xticklabels(series.index, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Number of Members', fontsize=10, color='#475569')

    # Value labels on bars
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + max(series)*0.01,
                f'{int(h):,}', ha='center', va='bottom',
                fontsize=8, fontweight='bold', color='#475569')

    title = f"{tier or 'All'} {model.title()} — by {group_by.replace('_', ' ').title()}"
    _style_chart(fig, ax, title, f"{len(series)} groups shown · {int(series.sum()):,} total members")

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()


# ═══════════════════════════════════════════════════════════════
# 2. HORIZONTAL BAR CHART
# ═══════════════════════════════════════════════════════════════
def build_horizontal_bar(grouped, model, group_by, tier, filename, top_n=10):
    """Horizontal bar — better for long category names."""
    series = pd.Series(grouped).sort_values(ascending=True).tail(top_n)

    fig, ax = plt.subplots(figsize=(10, max(6, len(series) * 0.5)))
    bars = ax.barh(range(len(series)), series.values,
                   color=TIER_COLORS.get(tier, COLORS['primary']),
                   edgecolor='white', height=0.6, zorder=3)

    ax.set_yticks(range(len(series)))
    ax.set_yticklabels(series.index, fontsize=9)
    ax.set_xlabel('Number of Members', fontsize=10, color='#475569')

    for bar in bars:
        w = bar.get_width()
        ax.text(w + max(series)*0.01, bar.get_y() + bar.get_height()/2,
                f'{int(w):,}', ha='left', va='center',
                fontsize=8, fontweight='bold', color='#475569')

    title = f"{tier or 'All'} {model.title()} — by {group_by.replace('_', ' ').title()}"
    _style_chart(fig, ax, title)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()


# ═══════════════════════════════════════════════════════════════
# 3. STACKED BAR CHART
# ═══════════════════════════════════════════════════════════════
def build_stacked_bar(df, model, group_by, tier_col, filename, top_n=10):
    """Stacked bar showing tier breakdown per group."""
    cross = pd.crosstab(df[group_by], df[tier_col])

    # Sort by total count
    cross['_total'] = cross.sum(axis=1)
    cross = cross.sort_values('_total', ascending=False).head(top_n).drop('_total', axis=1)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Determine tier order and colors
    tier_order = [t for t in TIER_COLORS.keys() if t in cross.columns]
    remaining = [t for t in cross.columns if t not in tier_order]
    tier_order += remaining

    bottom = np.zeros(len(cross))
    for t in tier_order:
        if t in cross.columns:
            color = TIER_COLORS.get(t, COLORS['slate'])
            ax.bar(range(len(cross)), cross[t].values, bottom=bottom,
                   label=t, color=color, edgecolor='white', width=0.7, zorder=3)
            bottom += cross[t].values

    ax.set_xticks(range(len(cross)))
    ax.set_xticklabels(cross.index, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Number of Members', fontsize=10, color='#475569')
    ax.legend(fontsize=9, framealpha=0.9, edgecolor='#E2E8F0')

    title = f"{model.title()} Risk Breakdown — by {group_by.replace('_', ' ').title()}"
    _style_chart(fig, ax, title, f"Top {len(cross)} groups · Stacked by tier")

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()


# ═══════════════════════════════════════════════════════════════
# 4. PIE CHART
# ═══════════════════════════════════════════════════════════════
def build_pie_chart(grouped, model, group_by, tier, filename):
    """Pie chart for distribution / proportions."""
    series = pd.Series(grouped).sort_values(ascending=False)
    if len(series) > 8:
        other = series[7:].sum()
        series = pd.concat([series[:7], pd.Series({'Other': other})])

    colors = [TIER_COLORS.get(k, PALETTE[i % len(PALETTE)]) for i, k in enumerate(series.index)]

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        series.values, labels=series.index, autopct='%1.1f%%',
        colors=colors, startangle=90, pctdistance=0.75,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    for t in texts:
        t.set_fontsize(9)
        t.set_color('#475569')
    for t in autotexts:
        t.set_fontsize(8)
        t.set_fontweight('bold')
        t.set_color('white')

    title = f"{model.title()} — {group_by.replace('_', ' ').title()} Distribution"
    ax.set_title(title, fontsize=14, fontweight='bold', color='#1E293B', pad=20)

    fig.text(0.99, 0.01, f'Credit Union Intelligence · {date.today()}',
             fontsize=7, color='#CBD5E1', ha='right', va='bottom')

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()


# ═══════════════════════════════════════════════════════════════
# 5. DONUT CHART
# ═══════════════════════════════════════════════════════════════
def build_donut_chart(grouped, model, group_by, tier, filename):
    """Donut chart — pie with center hole + total count."""
    series = pd.Series(grouped).sort_values(ascending=False)
    total = series.sum()
    if len(series) > 8:
        other = series[7:].sum()
        series = pd.concat([series[:7], pd.Series({'Other': other})])

    colors = [TIER_COLORS.get(k, PALETTE[i % len(PALETTE)]) for i, k in enumerate(series.index)]

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        series.values, labels=series.index, autopct='%1.1f%%',
        colors=colors, startangle=90, pctdistance=0.82,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2, 'width': 0.4}
    )
    for t in texts:
        t.set_fontsize(9)
        t.set_color('#475569')
    for t in autotexts:
        t.set_fontsize(8)
        t.set_fontweight('bold')

    # Center text
    ax.text(0, 0, f'{int(total):,}', ha='center', va='center',
            fontsize=24, fontweight='bold', color='#1E293B')
    ax.text(0, -0.08, 'members', ha='center', va='center',
            fontsize=10, color='#94A3B8')

    title = f"{model.title()} — {group_by.replace('_', ' ').title()} Distribution"
    ax.set_title(title, fontsize=14, fontweight='bold', color='#1E293B', pad=20)

    fig.text(0.99, 0.01, f'Credit Union Intelligence · {date.today()}',
             fontsize=7, color='#CBD5E1', ha='right', va='bottom')

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()


# ═══════════════════════════════════════════════════════════════
# 6. COMPARISON BAR (multi-model side-by-side)
# ═══════════════════════════════════════════════════════════════
def build_comparison_bar(data_dict, group_by, filename, top_n=10):
    """
    Side-by-side bars comparing multiple models.
    data_dict = { 'attrition': {branch: count}, 'loan': {...}, ... }
    """
    all_groups = set()
    for v in data_dict.values():
        all_groups.update(v.keys())

    # Top N by total across all models
    totals = {}
    for g in all_groups:
        totals[g] = sum(data_dict[m].get(g, 0) for m in data_dict)
    top_groups = sorted(totals, key=totals.get, reverse=True)[:top_n]

    models = list(data_dict.keys())
    x = np.arange(len(top_groups))
    width = 0.8 / len(models)
    model_colors = [COLORS['danger'], COLORS['info'], COLORS['purple'],
                    COLORS['warning'], COLORS['success']]

    fig, ax = plt.subplots(figsize=(14, 6))
    for i, m in enumerate(models):
        vals = [data_dict[m].get(g, 0) for g in top_groups]
        ax.bar(x + i * width, vals, width, label=m.title(),
               color=model_colors[i % len(model_colors)],
               edgecolor='white', zorder=3)

    ax.set_xticks(x + width * (len(models) - 1) / 2)
    ax.set_xticklabels(top_groups, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Number of Members', fontsize=10, color='#475569')
    ax.legend(fontsize=9, framealpha=0.9, edgecolor='#E2E8F0')

    title = f"Model Comparison — by {group_by.replace('_', ' ').title()}"
    _style_chart(fig, ax, title, f"Top {len(top_groups)} groups · High risk")

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()


# ═══════════════════════════════════════════════════════════════
# 7. DISTRIBUTION HISTOGRAM
# ═══════════════════════════════════════════════════════════════
def build_distribution(values, model, column, filename, bins=20):
    """Histogram showing probability/score distribution."""
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.hist(values, bins=bins, color=COLORS['primary'],
            edgecolor='white', alpha=0.85, zorder=3)

    mean_val = np.mean(values)
    median_val = np.median(values)
    ax.axvline(mean_val, color=COLORS['danger'], linestyle='--', linewidth=1.5,
               label=f'Mean: {mean_val:.3f}')
    ax.axvline(median_val, color=COLORS['warning'], linestyle='--', linewidth=1.5,
               label=f'Median: {median_val:.3f}')

    ax.set_xlabel(column.replace('_', ' ').title(), fontsize=10, color='#475569')
    ax.set_ylabel('Frequency', fontsize=10, color='#475569')
    ax.legend(fontsize=9, framealpha=0.9, edgecolor='#E2E8F0')

    title = f"{model.title()} — {column.replace('_', ' ').title()} Distribution"
    _style_chart(fig, ax, title, f"{len(values):,} members · {bins} bins")

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()


# ═══════════════════════════════════════════════════════════════
# 8. HEATMAP (group_by x tier cross-tab)
# ═══════════════════════════════════════════════════════════════
def build_heatmap(df, group_by, tier_col, model, filename, top_n=10):
    """Heatmap showing intensity of tier distribution across groups."""
    cross = pd.crosstab(df[group_by], df[tier_col])

    cross['_total'] = cross.sum(axis=1)
    cross = cross.sort_values('_total', ascending=False).head(top_n).drop('_total', axis=1)

    fig, ax = plt.subplots(figsize=(10, max(5, len(cross) * 0.5)))

    im = ax.imshow(cross.values, cmap='YlOrRd', aspect='auto')

    ax.set_xticks(range(len(cross.columns)))
    ax.set_xticklabels(cross.columns, fontsize=9)
    ax.set_yticks(range(len(cross.index)))
    ax.set_yticklabels(cross.index, fontsize=9)

    # Annotate cells
    for i in range(len(cross.index)):
        for j in range(len(cross.columns)):
            val = cross.values[i, j]
            color = 'white' if val > cross.values.max() * 0.6 else '#1E293B'
            ax.text(j, i, f'{int(val):,}', ha='center', va='center',
                    fontsize=9, fontweight='bold', color=color)

    plt.colorbar(im, ax=ax, shrink=0.8, label='Member Count')

    title = f"{model.title()} — {group_by.replace('_', ' ').title()} × Risk Heatmap"
    ax.set_title(title, fontsize=14, fontweight='bold', color='#1E293B', pad=15)

    fig.text(0.99, 0.01, f'Credit Union Intelligence · {date.today()}',
             fontsize=7, color='#CBD5E1', ha='right', va='bottom')

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()


# ═══════════════════════════════════════════════════════════════
# 9. TREEMAP (requires squarify)
# ═══════════════════════════════════════════════════════════════
def build_treemap(grouped, model, group_by, tier, filename, top_n=12):
    """Treemap — area proportional to member count."""
    try:
        import squarify
    except ImportError:
        # Fallback to horizontal bar if squarify not installed
        build_horizontal_bar(grouped, model, group_by, tier, filename, top_n)
        return

    series = pd.Series(grouped).sort_values(ascending=False).head(top_n)
    total = series.sum()

    labels = [f"{name}\n{int(val):,}\n({val/total*100:.1f}%)"
              for name, val in series.items()]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(series))]

    fig, ax = plt.subplots(figsize=(12, 7))
    squarify.plot(sizes=series.values, label=labels, color=colors,
                  alpha=0.85, ax=ax, text_kwargs={'fontsize': 9, 'color': 'white', 'fontweight': 'bold'},
                  edgecolor='white', linewidth=2)

    ax.axis('off')
    title = f"{tier or 'All'} {model.title()} — {group_by.replace('_', ' ').title()} Treemap"
    ax.set_title(title, fontsize=14, fontweight='bold', color='#1E293B', pad=15)

    fig.text(0.99, 0.01, f'Credit Union Intelligence · {date.today()}',
             fontsize=7, color='#CBD5E1', ha='right', va='bottom')

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()


# ═══════════════════════════════════════════════════════════════
# AUTO-SELECT: pick the best chart type based on context
# ═══════════════════════════════════════════════════════════════
def auto_select_chart_type(query_hint, group_count, is_tier_breakdown, is_multi_model):
    """
    Intelligently pick the best chart type based on context.
    Called by the router when chart_type='auto'.
    """
    q = (query_hint or '').lower()

    # Explicit keywords
    if any(w in q for w in ['pie', 'percentage', 'proportion', 'share']):
        return 'pie'
    if any(w in q for w in ['donut', 'ring']):
        return 'donut'
    if any(w in q for w in ['heatmap', 'heat map', 'intensity', 'matrix']):
        return 'heatmap'
    if any(w in q for w in ['distribution', 'histogram', 'spread', 'frequency']):
        return 'distribution'
    if any(w in q for w in ['compare', 'comparison', 'vs', 'versus', 'side by side']):
        return 'comparison'
    if any(w in q for w in ['stacked', 'breakdown', 'composition']):
        return 'stacked_bar'
    if any(w in q for w in ['treemap', 'tree map', 'area']):
        return 'treemap'
    if any(w in q for w in ['horizontal']):
        return 'horizontal_bar'

    # Smart auto-select based on data
    if is_multi_model:
        return 'comparison'
    if is_tier_breakdown:
        return 'stacked_bar'
    if group_count <= 5:
        return 'donut'
    if group_count > 15:
        return 'horizontal_bar'

    return 'bar'