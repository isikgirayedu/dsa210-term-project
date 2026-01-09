#!/usr/bin/env python3
"""Fetch monthly USD/TRY and food HICP indices for Turkey."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUT = BASE_DIR / "data" / "food_inflation_data.csv"

EVDS_SERIES = "TP.DK.USD.A.YTL"
EVDS_FREQUENCY = "5"  # monthly
EVDS_AGGREGATION = "avg"  # monthly average
FRED_SERIES = {
    "Bread_Index": "CP0111TRM086NEST",
    "Meat_Index": "CP0112TRM086NEST",
    "Milk_Index": "CP0114TRM086NEST",
}
FRED_USD_SERIES = "CCUSMA02TRM618N"


def fetch_evds_usd_try(
    api_key: str,
    start_date: str,
    end_date: str,
    series: str,
    frequency: str = EVDS_FREQUENCY,
    aggregation: str = EVDS_AGGREGATION,
) -> pd.DataFrame:
    params = {
        "series": series,
        "startDate": start_date,
        "endDate": end_date,
        "type": "json",
        "frequency": frequency,
        "aggregation_types": aggregation,
    }
    urls = [
        ("https://evds2.tcmb.gov.tr/service/evds", params),
        ("https://evds2.tcmb.gov.tr/service/evds/", params),
        (
            "https://evds2.tcmb.gov.tr/service/evds/series="
            f"{series}&startDate={start_date}&endDate={end_date}&type=json",
            None,
        ),
    ]

    last_status = None
    headers = {"User-Agent": "Mozilla/5.0", "key": api_key}
    for url, query in urls:
        resp = requests.get(url, params=query, headers=headers, timeout=30)
        last_status = resp.status_code
        if resp.status_code == 404:
            continue
        if resp.status_code == 403:
            raise ValueError("EVDS returned 403. Check that the API key is active and correct.")
        if resp.status_code != 200:
            raise ValueError(f"EVDS request failed with status {resp.status_code}.")
        payload = resp.json()
        break
    else:
        raise ValueError(f"EVDS endpoint not found (last status {last_status}).")
    items = payload.get("items") or payload.get("Items") or []
    if not items:
        raise ValueError("EVDS response did not include items.")

    df = pd.DataFrame(items)
    date_col = "Tarih" if "Tarih" in df.columns else "Date"
    series_key_candidates = [series, series.replace(".", "_")]
    series_key = None
    for candidate in series_key_candidates:
        if candidate in df.columns:
            series_key = candidate
            break
    if series_key is None:
        raise ValueError(f"Series column not found in EVDS response: {series}")

    df["Date"] = pd.to_datetime(df[date_col], dayfirst=True)
    df["Date"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    df["USD_TRY"] = pd.to_numeric(df[series_key], errors="coerce")
    df = df[["Date", "USD_TRY"]]

    agg_map = {
        "avg": "mean",
        "mean": "mean",
        "first": "first",
        "last": "last",
        "min": "min",
        "max": "max",
        "sum": "sum",
    }
    agg = agg_map.get(aggregation.lower(), "mean")
    df = df.groupby("Date", as_index=False)["USD_TRY"].agg(agg)
    return df


def fetch_fred_series(api_key: str, series_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "observation_start": start_date,
        "observation_end": end_date,
        "frequency": "m",
        "file_type": "json",
    }
    resp = requests.get(url, params=params, timeout=30)
    if resp.status_code != 200:
        raise ValueError(f"FRED request failed with status {resp.status_code}.")
    payload = resp.json()
    obs = payload.get("observations", [])
    if not obs:
        raise ValueError(f"FRED response empty for {series_id}.")

    df = pd.DataFrame(obs)
    df["Date"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()
    df[series_id] = pd.to_numeric(df["value"], errors="coerce")
    return df[["Date", series_id]]


def build_base_dates(start_date: str, end_date: str) -> pd.DataFrame:
    dates = pd.date_range(start=start_date, end=end_date, freq="MS")
    return pd.DataFrame({"Date": dates})


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch monthly USD/TRY and food HICP indices.")
    parser.add_argument("--start", default="2019-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default="2024-12-31", help="End date (YYYY-MM-DD)")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output CSV path")
    parser.add_argument("--evds-key", default=os.getenv("EVDS_API_KEY"), help="EVDS API key")
    parser.add_argument("--fred-key", default=os.getenv("FRED_API_KEY"), help="FRED API key")
    parser.add_argument(
        "--usd-source",
        default="evds",
        choices=["evds", "fred"],
        help="Source for USD/TRY (evds or fred)",
    )
    parser.add_argument(
        "--fred-usd-series",
        default=FRED_USD_SERIES,
        help="FRED series id for USD/TRY (monthly average)",
    )
    parser.add_argument(
        "--evds-frequency",
        default=EVDS_FREQUENCY,
        help="EVDS frequency code (5=monthly)",
    )
    parser.add_argument(
        "--evds-aggregation",
        default=EVDS_AGGREGATION,
        help="EVDS aggregation type (avg, last, first, etc.)",
    )
    args = parser.parse_args()

    if not args.fred_key:
        raise ValueError("Missing FRED API key. Set --fred-key or FRED_API_KEY.")
    if args.usd_source == "evds" and not args.evds_key:
        raise ValueError("Missing EVDS API key. Set --evds-key or EVDS_API_KEY.")

    start_iso = pd.to_datetime(args.start).strftime("%Y-%m-%d")
    end_iso = pd.to_datetime(args.end).strftime("%Y-%m-%d")
    start_evds = pd.to_datetime(args.start).strftime("%d-%m-%Y")
    end_evds = pd.to_datetime(args.end).strftime("%d-%m-%Y")

    base = build_base_dates(start_iso, end_iso)

    if args.usd_source == "evds":
        usd = fetch_evds_usd_try(
            args.evds_key,
            start_evds,
            end_evds,
            EVDS_SERIES,
            frequency=args.evds_frequency,
            aggregation=args.evds_aggregation,
        )
    else:
        usd = fetch_fred_series(args.fred_key, args.fred_usd_series, start_iso, end_iso)
        usd = usd.rename(columns={args.fred_usd_series: "USD_TRY"})
    df = base.merge(usd, on="Date", how="left")

    for out_col, series_id in FRED_SERIES.items():
        fred_df = fetch_fred_series(args.fred_key, series_id, start_iso, end_iso)
        fred_df = fred_df.rename(columns={series_id: out_col})
        df = df.merge(fred_df, on="Date", how="left")

    df = df.sort_values("Date").reset_index(drop=True)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    missing = df.isna().sum()
    if missing.any():
        print("Missing values detected:")
        print(missing[missing > 0])

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()
