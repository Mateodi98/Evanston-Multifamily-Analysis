import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load master DataFrame
df = pd.read_csv('data/listings_with_rents.csv')

# ── 1. Price Distribution ────────────────────────────────────────────────
fig1 = px.histogram(
    df, x='price', nbins=15,
    title='Distribution of Sale Prices — Evanston Multifamily (Last 12 Months)',
    labels={'price': 'Sale Price ($)', 'count': 'Number of Properties'},
    color_discrete_sequence=['#1565C0']
)
fig1.update_layout(bargap=0.1)
fig1.write_html('data/eda_price_distribution.html')
print("✓ Price distribution chart saved")

# ── 2. GRM Distribution ──────────────────────────────────────────────────
fig2 = px.histogram(
    df, x='grm', nbins=15,
    title='Gross Rent Multiplier Distribution — Evanston Multifamily',
    labels={'grm': 'GRM', 'count': 'Number of Properties'},
    color_discrete_sequence=['#C8963E']
)
fig2.add_vline(x=9, line_dash='dash', line_color='red',
               annotation_text='GRM = 9 threshold')
fig2.write_html('data/eda_grm_distribution.html')
print("✓ GRM distribution chart saved")

# ── 3. Price vs Effective Gross Income Scatter ───────────────────────────
fig3 = px.scatter(
    df, x='price', y='effective_gross_income',
    hover_data=['address', 'beds', 'est_units', 'grm'],
    title='Purchase Price vs Effective Gross Income',
    labels={
        'price': 'Purchase Price ($)',
        'effective_gross_income': 'Effective Gross Income ($)'
    },
    color='grm',
    color_continuous_scale='RdYlGn_r'
)
fig3.write_html('data/eda_price_vs_egi.html')
print("✓ Price vs EGI scatter saved")

# ── 4. GRM by Number of Units ────────────────────────────────────────────
fig4 = px.box(
    df, x='est_units', y='grm',
    title='GRM by Estimated Number of Units',
    labels={'est_units': 'Estimated Units', 'grm': 'GRM'},
    color='est_units'
)
fig4.add_hline(y=9, line_dash='dash', line_color='red',
               annotation_text='GRM = 9 threshold')
fig4.write_html('data/eda_grm_by_units.html')
print("✓ GRM by units chart saved")

# ── 5. Summary Statistics ────────────────────────────────────────────────
print("\n── Summary Statistics ──────────────────────────────────────────")
print(f"Total properties analyzed: {len(df)}")
print(f"\nPrice:")
print(f"  Min:    ${df['price'].min():>12,.0f}")
print(f"  Median: ${df['price'].median():>12,.0f}")
print(f"  Mean:   ${df['price'].mean():>12,.0f}")
print(f"  Max:    ${df['price'].max():>12,.0f}")
print(f"\nGRM:")
print(f"  Min:    {df['grm'].min():>8.2f}")
print(f"  Median: {df['grm'].median():>8.2f}")
print(f"  Mean:   {df['grm'].mean():>8.2f}")
print(f"  Max:    {df['grm'].max():>8.2f}")
print(f"\nProperties with GRM < 9 (strong candidates): {len(df[df['grm'] < 9])}")
print(f"Properties with GRM 9-12 (moderate):          {len(df[(df['grm'] >= 9) & (df['grm'] < 12)])}")
print(f"Properties with GRM > 12 (expensive):         {len(df[df['grm'] > 12])}")

print("\nAll EDA charts saved to /data/")