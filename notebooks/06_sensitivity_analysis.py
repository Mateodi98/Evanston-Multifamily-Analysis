import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── ASSUMPTIONS ──────────────────────────────────────────────────────────
LOAN_TERM_YEARS = 30
INSURANCE_ANNUAL = 2500
MAINTENANCE_PCT = 0.08
UTILITIES_ANNUAL = 5000
CAPEX_RESERVE_PCT = 0.05
VACANCY_RATE = 0.057
COOK_COUNTY_TAX_RATE = 0.018

# Price and rate ranges
PRICES = list(range(300000, 950000, 50000))
RATES = [r/10000 for r in range(550, 925, 25)]

# Property type assumptions
PROPERTY_TYPES = {
    'Duplex':  {'down_pct': 0.20, 'rent': 52752},   # 2 units × 2BR ($2,198)
    '3-Flat':  {'down_pct': 0.15, 'rent': 79128},   # 3 units × 2BR ($2,198)
    '4-Unit':  {'down_pct': 0.15, 'rent': 105504},  # 4 units × 2BR ($2,198)
}

def calculate_dscr(price, rate, down_pct, gross_annual_rent):
    """Calculate DSCR for a given price, rate and property type."""
    loan_amount = price * (1 - down_pct)
    monthly_rate = rate / 12
    n_payments = LOAN_TERM_YEARS * 12
    monthly_mortgage = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / \
                      ((1 + monthly_rate)**n_payments - 1)
    annual_debt_service = monthly_mortgage * 12

    # Revenue
    vacancy_loss = gross_annual_rent * VACANCY_RATE
    gross_adjusted_income = gross_annual_rent - vacancy_loss

    # Expenses
    property_taxes = price * COOK_COUNTY_TAX_RATE
    maintenance = gross_annual_rent * MAINTENANCE_PCT
    capex_reserve = gross_annual_rent * CAPEX_RESERVE_PCT
    total_expenses = (property_taxes + INSURANCE_ANNUAL +
                     maintenance + UTILITIES_ANNUAL + capex_reserve)

    noi = gross_adjusted_income - total_expenses
    dscr = noi / annual_debt_service if annual_debt_service > 0 else 0
    return round(dscr, 3)

def build_sensitivity_matrix(down_pct, gross_annual_rent):
    """Build DSCR matrix across price and rate combinations."""
    matrix = []
    for price in PRICES:
        row = []
        for rate in RATES:
            dscr = calculate_dscr(price, rate, down_pct, gross_annual_rent)
            row.append(dscr)
        matrix.append(row)
    return np.array(matrix)

# ── BUILD MATRICES ────────────────────────────────────────────────────────
matrices = {}
for prop_type, params in PROPERTY_TYPES.items():
    matrices[prop_type] = build_sensitivity_matrix(
        params['down_pct'], params['rent'])

# ── PRINT SUMMARY ─────────────────────────────────────────────────────────
print("=" * 70)
print("SENSITIVITY ANALYSIS — DSCR ACROSS PRICE × INTEREST RATE")
print("Green: DSCR ≥ 1.0 | Yellow: 0.8–1.0 | Red: < 0.8")
print("=" * 70)

rate_labels = [f"{r*100:.2f}%" for r in RATES]
price_labels = [f"${p:,}" for p in PRICES]

for prop_type, matrix in matrices.items():
    params = PROPERTY_TYPES[prop_type]
    print(f"\n── {prop_type} ({params['down_pct']*100:.0f}% down) ─────────────")
    df_matrix = pd.DataFrame(matrix, index=price_labels, columns=rate_labels)
    print(df_matrix.to_string())
    viable = (matrix >= 1.0).sum()
    total = matrix.size
    print(f"Viable combinations: {viable}/{total} ({viable/total*100:.1f}%)")

# ── VISUALIZATIONS ────────────────────────────────────────────────────────
fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=list(PROPERTY_TYPES.keys())
)

col = 1
for prop_type, matrix in matrices.items():
    fig.add_trace(
        go.Heatmap(
            z=matrix,
            x=rate_labels,
            y=price_labels,
            colorscale=[
                [0.0, '#d32f2f'],    # Red - DSCR < 0.8
                [0.4, '#f57c00'],    # Orange - DSCR 0.8-1.0
                [0.5, '#ffd600'],    # Yellow - DSCR ~1.0
                [0.6, '#81c784'],    # Light green
                [1.0, '#1b5e20'],    # Dark green - DSCR > 1.5
            ],
            zmin=0.5,
            zmax=2.0,
            text=matrix.round(2),
            texttemplate='%{text}',
            textfont={'size': 7},
            hovertemplate='Price: %{y}<br>Rate: %{x}<br>DSCR: %{z:.3f}<extra></extra>',
            showscale=(col == 3),
            colorbar=dict(
                title='DSCR',
                tickvals=[0.5, 0.8, 1.0, 1.25, 1.5, 2.0],
                ticktext=['0.5', '0.8', '1.0✓', '1.25', '1.5', '2.0']
            )
        ),
        row=1, col=col
    )
    col += 1

fig.update_layout(
    title='DSCR Sensitivity Analysis — Price × Interest Rate by Property Type',
    height=700,
    width=1400
)

fig.write_html('models/sensitivity_matrix.html')
print("\n✓ Sensitivity matrix saved to models/sensitivity_matrix.html")

# ── CURRENT SCENARIO HIGHLIGHT ────────────────────────────────────────────
print("\n── CURRENT SCENARIO (6.8% rate) ───────────────────────────────────")
rate_idx = RATES.index(0.068) if 0.068 in RATES else None

if rate_idx:
    for prop_type, matrix in matrices.items():
        params = PROPERTY_TYPES[prop_type]
        print(f"\n{prop_type} at 6.8%:")
        for i, price in enumerate(PRICES):
            dscr = matrix[i][rate_idx]
            status = "✅ VIABLE" if dscr >= 1.0 else "❌ NOT VIABLE"
            print(f"  ${price:,}: DSCR = {dscr:.3f} {status}")

# Save matrices
for prop_type, matrix in matrices.items():
    df_matrix = pd.DataFrame(matrix, index=price_labels, columns=rate_labels)
    df_matrix.to_csv(f'models/sensitivity_{prop_type.lower().replace("-","_").replace(" ","_")}.csv')
print("\n✓ Sensitivity matrices saved to models/")