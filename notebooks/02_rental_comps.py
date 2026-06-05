# ── KNOWN LIMITATIONS ───────────────────────────────────────────────────
# Unit count is estimated from total bedroom count using a heuristic rule.
# Actual unit configurations may differ (e.g. a 6BR property could be a
# 2-flat with 3BR/unit or a 3-flat with 2BR/unit). Manual verification of
# unit counts against MLS listings is recommended before making investment
# decisions. This is flagged as a refinement item for future versions.
# ────────────────────────────────────────────────────────────────────────

import pandas as pd
import numpy as np

# ── Evanston Market Rents ────────────────────────────────────────────────
# Source: Zillow Rental Market Trends - Evanston, IL
# Last updated: June 3, 2026
# Property type: All property types

EVANSTON_MARKET_RENTS = {
    1: 1750,   # 1BR average: $1,750
    2: 2198,   # 2BR average: $2,198
    3: 3195,   # 3BR average: $3,195
    4: 5404,   # 4BR+ average: $5,404 (note: small sample, 44 listings)
}

# Cook County effective tax rate for Evanston
# Source: Cook County Assessor - residential properties assessed at 10% of market value
COOK_COUNTY_TAX_RATE = 0.018

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

# Property tax estimate
df['est_annual_taxes'] = df['price'] * COOK_COUNTY_TAX_RATE

# Gross Rent Multiplier
df['grm'] = (df['price'] / df['est_gross_annual_rent']).round(2)

print("Evanston Market Rents Used (Source: Zillow, June 2026):")
for beds, rent in EVANSTON_MARKET_RENTS.items():
    print(f"  {beds}BR: ${rent:,}/month")

print("\nListings with Rental Estimates:")
print(df[['address', 'price', 'beds', 'est_units',
          'est_rent_per_unit', 'est_gross_annual_rent', 'grm']].to_string())

# Save
df.to_csv('data/listings_with_rents.csv', index=False)
print("\nSaved to data/listings_with_rents.csv")