from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STARTER_PATH = PROJECT_ROOT / "data" / "bay_area_starter_metrics.csv"
CENSUS_PATH = PROJECT_ROOT / "data" / "processed" / "bay_area_census_metrics.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "bay_area_scoring_metrics.csv"

REAL_CENSUS_COLUMNS = [
    "income_growth",
    "population_growth",
]

EXTRA_CENSUS_CONTEXT_COLUMNS = [
    "population_2018",
    "population_2023",
    "median_income_2018",
    "median_income_2023",
]


def merge_metrics(
    starter_path=STARTER_PATH,
    census_path=CENSUS_PATH,
    output_path=OUTPUT_PATH,
):
    starter_df = pd.read_csv(starter_path, dtype={"zip_code": str})
    census_df = pd.read_csv(census_path, dtype={"zip_code": str})

    merge_columns = ["zip_code", *REAL_CENSUS_COLUMNS, *EXTRA_CENSUS_CONTEXT_COLUMNS]
    merged_df = starter_df.merge(
        census_df[merge_columns],
        on="zip_code",
        how="left",
        suffixes=("_starter", "_census"),
    )

    for column in REAL_CENSUS_COLUMNS:
        census_column = f"{column}_census"
        starter_column = f"{column}_starter"

        merged_df[column] = merged_df[census_column].fillna(merged_df[starter_column])
        merged_df = merged_df.drop(columns=[starter_column, census_column])

    missing_census = merged_df[REAL_CENSUS_COLUMNS].isna().any(axis=1)
    if missing_census.any():
        missing_zips = ", ".join(merged_df.loc[missing_census, "zip_code"])
        raise ValueError(f"Missing Census values for ZIP codes: {missing_zips}")

    ordered_columns = [
        "zip_code",
        "city",
        "state",
        "home_price_growth",
        "rent_to_price_ratio",
        "job_growth",
        "income_growth",
        "population_growth",
        "school_score_change",
        "vacancy_rate",
        "crime_risk",
        "climate_risk",
        *EXTRA_CENSUS_CONTEXT_COLUMNS,
    ]

    merged_df = merged_df[ordered_columns]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(output_path, index=False)

    return merged_df


def main():
    merged_df = merge_metrics()
    print(f"Wrote {len(merged_df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
