import json
import os
import re
import sys

import pandas as pd

from dashboard_data import load_sales, segment_comparison, totals


def compare_months(month, breakdown, data=None):
    """Compare YYYY-MM with the previous month, broken down by category, country or product."""
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        raise ValueError("month must use YYYY-MM")
    if breakdown not in {"category", "country", "product"}:
        raise ValueError("breakdown must be category, country or product")

    data = load_sales("CSV") if data is None else data
    selected = pd.Period(month, freq="M")
    months = data.sale_date.dt.to_period("M")
    current = data[months == selected]
    previous = data[months == selected - 1]
    if current.empty or previous.empty:
        raise ValueError("Sales are missing for the selected or previous month")

    current_revenue = totals(current)["revenue"]
    previous_revenue = totals(previous)["revenue"]
    segments = segment_comparison(current, previous, breakdown)
    segments = segments.reindex(segments["Change (EUR)"].abs().sort_values(ascending=False).index).head(10)
    return {
        "current_month": str(selected),
        "previous_month": str(selected - 1),
        "dataset_first_date": str(data.sale_date.min().date()),
        "dataset_last_date": str(data.sale_date.max().date()),
        "current_revenue_eur": round(current_revenue, 2),
        "previous_revenue_eur": round(previous_revenue, 2),
        "change_eur": round(current_revenue - previous_revenue, 2),
        "change_percent": round((current_revenue / previous_revenue - 1) * 100, 2) if previous_revenue else None,
        "segments": [
            {
                breakdown: name,
                "current_revenue_eur": float(row["Current revenue (EUR)"]),
                "previous_revenue_eur": float(row["Previous revenue (EUR)"]),
                "change_eur": float(row["Change (EUR)"]),
            }
            for name, row in segments.iterrows()
        ],
    }


def ask_sales(question, data, source):
    from dotenv import load_dotenv
    from agents import Agent, Runner, function_tool

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not configured")

    @function_tool
    def compare_sales(month: str, breakdown: str) -> str:
        """Compare a YYYY-MM month with the previous month by category, country or product."""
        try:
            return json.dumps(compare_months(month, breakdown, data), ensure_ascii=False)
        except ValueError as error:
            return json.dumps({"error": str(error)})

    agent = Agent(
        name="Sales analyst",
        model="gpt-5.6-luna",
        instructions=(
            "Answer in the user's language. Use compare_sales for sales questions; call it again "
            "with another breakdown when needed. Use only tool data for numbers. Describe which "
            f"segments contributed to a change, not an unproven cause. Data source: {source}. "
            "A date range alone does not prove that all transactions are present. "
            "State when the dataset date range does not cover a compared month. "
            "Ask for the year and month if the question does not specify them."
        ),
        tools=[compare_sales],
    )
    return Runner.run_sync(agent, question, max_turns=6).final_output


def main():
    question = " ".join(sys.argv[1:]) or input("Kérdés: ")
    print("Helyi sales_data_v2 CSV alapján:\n" + ask_sales(question, load_sales("CSV"), "local sample CSV"))


if __name__ == "__main__":
    main()
