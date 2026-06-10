from pathlib import Path
import argparse

import pandas as pd


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_zip_metrics.csv"


HIGHER_IS_BETTER = [
    "home_price_growth",
    "rent_to_price_ratio",
    "job_growth",
    "income_growth",
    "population_growth",
    "school_score_change",
]

LOWER_IS_BETTER = [
    "vacancy_rate",
    "crime_risk",
    "climate_risk",
]


WEIGHTS = {
    "housing_momentum_score": 0.25,
    "rental_roi_score": 0.20,
    "economic_growth_score": 0.20,
    "demographic_momentum_score": 0.10,
    "school_improvement_score": 0.10,
    "risk_score": 0.15,
}


def normalize_column(series, higher_is_better=True):
    """Convert a column into a 0-100 score."""
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series([50] * len(series), index=series.index)

    normalized = (series - minimum) / (maximum - minimum) * 100

    if not higher_is_better:
        normalized = 100 - normalized

    return normalized


def add_normalized_columns(df):
    scored_df = df.copy()

    for column in HIGHER_IS_BETTER:
        scored_df[f"{column}_score"] = normalize_column(scored_df[column], True)

    for column in LOWER_IS_BETTER:
        scored_df[f"{column}_score"] = normalize_column(scored_df[column], False)

    return scored_df


def add_category_scores(df):
    scored_df = df.copy()

    scored_df["housing_momentum_score"] = scored_df["home_price_growth_score"]
    scored_df["rental_roi_score"] = scored_df["rent_to_price_ratio_score"]
    scored_df["economic_growth_score"] = (
        scored_df["job_growth_score"] + scored_df["income_growth_score"]
    ) / 2
    scored_df["demographic_momentum_score"] = scored_df["population_growth_score"]
    scored_df["school_improvement_score"] = scored_df["school_score_change_score"]
    scored_df["risk_score"] = (
        scored_df["vacancy_rate_score"]
        + scored_df["crime_risk_score"]
        + scored_df["climate_risk_score"]
    ) / 3

    return scored_df


def add_opportunity_score(df):
    scored_df = df.copy()
    scored_df["opportunity_score"] = 0

    for column, weight in WEIGHTS.items():
        scored_df["opportunity_score"] += scored_df[column] * weight

    scored_df["opportunity_score"] = scored_df["opportunity_score"].round(1)
    return scored_df


def get_best_for(row):
    strengths = {
        "Long-term appreciation": row["housing_momentum_score"],
        "Rental ROI": row["rental_roi_score"],
        "Job and income growth": row["economic_growth_score"],
        "Families": (row["school_improvement_score"] + row["risk_score"]) / 2,
        "Balanced growth": row["opportunity_score"],
    }

    return max(strengths, key=strengths.get)


def build_rankings(data_path=DATA_PATH):
    df = pd.read_csv(data_path)
    df = add_normalized_columns(df)
    df = add_category_scores(df)
    df = add_opportunity_score(df)
    df["best_for"] = df.apply(get_best_for, axis=1)

    rankings = df.sort_values("opportunity_score", ascending=False).reset_index(drop=True)
    rankings.insert(0, "rank", rankings.index + 1)

    return rankings


def parse_args():
    parser = argparse.ArgumentParser(
        description="Rank ZIP codes by Neighborhood Opportunity Score."
    )
    parser.add_argument(
        "data_path",
        nargs="?",
        default=DATA_PATH,
        help="Path to a CSV file with ZIP code metrics.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    rankings = build_rankings(args.data_path)

    display_columns = [
        "rank",
        "zip_code",
        "city",
        "state",
        "opportunity_score",
        "best_for",
    ]

    print(f"\nNeighborhood Opportunity Rankings: {args.data_path}\n")
    print(rankings[display_columns].to_string(index=False))


if __name__ == "__main__":
    main()
