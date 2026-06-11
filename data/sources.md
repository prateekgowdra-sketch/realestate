# Data Sources

This file documents where each metric in the Neighborhood Opportunity Score should come from.

## Current Status

The current Bay Area dataset is a starter dataset used to test the scoring engine. The goal is to replace starter values with sourced public or licensed data.

## Metrics

| Metric | Current Column | Planned Source | Notes |
|---|---|---|---|
| Population growth | `population_growth` | U.S. Census ACS 5-year | Compare population by ZCTA across years |
| Income growth | `income_growth` | U.S. Census ACS 5-year | Compare median household income by ZCTA across years |
| Home price growth | `home_price_growth` | Zillow, Redfin, FHFA, or public housing datasets | Use historical median sale price or home value index |
| Rental ROI | `rent_to_price_ratio` | Rent data + home price data | Monthly rent divided by estimated home price |
| Job growth | `job_growth` | BLS, Census, local economic reports | Ideally by county/metro, later employer-proximity based |
| School improvement | `school_score_change` | CA Department of Education or school rating datasets | Track school performance changes over time |
| Vacancy risk | `vacancy_rate` | U.S. Census ACS 5-year | Lower vacancy usually means stronger demand |
| Crime risk | `crime_risk` | City/county crime data portals | Normalize incidents by population |
| Climate risk | `climate_risk` | FEMA National Risk Index, NOAA, CalFire | Bay Area risk may include wildfire, flood, heat, earthquake |

## Methodology Plan

1. Collect raw data from public or licensed sources.
2. Store original datasets in `data/raw/`.
3. Clean and standardize datasets into ZIP/ZCTA-level metrics.
4. Save cleaned datasets in `data/processed/`.
5. Feed processed data into `src/scoring.py`.
6. Use the scoring engine to calculate the Neighborhood Opportunity Score.
7. Later, train a machine learning model to predict future appreciation using historical data.

## Limitations

- Census ZCTAs are ZIP-like statistical areas, not exact USPS ZIP codes.
- Some data sources may only be available at the city, county, or metro level.
- Starter values should not be treated as investment advice.
- The scoring model is designed for comparison and research, not guaranteed prediction.
