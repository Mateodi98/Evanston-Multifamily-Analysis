import pandas as pd
import numpy as np

# ── FINANCING ASSUMPTIONS ────────────────────────────────────────────────
# Based on current market conditions and buyer's target scenario
PURCHASE_PRICE_MAX = 620000
DOWN_PAYMENT_PCT = 0.20
INTEREST_RATE = 0.068
LOAN_TERM_YEARS = 30

# ── EXPENSE ASSUMPTIONS ──────────────────────────────────────────────────
# Source: Buyer's estimates based on Evanston market knowledge
INSURANCE_ANNUAL = 2500          # Fixed annual insurance premium
MAINTENANCE_PCT = 0.08           # 8% of gross annual rent
UTILITIES_ANNUAL = 5000          # Owner-paid utilities (annual)
PROPERTY_MGMT_PCT = 0.00         # Self-managed
CAPEX_RESERVE_PCT = 0.05         # 5% of gross annual rent

# ── MARKET ASSUMPTIONS ───────────────────────────────────────────────────
# Source: U.S. Census Bureau CPS/HVS Table 4, 2026 - Chicago Metro
VACANCY_RATE = 0.057

# ── APPRECIATION ASSUMPTIONS ─────────────────────────────────────────────
# Source: Zillow Home Value Index, Evanston IL, 2026
# Source: Evanston Now, February 2026 (evanstonnow.com)
APPRECIATION_RATE_CONSERVATIVE = 0.035  # 3.5% - Zillow trailing 12 months
APPRECIATION_RATE_MODERATE = 0.058      # 5.8% - Evanston Now January 2026
HOLD_YEARS = [5, 10]                    # Analysis horizons

# ── COOK COUNTY TAX RATE ─────────────────────────────────────────────────
# Source: Cook County Assessor - needs verification per property ⚠️
COOK_COUNTY_TAX_RATE = 0.018

def calculate_monthly_mortgage(price, down_pct, annual_rate, years):
    """Calculate monthly mortgage payment using amortization formula."""
    loan_amount = price * (1 - down_pct)
    monthly_rate = annual_rate / 12
    n_payments = years * 12
    payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / \
              ((1 + monthly_rate)**n_payments - 1)
    return payment

def calculate_appreciation(price, annual_rate, years):
    """Calculate projected property value and equity gain."""
    future_value = price * (1 + annual_rate) ** years
    appreciation_gain = future_value - price
    return round(future_value, 2), round(appreciation_gain, 2)

def underwrite_property(row):
    """
    Full pro forma underwriting for a single property.
    Structure adapted from Coach Carson Simple Rental Calculator v1.0
    Source: coachcarson.com
    Extended with Break-Even Ratio per Fannie Mae 2-4 unit guidelines
    and DSCR as supplementary investment viability metric.
    """
    price = row['price']
    gross_annual_rent = row['est_gross_annual_rent']

    # ── REVENUE ─────────────────────────────────────────────────────────
    vacancy_loss = gross_annual_rent * VACANCY_RATE
    gross_adjusted_income = gross_annual_rent - vacancy_loss

    # ── EXPENSES ─────────────────────────────────────────────────────────
    property_taxes = price * COOK_COUNTY_TAX_RATE
    insurance = INSURANCE_ANNUAL
    maintenance = gross_annual_rent * MAINTENANCE_PCT
    utilities = UTILITIES_ANNUAL
    property_mgmt = gross_annual_rent * PROPERTY_MGMT_PCT
    capex_reserve = gross_annual_rent * CAPEX_RESERVE_PCT
    total_expenses = (property_taxes + insurance + maintenance +
                     utilities + property_mgmt + capex_reserve)

    # ── NOI ──────────────────────────────────────────────────────────────
    noi = gross_adjusted_income - total_expenses

    # ── FINANCING ────────────────────────────────────────────────────────
    loan_amount = price * (1 - DOWN_PAYMENT_PCT)
    down_payment = price * DOWN_PAYMENT_PCT
    monthly_mortgage = calculate_monthly_mortgage(
        price, DOWN_PAYMENT_PCT, INTEREST_RATE, LOAN_TERM_YEARS
    )
    annual_debt_service = monthly_mortgage * 12

    # ── CASH FLOW ────────────────────────────────────────────────────────
    annual_cash_flow = noi - annual_debt_service
    monthly_cash_flow = annual_cash_flow / 12

    # ── KEY METRICS ──────────────────────────────────────────────────────
    # Cap Rate
    cap_rate = (noi / price) * 100

    # DSCR - supplementary investment viability metric
    dscr = noi / annual_debt_service if annual_debt_service > 0 else 0

    # Break-Even Ratio - Fannie Mae 2-4 unit primary metric
    # Monthly rent / (monthly mortgage + monthly taxes + monthly insurance)
    monthly_taxes = property_taxes / 12
    monthly_insurance = insurance / 12
    monthly_rent = gross_annual_rent / 12
    break_even_ratio = monthly_rent / (monthly_mortgage + monthly_taxes + monthly_insurance)

    # Cash-on-Cash Return
    total_cash_invested = down_payment
    coc_return = (annual_cash_flow / total_cash_invested) * 100

    # Expense ratio
    expense_ratio = (total_expenses / gross_annual_rent) * 100

    # ── APPRECIATION & TOTAL RETURN ──────────────────────────────────────
    # Conservative scenario (3.5%/yr - Zillow 2026)
    fv_5yr_cons, appr_5yr_cons = calculate_appreciation(
        price, APPRECIATION_RATE_CONSERVATIVE, 5)
    fv_10yr_cons, appr_10yr_cons = calculate_appreciation(
        price, APPRECIATION_RATE_CONSERVATIVE, 10)

    # Moderate scenario (5.8%/yr - Evanston Now 2026)
    fv_5yr_mod, appr_5yr_mod = calculate_appreciation(
        price, APPRECIATION_RATE_MODERATE, 5)
    fv_10yr_mod, appr_10yr_mod = calculate_appreciation(
        price, APPRECIATION_RATE_MODERATE, 10)

    # Total return = Cash Flow + Appreciation (5yr conservative)
    total_cash_flow_5yr = annual_cash_flow * 5
    total_return_5yr_cons = total_cash_flow_5yr + appr_5yr_cons
    total_return_5yr_mod = total_cash_flow_5yr + appr_5yr_mod


    return {
        # Revenue
        'gross_annual_rent': round(gross_annual_rent, 2),
        'vacancy_loss': round(vacancy_loss, 2),
        'gross_adjusted_income': round(gross_adjusted_income, 2),
        # Expenses
        'property_taxes': round(property_taxes, 2),
        'insurance': round(insurance, 2),
        'maintenance': round(maintenance, 2),
        'utilities': round(utilities, 2),
        'capex_reserve': round(capex_reserve, 2),
        'total_expenses': round(total_expenses, 2),
        'expense_ratio_pct': round(expense_ratio, 2),
        # NOI
        'noi': round(noi, 2),
        # Financing
        'loan_amount': round(loan_amount, 2),
        'down_payment': round(down_payment, 2),
        'monthly_mortgage': round(monthly_mortgage, 2),
        'annual_debt_service': round(annual_debt_service, 2),
        # Cash Flow
        'annual_cash_flow': round(annual_cash_flow, 2),
        'monthly_cash_flow': round(monthly_cash_flow, 2),
        # Key Metrics
        'cap_rate': round(cap_rate, 2),
        'dscr': round(dscr, 3),
        'break_even_ratio': round(break_even_ratio, 3),
        'coc_return': round(coc_return, 2),
        # Appreciation
        'fv_5yr_conservative': fv_5yr_cons,
        'appreciation_5yr_conservative': appr_5yr_cons,
        'fv_5yr_moderate': fv_5yr_mod,
        'appreciation_5yr_moderate': appr_5yr_mod,
        'fv_10yr_conservative': fv_10yr_cons,
        'fv_10yr_moderate': fv_10yr_mod,
        'total_return_5yr_conservative': round(total_return_5yr_cons, 2),
        'total_return_5yr_moderate': round(total_return_5yr_mod, 2),
    }

