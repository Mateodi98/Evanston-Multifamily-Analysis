# Research Hypothesis

## Question
In the Evanston real estate market, which type of multifamily property 
(duplex, 3-flat, or 4-unit) offers the best investment outcome for an 
owner-occupied buyer under current market conditions?

## Hypothesis
A 3-flat priced at or below $800,000 with 15% down payment at a 6.8% 
interest rate will generate a superior combination of Break-Even Ratio, 
DSCR, and 5-year total ROI compared to a duplex (20% down, max $620,000) 
or 4-unit property (15% down, max $800,000) in the Evanston market.

## Null Hypothesis
There is no statistically significant difference in investment performance 
(Break-Even Ratio, DSCR, cap rate, 5-year total ROI) between duplex, 
3-flat, and 4-unit multifamily properties in the Evanston market at 
current prices and financing conditions.

## Key Variables
- **Independent:** Property type (duplex, 3-flat, 4-unit), purchase price,
  down payment percentage
- **Dependent:** Break-Even Ratio, DSCR, Cash-on-Cash Return, Cap Rate,
  5-year Total ROI
- **Control:** Market rents (Zillow June 2026), Vacancy rate (Census 5.7%),
  Interest rate (6.8%)

## Important Note on Fannie Mae Guidelines
Fannie Mae does not apply DSCR to 2-4 unit owner-occupied residential 
mortgages. Instead it uses a Break-Even Ratio requiring a minimum of 1.0x. 
DSCR (1.25x minimum) applies only to commercial multifamily properties 
with 5+ units. This project uses Break-Even Ratio as the primary 
qualification metric and DSCR as a supplementary investment viability metric.

## Financing Assumptions by Property Type
- **Duplex:** Max $620,000 | 20% down | 6.8% rate | 30yr fixed
- **3-flat:** Max $800,000 | 15% down | 6.8% rate | 30yr fixed
- **4-unit:** Max $800,000 | 15% down | 6.8% rate | 30yr fixed

## Success Criteria
A property is considered viable if it meets ALL of the following:
- Break-Even Ratio ≥ 1.0x (Fannie Mae 2-4 unit owner-occupied guidelines)
- DSCR ≥ 1.0x (supplementary investment viability measure)
- LTV ≤ 85% (Fannie Mae conventional conforming — 3 and 4 unit)
- Cap Rate ≥ 5.6% (CBRE U.S. Cap Rate Survey H2 2025, Chicago metro Q1 2026)

## Data Sources
- Sales data: Redfin (49 Evanston multifamily transactions, last 12 months)
- Market rents: Zillow Rental Market Trends, Evanston IL, June 3 2026
- Vacancy rate: U.S. Census Bureau CPS/HVS Table 4, 2026 (5.7% Chicago metro)
- Cap rate benchmark: CBRE U.S. Cap Rate Survey H2 2025 (5.6% Chicago metro Q1 2026)
- Evanston cap rate: Cook County Assessor Evanston Township Commercial Valuations (7.93%)
- Appreciation rates: Zillow HVI 2026 (3.5% conservative),
  Evanston Now Feb 2026 (5.8% moderate)
- Pro forma structure: Coach Carson Simple Rental Calculator (coachcarson.com)

## Dataset Summary
| Property Type | Count | Avg Price | Min Price | Max Price |
|---|---|---|---|---|
| Duplex (2 units) | 12 | $498,167 | $350,000 | $640,000 |
| 3-flat (3 units) | 20 | $691,725 | $299,000 | $1,500,000 |
| 4-unit (4 units) | 18 | $837,950 | $567,825 | $1,300,000 |
| **Total** | **49** | | | |

## Expected Outcome
Based on dataset analysis and EDA findings (median GRM 8.01):
- 3-flats have the largest sample (20 properties) and widest price range
- We expect 3-flats to show the best balance of cash flow and appreciation
  potential given their price range and unit count
- Duplexes will likely show stronger per-unit metrics but lower absolute
  returns due to fewer units
- 4-units will likely show the highest absolute cash flow but require
  the most capital and carry the most management complexity