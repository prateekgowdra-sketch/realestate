from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen
import csv
import json
import os


BASE_URL = "https://api.census.gov/data/{year}/acs/acs5"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "bay_area_census_metrics.csv"

START_YEAR = 2018
END_YEAR = 2023

VARIABLES = {
    "B01003_001E": "population",
    "B19013_001E": "median_household_income",
}

BAY_AREA_ZCTAS = {
    "95051": ("Santa Clara", "CA"),
    "94086": ("Sunnyvale", "CA"),
    "95112": ("San Jose", "CA"),
    "94538": ("Fremont", "CA"),
    "94403": ("San Mateo", "CA"),
    "94608": ("Oakland", "CA"),
    "94063": ("Redwood City", "CA"),
    "94110": ("San Francisco", "CA"),
    "94536": ("Fremont", "CA"),
    "94704": ("Berkeley", "CA"),
}


def fetch_census_year(year):
    params = {
        "get": f"NAME,{','.join(VARIABLES)}",
        "for": "zip code tabulation area:*",
    }
    api_key = os.getenv("CENSUS_API_KEY")
    if api_key:
        params["key"] = api_key

    url = f"{BASE_URL.format(year=year)}?{urlencode(params)}"

    try:
        with urlopen(url, timeout=30) as response:
            body = response.read().decode("utf-8")
    except HTTPError as error:
        body = error.read().decode("utf-8")
        raise RuntimeError(f"Census API request failed for {year}: {body}") from error
    except URLError as error:
        raise RuntimeError(f"Could not reach Census API for {year}: {error}") from error

    if "missing_key" in response.url or "Missing Key" in body:
        raise RuntimeError(
            "Census API key required. Set CENSUS_API_KEY before running this script."
        )

    try:
        rows = json.loads(body)
    except json.JSONDecodeError as error:
        preview = body[:300].replace("\n", " ")
        raise RuntimeError(
            f"Census API returned an unexpected response for {year}: {preview}"
        ) from error

    header = rows[0]
    return [dict(zip(header, row)) for row in rows[1:]]


def to_number(value):
    if value in (None, "", "-666666666", "-222222222", "-999999999"):
        return None
    return float(value)


def percent_change(start_value, end_value):
    if start_value in (None, 0) or end_value is None:
        return None
    return round((end_value - start_value) / start_value * 100, 2)


def build_processed_rows():
    start_rows = {
        row["zip code tabulation area"]: row for row in fetch_census_year(START_YEAR)
    }
    end_rows = {
        row["zip code tabulation area"]: row for row in fetch_census_year(END_YEAR)
    }

    processed_rows = []

    for zcta, (city, state) in BAY_AREA_ZCTAS.items():
        start = start_rows.get(zcta, {})
        end = end_rows.get(zcta, {})

        start_population = to_number(start.get("B01003_001E"))
        end_population = to_number(end.get("B01003_001E"))
        start_income = to_number(start.get("B19013_001E"))
        end_income = to_number(end.get("B19013_001E"))

        processed_rows.append(
            {
                "zip_code": zcta,
                "city": city,
                "state": state,
                "population_2018": start_population,
                "population_2023": end_population,
                "population_growth": percent_change(start_population, end_population),
                "median_income_2018": start_income,
                "median_income_2023": end_income,
                "income_growth": percent_change(start_income, end_income),
            }
        )

    return processed_rows


def write_csv(rows):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "zip_code",
        "city",
        "state",
        "population_2018",
        "population_2023",
        "population_growth",
        "median_income_2018",
        "median_income_2023",
        "income_growth",
    ]

    with OUTPUT_PATH.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    try:
        rows = build_processed_rows()
    except RuntimeError as error:
        print(f"Error: {error}")
        print("Get a free Census API key at https://api.census.gov/data/key_signup.html")
        raise SystemExit(1)

    write_csv(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
