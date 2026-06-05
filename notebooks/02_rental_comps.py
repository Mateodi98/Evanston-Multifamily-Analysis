import pandas as pd
import numpy as np

# ── KNOWN LIMITATIONS ───────────────────────────────────────────────────
# Unit count is estimated from total bedroom count using a heuristic rule.
# Actual unit configurations may differ (e.g. a 6BR property could be a
# 2-flat with 3BR/unit or a 3-flat with 2BR/unit). Manual verification of
# unit counts against MLS listings is recommended before making investment
# decisions. This is flagged as a refinement item for future versions.
# ────────────────────────────────────────────────────────────────────────

# ── Evanston Market Rents ────────────────────────────────────────────────
# Source: Zillow Rental Market Trends - Evanston, IL
# Last updated: June 3, 2026
EVANSTON_MARKET_RENTS = {
    1: 1750,
    2: 2198,
    3: 3195,
    4: 5404,
}

# Cook County effective tax rate
# Source: Cook County Assessor - needs verification ⚠️
COOK_COUNTY_TAX_RATE = 0.018

# Vacancy rate
# Source: U.S. Census Bureau CPS/HVS Table 4, 2026
# Chicago-Naperville-Elgin, IL-IN Metro
VACANCY_RATE = 0.057

def estimate_units(beds):
    """Estimate number of units based on total bedroom count."""
    if beds <= 4:
        return 2
    elif beds <= 6:
        return 3
    else:
        return 4

def estimate_rent_per_unit(beds, units):
    """Estimate rent per unit based on bedrooms per unit."""
    beds_per_unit = beds / units
    if beds_per_unit <= 1.5:
        return EVANSTON_MARKET_RENTS[1]
    elif beds_per_unit <= 2.5:
        return EVANSTON_MARKET_RENTS[2]
    elif beds_per_unit <= 3.5:
        return EVANSTON_MARKET_RENTS[3]
    else:
        return EVANSTON_MARKET_RENTS[4]

# Load clean listings
df = pd.read_csv('data/clean_listings.csv')

# Apply rental estimates
df['est_units'] = df['beds'].apply(estimate_units)
df['est_rent_per_unit'] = df.apply(
    lambda row: estimate_rent_per_unit(row['beds'], row['est_units']), axis=1
)
df['est_gross_monthly_rent'] = df['est_units'] * df['est_rent_per_unit']
df['est_gross_annual_rent'] = df['est_gross_monthly_rent'] * 12

# Apply vacancy loss
df['vacancy_loss'] = (df['est_gross_annual_rent'] * VACANCY_RATE).round(2)
df['effective_gross_income'] = (df['est_gross_annual_rent'] - df['vacancy_loss']).round(2)

# Property tax estimate
df['est_annual_taxes'] = (df['price'] * COOK_COUNTY_TAX_RATE).round(2)

# Gross Rent Multiplier
df['grm'] = (df['price'] / df['est_gross_annual_rent']).round(2)

# Summary
print("Data Sources:")
print("  Rents: Zillow Rental Market Trends, Evanston IL, June 3 2026")
print("  Vacancy: U.S. Census Bureau CPS/HVS Table 4, 2026 - Chicago Metro: 5.7%")
print("  Tax Rate: Cook County Assessor 1.8% (needs verification)")

print("\nMaster DataFrame Summary:")
print(df[['address', 'price', 'beds', 'est_units',
          'est_gross_annual_rent', 'vacancy_loss',
          'effective_gross_income', 'est_annual_taxes', 'grm']].to_string())

# Save master DataFrame
df.to_csv('data/listings_with_rents.csv', index=False)
print("\nSaved to data/listings_with_rents.csv")