# ── LOAD DATA ────────────────────────────────────────────────────────────
df = pd.read_csv('data/listings_with_rents.csv')

# ── DATA QUALITY FLAGS ───────────────────────────────────────────────────
# 1835 Darrow Ave excluded: cap rate 17.21% is unrealistic for Evanston
# likely due to unverified unit count. Flagged as data quality outlier.
df_excluded = df[df['address'] == '1835 Darrow Ave']
df = df[df['address'] != '1835 Darrow Ave'].reset_index(drop=True)
print(f"Excluded 1 outlier: 1835 Darrow Ave (cap rate outlier - see REFINEMENTS.md)")

# ── APPLY UNDERWRITING ───────────────────────────────────────────────────
results = df.apply(underwrite_property, axis=1, result_type='expand')
df = pd.concat([df[['address', 'price', 'beds', 'est_units',
                     'est_rent_per_unit', 'est_gross_annual_rent']], results], axis=1)

# ── DEAL ELIGIBILITY FLAGS ───────────────────────────────────────────────
df['fannie_eligible'] = (
    (df['break_even_ratio'] >= 1.0) &
    (df['dscr'] >= 1.0) &
    (df['cap_rate'] >= 5.6) &
    (df['price'] * (1 - DOWN_PAYMENT_PCT) <= 832750)  # 2026 conforming limit
)

# ── FILTER TO TARGET PRICE RANGE ─────────────────────────────────────────
df_target = df[df['price'] <= PURCHASE_PRICE_MAX].copy()

# ── PRINT RESULTS ────────────────────────────────────────────────────────
print("=" * 70)
print("EVANSTON MULTIFAMILY UNDERWRITING RESULTS")
print("Financing: 20% down | 6.8% rate | 30yr fixed")
print("=" * 70)

print(f"\nTotal properties analyzed: {len(df)}")
print(f"Properties at or below $620,000: {len(df_target)}")
print(f"Fannie Mae eligible (all criteria): {df['fannie_eligible'].sum()}")

print("\n── TARGET RANGE PROPERTIES (≤ $620,000) ──────────────────────────")
cols = ['address', 'price', 'monthly_mortgage', 'monthly_cash_flow',
        'cap_rate', 'dscr', 'break_even_ratio', 'fannie_eligible']
print(df_target[cols].to_string())

print("\n── TOP 5 DEALS BY BREAK-EVEN RATIO ───────────────────────────────")
top5 = df.nlargest(5, 'break_even_ratio')[cols]
print(top5.to_string())

print("\n── TOP 5 DEALS BY TOTAL RETURN (5yr Conservative) — ELIGIBLE ONLY ─")
top5 = df[df['fannie_eligible'] == True].nlargest(5, 'total_return_5yr_conservative')[
    ['address', 'price', 'monthly_cash_flow', 'cap_rate',
     'fv_5yr_conservative', 'total_return_5yr_conservative',
     'fv_5yr_moderate', 'total_return_5yr_moderate', 'fannie_eligible']
]
print(top5.to_string())

# ── SAVE RESULTS ─────────────────────────────────────────────────────────
df.to_csv('data/underwriting_results.csv', index=False)
print("\nSaved to data/underwriting_results.csv")