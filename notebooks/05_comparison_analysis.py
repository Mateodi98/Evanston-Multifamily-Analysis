import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── LOAD DATA ────────────────────────────────────────────────────────────
df = pd.read_csv('data/underwriting_results.csv')

# ── FILTER ELIGIBLE ONLY FOR FAIR COMPARISON ─────────────────────────────
df_eligible = df[df['fannie_eligible'] == True].copy()

print("=" * 70)
print("PROPERTY TYPE COMPARISON ANALYSIS")
print("Evanston Multifamily Market — Owner Occupied Investment")
print("=" * 70)

# ── 1. SUMMARY STATS BY PROPERTY TYPE ────────────────────────────────────
metrics = ['monthly_cash_flow', 'cap_rate', 'dscr', 'break_even_ratio',
           'cagr_5yr_conservative_pct', 'cagr_5yr_cash_only_pct',
           'total_cash_invested', 'roi_5yr_conservative_pct']

print("\n── ELIGIBLE PROPERTIES ONLY ────────────────────────────────────────")
summary = df_eligible.groupby('property_label')[metrics].agg(['mean', 'median', 'count'])
print(summary.to_string())

# ── 2. STATISTICAL TEST ───────────────────────────────────────────────────
# Kruskal-Wallis test - non-parametric comparison (small sample sizes)
from scipy import stats

print("\n── STATISTICAL SIGNIFICANCE TEST ───────────────────────────────────")
print("Kruskal-Wallis Test: Is there a significant difference in CAGR")
print("between property types? (p < 0.05 = significant difference)")

duplex_cagr = df_eligible[df_eligible['property_label'] == 'Duplex']['cagr_5yr_conservative_pct']
flat_cagr = df_eligible[df_eligible['property_label'] == '3-Flat']['cagr_5yr_conservative_pct']
unit_cagr = df_eligible[df_eligible['property_label'] == '4-Unit']['cagr_5yr_conservative_pct']

if len(duplex_cagr) > 0 and len(flat_cagr) > 0 and len(unit_cagr) > 0:
    stat, p_value = stats.kruskal(duplex_cagr, flat_cagr, unit_cagr)
    print(f"\nKruskal-Wallis statistic: {stat:.4f}")
    print(f"P-value: {p_value:.4f}")
    if p_value < 0.05:
        print("Result: SIGNIFICANT difference between property types (p < 0.05)")
        print("→ We can REJECT the null hypothesis")
    else:
        print("Result: NO significant difference between property types (p >= 0.05)")
        print("→ We FAIL TO REJECT the null hypothesis")

# ── 3. VISUALIZATIONS ────────────────────────────────────────────────────

# Chart 1 — CAGR by Property Type (Box Plot)
fig1 = px.box(
    df_eligible,
    x='property_label',
    y='cagr_5yr_conservative_pct',
    color='property_label',
    title='5-Year CAGR by Property Type (Eligible Properties Only)',
    labels={
        'cagr_5yr_conservative_pct': 'CAGR 5yr Conservative (%)',
        'property_label': 'Property Type'
    },
    color_discrete_map={
        'Duplex': '#1565C0',
        '3-Flat': '#C8963E',
        '4-Unit': '#2E7D32'
    }
)
fig1.add_hline(y=10.5, line_dash='dash', line_color='red',
               annotation_text='S&P 500 avg: 10.5%/yr')
fig1.write_html('models/comparison_cagr_boxplot.html')
print("\n✓ CAGR box plot saved")

# Chart 2 — Monthly Cash Flow by Property Type
fig2 = px.box(
    df_eligible,
    x='property_label',
    y='monthly_cash_flow',
    color='property_label',
    title='Monthly Cash Flow by Property Type (Eligible Properties Only)',
    labels={
        'monthly_cash_flow': 'Monthly Cash Flow ($)',
        'property_label': 'Property Type'
    },
    color_discrete_map={
        'Duplex': '#1565C0',
        '3-Flat': '#C8963E',
        '4-Unit': '#2E7D32'
    }
)
fig2.add_hline(y=0, line_dash='dash', line_color='red',
               annotation_text='Break Even')
fig2.write_html('models/comparison_cashflow_boxplot.html')
print("✓ Cash flow box plot saved")

