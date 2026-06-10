import pandas as pd
import numpy as np

# ── FINANCING ASSUMPTIONS BY PROPERTY TYPE ──────────────────────────────
# Based on current market conditions and buyer's target scenario
INTEREST_RATE = 0.068
LOAN_TERM_YEARS = 30
CLOSING_COSTS_PCT = 0.025

FINANCING_BY_TYPE = {
    2: {'down_pct': 0.20, 'max_price': 620000, 'label': 'Duplex'},
    3: {'down_pct': 0.15, 'max_price': 800000, 'label': '3-Flat'},
    4: {'down_pct': 0.15, 'max_price': 900000, 'label': '4-Unit'},
}

# ── EXPENSE ASSUMPTIONS ──────────────────────────────────────────────────
# Source: Buyer's estimates based on Evanston market knowledge
INSURANCE_ANNUAL = 2500
MAINTENANCE_PCT = 0.08
UTILITIES_ANNUAL = 5000
PROPERTY_MGMT_PCT = 0.00
CAPEX_RESERVE_PCT = 0.05

# ── MARKET ASSUMPTIONS ───────────────────────────────────────────────────
# Source: U.S. Census Bureau CPS/HVS Table 4, 2026 - Chicago Metro
VACANCY_RATE = 0.057

# ── COOK COUNTY TAX RATE ─────────────────────────────────────────────────
# Source: Cook County Assessor - needs verification per property ⚠️
COOK_COUNTY_TAX_RATE = 0.018

# ── APPRECIATION ASSUMPTIONS ─────────────────────────────────────────────
# Source: Zillow Home Value Index, Evanston IL, 2026
# Source: Evanston Now, February 2026 (evanstonnow.com)
APPRECIATION_RATE_CONSERVATIVE = 0.035
APPRECIATION_RATE_MODERATE = 0.058


def calculate_monthly_mortgage(price, down_pct, annual_rate, years):
    """Calculate monthly mortgage payment using amortization formula."""
    loan_amount = price * (1 - down_pct)
    monthly_rate = annual_rate / 12
    n_payments = years * 12
    payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / \
              ((1 + monthly_rate)**n_payments - 1)
    return payment


