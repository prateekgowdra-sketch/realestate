from pathlib import Path

import pandas as pd
import pytest

from src.scoring import build_rankings, normalize_column, validate_columns


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BAY_AREA_DATA = PROJECT_ROOT / "data" / "bay_area_starter_metrics.csv"


def test_bay_area_rankings_are_sorted_highest_to_lowest():
    rankings = build_rankings(BAY_AREA_DATA)

    scores = rankings["opportunity_score"].tolist()

    assert scores == sorted(scores, reverse=True)


def test_opportunity_scores_stay_between_0_and_100():
    rankings = build_rankings(BAY_AREA_DATA)

    assert rankings["opportunity_score"].between(0, 100).all()


def test_rank_column_starts_at_one_and_has_no_gaps():
    rankings = build_rankings(BAY_AREA_DATA)

    assert rankings["rank"].tolist() == list(range(1, len(rankings) + 1))


def test_higher_is_better_normalization():
    scores = normalize_column(pd.Series([10, 20, 30]), higher_is_better=True)

    assert scores.tolist() == [0, 50, 100]


def test_lower_is_better_normalization():
    scores = normalize_column(pd.Series([10, 20, 30]), higher_is_better=False)

    assert scores.tolist() == [100, 50, 0]


def test_constant_column_normalizes_to_neutral_score():
    scores = normalize_column(pd.Series([5, 5, 5]), higher_is_better=True)

    assert scores.tolist() == [50, 50, 50]


def test_missing_required_columns_raise_clear_error():
    incomplete_df = pd.DataFrame(
        {
            "zip_code": ["95051"],
            "city": ["Santa Clara"],
            "state": ["CA"],
        }
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_columns(incomplete_df)