# Chart 3 — Cap Rate by Property Type
fig3 = px.box(
    df_eligible,
    x='property_label',
    y='cap_rate',
    color='property_label',
    title='Cap Rate by Property Type (Eligible Properties Only)',
    labels={
        'cap_rate': 'Cap Rate (%)',
        'property_label': 'Property Type'
    },
    color_discrete_map={
        'Duplex': '#1565C0',
        '3-Flat': '#C8963E',
        '4-Unit': '#2E7D32'
    }
)
fig3.add_hline(y=5.6, line_dash='dash', line_color='red',
               annotation_text='Market benchmark: 5.6%')
fig3.write_html('models/comparison_caprate_boxplot.html')
print("✓ Cap rate box plot saved")

# Chart 4 — Total Cash Invested vs 5yr Total Return Scatter
fig4 = px.scatter(
    df_eligible,
    x='total_cash_invested',
    y='total_return_5yr_conservative',
    color='property_label',
    size='monthly_cash_flow',
    hover_data=['address', 'price', 'cagr_5yr_conservative_pct'],
    title='Cash Invested vs 5yr Total Return by Property Type',
    labels={
        'total_cash_invested': 'Total Cash Invested ($)',
        'total_return_5yr_conservative': '5yr Total Return Conservative ($)',
        'property_label': 'Property Type'
    },
    color_discrete_map={
        'Duplex': '#1565C0',
        '3-Flat': '#C8963E',
        '4-Unit': '#2E7D32'
    }
)
fig4.write_html('models/comparison_investment_scatter.html')
print("✓ Investment scatter saved")

# Chart 5 — Average Metrics Comparison Bar Chart
avg_metrics = df_eligible.groupby('property_label').agg({
    'monthly_cash_flow': 'mean',
    'cap_rate': 'mean',
    'dscr': 'mean',
    'cagr_5yr_conservative_pct': 'mean',
    'cagr_5yr_cash_only_pct': 'mean'
}).reset_index()

fig5 = make_subplots(
    rows=2, cols=2,
    subplot_titles=[
        'Avg Monthly Cash Flow ($)',
        'Avg Cap Rate (%)',
        'Avg DSCR',
        'Avg 5yr CAGR Conservative (%)'
    ]
)

colors = {'Duplex': '#1565C0', '3-Flat': '#C8963E', '4-Unit': '#2E7D32'}

for _, row in avg_metrics.iterrows():
    color = colors[row['property_label']]
    fig5.add_trace(go.Bar(
        name=row['property_label'],
        x=[row['property_label']],
        y=[row['monthly_cash_flow']],
        marker_color=color,
        showlegend=False
    ), row=1, col=1)
    fig5.add_trace(go.Bar(
        name=row['property_label'],
        x=[row['property_label']],
        y=[row['cap_rate']],
        marker_color=color,
        showlegend=False
    ), row=1, col=2)
    fig5.add_trace(go.Bar(
        name=row['property_label'],
        x=[row['property_label']],
        y=[row['dscr']],
        marker_color=color,
        showlegend=False
    ), row=2, col=1)
    fig5.add_trace(go.Bar(
        name=row['property_label'],
        x=[row['property_label']],
        y=[row['cagr_5yr_conservative_pct']],
        marker_color=color,
        showlegend=False
    ), row=2, col=2)

fig5.update_layout(title='Property Type Comparison — Average Key Metrics')
fig5.write_html('models/comparison_metrics_overview.html')
print("✓ Metrics overview chart saved")

# ── 4. HYPOTHESIS VERDICT ─────────────────────────────────────────────────
print("\n── HYPOTHESIS VERDICT ──────────────────────────────────────────────")
print("Hypothesis: 3-flat at ≤$800k with 15% down will outperform")
print("duplex and 4-unit on CAGR, cash flow, and 5yr total ROI")
print()

for label in ['Duplex', '3-Flat', '4-Unit']:
    subset = df_eligible[df_eligible['property_label'] == label]
    if len(subset) > 0:
        print(f"{label} ({len(subset)} eligible properties):")
        print(f"  Avg Monthly Cash Flow: ${subset['monthly_cash_flow'].mean():,.0f}")
        print(f"  Avg Cap Rate:          {subset['cap_rate'].mean():.2f}%")
        print(f"  Avg DSCR:              {subset['dscr'].mean():.3f}")
        print(f"  Avg 5yr CAGR:          {subset['cagr_5yr_conservative_pct'].mean():.2f}%")
        print(f"  Avg Cash-Only CAGR:    {subset['cagr_5yr_cash_only_pct'].mean():.2f}%")
        print()

# Save summary
avg_metrics.to_csv('models/comparison_summary.csv', index=False)
print("✓ Comparison summary saved to models/comparison_summary.csv")