def calculate_principal_paydown(price, down_pct, annual_rate, years, hold_years):
    """Calculate cumulative principal paid down over hold period."""
    loan_amount = price * (1 - down_pct)
    monthly_rate = annual_rate / 12
    monthly_payment = calculate_monthly_mortgage(price, down_pct, annual_rate, years)
    balance = loan_amount
    total_principal = 0
    for month in range(1, hold_years * 12 + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment
        total_principal += principal_payment
    return round(total_principal, 2)

def calculate_appreciation(price, annual_rate, years):
    """Calculate projected property value and appreciation gain."""
    future_value = price * (1 + annual_rate) ** years
    appreciation_gain = future_value - price
    return round(future_value, 2), round(appreciation_gain, 2)


def calculate_cagr(total_cash_invested, total_return, years):
    """
    Calculate Compound Annual Growth Rate (CAGR).
    Allows apples-to-apples comparison with stock market returns.
    S&P 500 historical average: ~10.5%/yr
    """
    total_value = total_cash_invested + total_return
    if total_value <= 0 or total_cash_invested <= 0:
        return 0
    cagr = (total_value / total_cash_invested) ** (1 / years) - 1
    return round(cagr * 100, 2)


def underwrite_property(row):
    """
    Full pro forma underwriting for a single property.
    Structure adapted from Coach Carson Simple Rental Calculator v1.0
    Source: coachcarson.com
    Extended with Break-Even Ratio per Fannie Mae 2-4 unit guidelines,
    DSCR as supplementary investment viability metric,
    and total return analysis including appreciation and principal paydown.
    """
    price = row['price']
    gross_annual_rent = row['est_gross_annual_rent']

    # ── FINANCING ────────────────────────────────────────────────────────
    units = int(row['est_units'])
    financing = FINANCING_BY_TYPE.get(units, FINANCING_BY_TYPE[4])
    down_pct = financing['down_pct']

    loan_amount = price * (1 - down_pct)
    down_payment = price * down_pct
    closing_costs = price * CLOSING_COSTS_PCT
    total_cash_invested = down_payment + closing_costs
    monthly_mortgage = calculate_monthly_mortgage(
        price, down_pct, INTEREST_RATE, LOAN_TERM_YEARS)
    annual_debt_service = monthly_mortgage * 12

    # ── REVENUE ──────────────────────────────────────────────────────────
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

    # ── CASH FLOW ────────────────────────────────────────────────────────
    annual_cash_flow = noi - annual_debt_service
    monthly_cash_flow = annual_cash_flow / 12

    # ── KEY METRICS ──────────────────────────────────────────────────────
    cap_rate = (noi / price) * 100
    dscr = noi / annual_debt_service if annual_debt_service > 0 else 0
    monthly_taxes = property_taxes / 12
    monthly_insurance = insurance / 12
    monthly_rent = gross_annual_rent / 12
    break_even_ratio = monthly_rent / (
        monthly_mortgage + monthly_taxes + monthly_insurance)
    coc_return = (annual_cash_flow / total_cash_invested) * 100
    expense_ratio = (total_expenses / gross_annual_rent) * 100

    # ── PRINCIPAL PAYDOWN ────────────────────────────────────────────────
    principal_5yr = calculate_principal_paydown(
        price, down_pct, INTEREST_RATE, LOAN_TERM_YEARS, 5)
    principal_10yr = calculate_principal_paydown(
        price, down_pct, INTEREST_RATE, LOAN_TERM_YEARS, 10)

    # ── APPRECIATION ─────────────────────────────────────────────────────
    fv_5yr_cons, appr_5yr_cons = calculate_appreciation(
        price, APPRECIATION_RATE_CONSERVATIVE, 5)
    fv_10yr_cons, appr_10yr_cons = calculate_appreciation(
        price, APPRECIATION_RATE_CONSERVATIVE, 10)
    fv_5yr_mod, appr_5yr_mod = calculate_appreciation(
        price, APPRECIATION_RATE_MODERATE, 5)
    fv_10yr_mod, appr_10yr_mod = calculate_appreciation(
        price, APPRECIATION_RATE_MODERATE, 10)

    # ── TOTAL RETURN ─────────────────────────────────────────────────────
    cashflow_5yr = annual_cash_flow * 5
    cashflow_10yr = annual_cash_flow * 10
    total_return_5yr_cons = cashflow_5yr + appr_5yr_cons + principal_5yr
    total_return_5yr_mod = cashflow_5yr + appr_5yr_mod + principal_5yr
    total_return_10yr_cons = cashflow_10yr + appr_10yr_cons + principal_10yr
    total_return_10yr_mod = cashflow_10yr + appr_10yr_mod + principal_10yr

    # ── TOTAL ROI ────────────────────────────────────────────────────────
    roi_5yr_cons = (total_return_5yr_cons / total_cash_invested) * 100
    roi_5yr_mod = (total_return_5yr_mod / total_cash_invested) * 100
    roi_10yr_cons = (total_return_10yr_cons / total_cash_invested) * 100
    roi_10yr_mod = (total_return_10yr_mod / total_cash_invested) * 100

    return {
        'gross_annual_rent': round(gross_annual_rent, 2),
        'vacancy_loss': round(vacancy_loss, 2),
        'gross_adjusted_income': round(gross_adjusted_income, 2),
        'property_taxes': round(property_taxes, 2),
        'insurance': round(insurance, 2),
        'maintenance': round(maintenance, 2),
        'utilities': round(utilities, 2),
        'capex_reserve': round(capex_reserve, 2),
        'total_expenses': round(total_expenses, 2),
        'expense_ratio_pct': round(expense_ratio, 2),
        'noi': round(noi, 2),
        'loan_amount': round(loan_amount, 2),
        'down_payment': round(down_payment, 2),
        'closing_costs': round(closing_costs, 2),
        'total_cash_invested': round(total_cash_invested, 2),
        'monthly_mortgage': round(monthly_mortgage, 2),
        'annual_debt_service': round(annual_debt_service, 2),
        'annual_cash_flow': round(annual_cash_flow, 2),
        'monthly_cash_flow': round(monthly_cash_flow, 2),
        'cap_rate': round(cap_rate, 2),
        'dscr': round(dscr, 3),
        'break_even_ratio': round(break_even_ratio, 3),
        'coc_return': round(coc_return, 2),
        'principal_paydown_5yr': principal_5yr,
        'principal_paydown_10yr': principal_10yr,
        'fv_5yr_conservative': fv_5yr_cons,
        'appreciation_5yr_conservative': appr_5yr_cons,
        'fv_5yr_moderate': fv_5yr_mod,
        'appreciation_5yr_moderate': appr_5yr_mod,
        'fv_10yr_conservative': fv_10yr_cons,
        'appreciation_10yr_conservative': appr_10yr_cons,
        'fv_10yr_moderate': fv_10yr_mod,
        'appreciation_10yr_moderate': appr_10yr_mod,
        'total_return_5yr_conservative': round(total_return_5yr_cons, 2),
        'total_return_5yr_moderate': round(total_return_5yr_mod, 2),
        'total_return_10yr_conservative': round(total_return_10yr_cons, 2),
        'total_return_10yr_moderate': round(total_return_10yr_mod, 2),
        'roi_5yr_conservative_pct': round(roi_5yr_cons, 2),
        'roi_5yr_moderate_pct': round(roi_5yr_mod, 2),
        'roi_10yr_conservative_pct': round(roi_10yr_cons, 2),
        'roi_10yr_moderate_pct': round(roi_10yr_mod, 2),
        # CAGR - Annualized return for stock market comparison
        # S&P 500 historical average: ~10.5%/yr
        'cagr_5yr_conservative_pct': calculate_cagr(
            total_cash_invested, total_return_5yr_cons, 5),
        'cagr_5yr_moderate_pct': calculate_cagr(
            total_cash_invested, total_return_5yr_mod, 5),
        'cagr_10yr_conservative_pct': calculate_cagr(
            total_cash_invested, total_return_10yr_cons, 10),
        'cagr_10yr_moderate_pct': calculate_cagr(
            total_cash_invested, total_return_10yr_mod, 10),
        # Cash-only CAGR (excludes appreciation - no leverage effect)
        'cagr_5yr_cash_only_pct': calculate_cagr(
            total_cash_invested, cashflow_5yr + principal_5yr, 5),
    }


# ── LOAD DATA ────────────────────────────────────────────────────────────
df = pd.read_csv('data/listings_with_rents.csv')

# ── DATA QUALITY FLAGS ───────────────────────────────────────────────────
df = df[df['address'] != '1835 Darrow Ave'].reset_index(drop=True)
print("Excluded 1 outlier: 1835 Darrow Ave (cap rate outlier - see REFINEMENTS.md)")

# ── APPLY UNDERWRITING ───────────────────────────────────────────────────
results = df.apply(underwrite_property, axis=1, result_type='expand')
df = pd.concat([df[['address', 'price', 'beds', 'est_units',
                     'est_rent_per_unit', 'est_gross_annual_rent']], results], axis=1)

# ── ADD PROPERTY LABELS AND ELIGIBILITY ──────────────────────────────────
df['property_label'] = df['est_units'].apply(
    lambda u: FINANCING_BY_TYPE.get(int(u), FINANCING_BY_TYPE[4])['label'])
df['max_price_for_type'] = df['est_units'].apply(
    lambda u: FINANCING_BY_TYPE.get(int(u), FINANCING_BY_TYPE[4])['max_price'])
df['down_pct'] = df['est_units'].apply(
    lambda u: FINANCING_BY_TYPE.get(int(u), FINANCING_BY_TYPE[4])['down_pct'])
df['fannie_eligible'] = (
    (df['break_even_ratio'] >= 1.0) &
    (df['dscr'] >= 1.0) &
    (df['cap_rate'] >= 5.6) &
    (df['price'] <= df['max_price_for_type'])
)

# ── PRINT RESULTS ────────────────────────────────────────────────────────
print("=" * 70)
print("EVANSTON MULTIFAMILY UNDERWRITING RESULTS")
print("Duplex: 20% down | 3-Flat: 15% down | 4-Unit: 15% down")
print("All: 6.8% rate | 30yr fixed | 2.5% closing costs")
print("=" * 70)

print(f"\nTotal properties analyzed: {len(df)}")
for units, info in FINANCING_BY_TYPE.items():
    subset = df[df['est_units'] == units]
    eligible = subset[subset['fannie_eligible'] == True]
    print(f"{info['label']}: {len(subset)} properties | "
          f"{len(eligible)} eligible | "
          f"Avg cash flow: ${subset['monthly_cash_flow'].mean():,.0f}/mo")

cols = ['address', 'price', 'property_label', 'monthly_cash_flow',
        'cap_rate', 'dscr', 'break_even_ratio', 'fannie_eligible']

print("\n── RESULTS BY PROPERTY TYPE ───────────────────────────────────────")
for units, info in FINANCING_BY_TYPE.items():
    subset = df[df['est_units'] == units].copy()
    print(f"\n{info['label']} ({units} units) — {info['down_pct']*100:.0f}% down "
          f"| max ${info['max_price']:,}:")
    print(subset[cols].to_string())

print("\n── TOP 5 DEALS BY 5YR TOTAL ROI (ELIGIBLE ONLY) ──────────────────")
top5 = df[df['fannie_eligible'] == True].nlargest(5, 'roi_5yr_conservative_pct')[
    ['address', 'property_label', 'price', 'monthly_cash_flow',
     'total_cash_invested', 'principal_paydown_5yr',
     'appreciation_5yr_conservative', 'total_return_5yr_conservative',
     'roi_5yr_conservative_pct', 'roi_5yr_moderate_pct']
]
print(top5.to_string())
print("\n── TOP 5 DEALS BY 5YR CAGR vs S&P 500 (ELIGIBLE ONLY) ───────────")
print("S&P 500 historical average: ~10.5%/yr")
print("-" * 70)
top5 = df[df['fannie_eligible'] == True].nlargest(5, 'cagr_5yr_conservative_pct')[
    ['address', 'property_label', 'price', 'monthly_cash_flow',
     'total_cash_invested', 'total_return_5yr_conservative',
     'cagr_5yr_conservative_pct', 'cagr_5yr_moderate_pct',
     'cagr_5yr_cash_only_pct']
]
print(top5.to_string())

# ── SAVE RESULTS ─────────────────────────────────────────────────────────
df.to_csv('data/underwriting_results.csv', index=False)
print("\nSaved to data/underwriting_results.csv")