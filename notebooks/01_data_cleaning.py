import pandas as pd
import numpy as np

# Load raw Redfin data
df = pd.read_csv('data/redfin_2026-06-05-12-38-16.csv', skiprows=[1])

# Keep only the columns we need for underwriting
columns_to_keep = [
    'ADDRESS', 'CITY', 'ZIP OR POSTAL CODE', 'PRICE', 'BEDS', 'BATHS',
    'SQUARE FEET', 'LOT SIZE', 'YEAR BUILT', 'DAYS ON MARKET',
    '$/SQUARE FEET', 'PROPERTY TYPE', 'SOLD DATE', 'LATITUDE', 'LONGITUDE'
]
df = df[columns_to_keep]

# Rename columns for easier use
df.columns = [
    'address', 'city', 'zip', 'price', 'beds', 'baths',
    'sqft', 'lot_size', 'year_built', 'days_on_market',
    'price_per_sqft', 'property_type', 'sold_date', 'latitude', 'longitude'
]

# Filter to Evanston only
df = df[df['city'] == 'Evanston']

# Drop rows missing critical fields
df = df.dropna(subset=['price', 'beds', 'baths'])

# Reset index
df = df.reset_index(drop=True)

# Summary
print("Clean dataset shape:", df.shape)
print("\nMissing values:")
print(df.isnull().sum())
print("\nPrice range: ${:,.0f} - ${:,.0f}".format(df['price'].min(), df['price'].max()))
print("Avg price: ${:,.0f}".format(df['price'].mean()))
print("\nSample:")
print(df[['address', 'price', 'beds', 'baths', 'sqft', 'year_built']].head(10).to_string())

# Save clean data
df.to_csv('data/clean_listings.csv', index=False)
print("\nSaved to data/clean_listings.csv")
