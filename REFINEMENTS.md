# Known Limitations & Planned Refinements
## Data Sources

### Vacancy Rate
- **Rate Used:** 5.7%
- **Source:** U.S. Census Bureau, Current Population Survey/Housing Vacancy Survey (CPS/HVS)
- **Table:** Table 4 - Rental Vacancy Rates for the 75 Largest Metropolitan Statistical Areas: 2026
- **Geography:** Chicago-Naperville-Elgin, IL-IN Metro
- **Last Revised:** April 28, 2026
- **URL:** https://www.census.gov/housing/hvs/data/rates.html

### Market Rents
- **Source:** Zillow Rental Market Trends
- **Geography:** Evanston, IL
- **Last Updated:** June 3, 2026
- **URL:** https://www.zillow.com/rental-manager/market-trends/evanston-il

### Property Tax Rate
- **Rate Used:** 1.8% of market value
- **Source:** TO BE VERIFIED - Cook County Assessor
- **URL:** https://www.cookcountyassessor.com
- **Status:** ⚠️ Needs verification against actual tax bills
## Data Limitations

### 1. Unit Count Estimation
**Issue:** Unit count is estimated from total bedroom count using a heuristic rule
rather than actual MLS unit configuration data.
**Example:** 827 Sherman Ave is a 3-unit building with 2BR/2BA + 2BR/2BA + 1BR/1BA
but our model treats all units as 2BR.
**Impact:** Rent estimates may be overstated or understated depending on actual unit mix.
**Fix:** Manually verify unit configurations against individual MLS listings and build
a unit-level rent roll for each property.

### 2. Bathroom Count Not Reflected in Rent Estimates
**Issue:** Rent estimates are based solely on bedroom count. Properties with more
bathrooms per unit typically command higher rents.
**Example:** A 2BR/2BA unit rents for more than a 2BR/1BA unit in the Evanston market.
**Impact:** Rent may be underestimated for higher-end units and overestimated for
lower-end units.
**Fix:** Build a regression model using Evanston active rental listings with both
beds and baths as features to produce more accurate per-unit rent estimates.

### 3. Mixed Unit Configuration Properties
**Issue:** Properties with non-uniform unit layouts (e.g. two 2BR units + one 1BR unit)
are underwritten as if all units are identical.
**Impact:** Gross rental income estimates are less accurate for mixed-configuration
buildings.
**Fix:** Collect unit-level rent rolls from sellers or listing agents before
making final underwriting decisions.

### 4. 4BR+ Rent Estimate Reliability
**Issue:** Zillow's 4BR+ average rent for Evanston ($5,404) is based on only 44
active listings and shows an unusually high year-over-year change (+$3,402),
suggesting the sample is skewed by luxury listings.
**Impact:** Properties with 4+ bedrooms per unit may have overstated rent estimates.
**Fix:** Cross-reference with additional sources such as Apartments.com or direct
comparable rental analysis for large-unit properties.

### 5. Redfin Data Does Not Include Days on Market for Sold Listings
**Issue:** The days on market column is empty for all sold properties in the Redfin
export, limiting our ability to analyze liquidity and demand velocity.
**Fix:** Pull days on market from individual MLS listing pages or use a paid data
provider such as CoStar.

## Model Limitations

### 6. Operating Expense Ratios Are Estimates
**Issue:** Insurance, maintenance, and capital expenditure reserves are estimated
as a percentage of gross rent rather than actual property-level figures.
**Fix:** Obtain actual insurance quotes and historical expense statements from
sellers for properties under serious consideration.

### 7. Interest Rate Assumption Is Static
**Issue:** The underwriting model uses a single interest rate assumption.
**Fix:** The sensitivity analysis matrix partially addresses this but a full
Monte Carlo simulation across rate scenarios would be more robust.

## Planned Features
- [ ] Unit-level rent roll input for mixed-configuration properties
- [ ] Beds + baths regression model for rent estimation
- [ ] Integration with Cook County Assessor API for actual tax bills
- [ ] Days on market analysis using supplemental data source
- [ ] Monte Carlo simulation for interest rate sensitivity
- [ ] Manual verification of unit counts for the 21 target properties 
      (≤ $620,000) against individual Redfin/MLS listings to improve 
      rent estimate accuracy. Priority: top 5 deals by Break-Even Ratio.
      Estimated impact: up to $448/month cash flow variance per property.
      Update 04_underwriting_engine.py after manually entering the number
      of units per property, so the gross income is adjusted and the cashflow
      is accurate. 