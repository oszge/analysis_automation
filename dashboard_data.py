"""Read-only data preparation for the Streamlit dashboard (no AI calls)."""

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
REQUIRED_COLUMNS = ["sale_date", "product", "category", "country", "quantity", "revenue"]


def prepare_sales(raw):
    missing = set(REQUIRED_COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
    data = raw[REQUIRED_COLUMNS].copy()
    data["sale_date"] = pd.to_datetime(data["sale_date"], errors="coerce").dt.normalize()
    for column in ("revenue", "quantity"):
        data[column] = pd.to_numeric(data[column], errors="coerce")
        if not np.isfinite(data[column]).all():
            raise ValueError(f"Invalid numeric value in column {column}.")
    if data.isna().any().any():
        raise ValueError("The data contains missing or invalid values.")
    if (data["quantity"] % 1 != 0).any():
        raise ValueError("Quantity must be a whole number.")
    data["currency"] = "EUR"
    return data.sort_values("sale_date").reset_index(drop=True)


def load_sales(source):
    if source == "CSV":
        return prepare_sales(pd.read_csv(BASE_DIR / "sales_data"))
    # Import only on explicit database selection; never import the pipeline.
    from database import load_sales as load_database_sales

    return prepare_sales(load_database_sales())


def totals(data):
    return {
        "revenue": float(data["revenue"].sum()),
        "quantity": int(data["quantity"].sum()),
        "transactions": len(data),
    }


def period_comparison(data, anchor, period):
    """Match the existing pipeline: trailing 7 days or month-to-date vs last month."""
    anchor = pd.Timestamp(anchor).normalize()
    start = anchor - pd.Timedelta(days=6) if period == "weekly" else anchor.replace(day=1)
    previous_end = start - pd.Timedelta(days=1)
    previous_start = (
        previous_end - pd.Timedelta(days=6)
        if period == "weekly" else previous_end.replace(day=1)
    )
    current = data[data.sale_date.between(start, anchor)]
    previous = data[data.sale_date.between(previous_start, previous_end)]
    return current, previous, (start, anchor, previous_start, previous_end)


def segment_comparison(current, previous, dimension):
    result = pd.concat([
        current.groupby(dimension).revenue.sum().rename("Current revenue (EUR)"),
        previous.groupby(dimension).revenue.sum().rename("Previous revenue (EUR)"),
    ], axis=1).fillna(0)
    result["Change (EUR)"] = result["Current revenue (EUR)"] - result["Previous revenue (EUR)"]
    result["Change (%)"] = (
        result["Change (EUR)"] / result["Previous revenue (EUR)"].replace(0, np.nan) * 100
    )
    return result.round(2).sort_values("Current revenue (EUR)", ascending=False)
