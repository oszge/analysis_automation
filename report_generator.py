from pathlib import Path


def generate_report(business_analysis, analysis_data):
    overall = analysis_data["overall"]
    weekly = analysis_data["weekly"]
    monthly = analysis_data["monthly"]

    report = f"""# Business Intelligence Report

## Executive Summary

{business_analysis.executive_summary}

## Overall Performance

- Total revenue: {overall["total_revenue"]:,.2f}
- Total units sold: {overall["total_units"]}
- Total transactions: {overall["total_transactions"]}
- Best category: {overall["best_category"]}
- Best country: {overall["best_country"]}
- Best product: {overall["best_product"]}

## Monthly Performance

**Period:** {monthly["period_start"]} – {monthly["period_end"]}

- Revenue: {monthly["current_revenue"]:,.2f}
- Previous revenue: {monthly["previous_revenue"]:,.2f}
- Revenue change: {monthly["revenue_change_value"]:+,.2f} ({monthly["revenue_change_percent"]:+.2f}%)
- Units sold: {monthly["current_units"]}
- Previous units sold: {monthly["previous_units"]}
- Transactions: {monthly["current_transactions"]}
- Previous transactions: {monthly["previous_transactions"]}
- Best category: {monthly["best_category"]} ({monthly["best_category_revenue"]:,.2f})
- Best country: {monthly["best_country"]} ({monthly["best_country_revenue"]:,.2f})

## Weekly Performance

**Period:** {weekly["period_start"]} – {weekly["period_end"]}

- Revenue: {weekly["current_revenue"]:,.2f}
- Previous revenue: {weekly["previous_revenue"]:,.2f}
- Revenue change: {weekly["revenue_change_value"]:+,.2f} ({weekly["revenue_change_percent"]:+.2f}%)
- Units sold: {weekly["current_units"]}
- Previous units sold: {weekly["previous_units"]}
- Transactions: {weekly["current_transactions"]}
- Previous transactions: {weekly["previous_transactions"]}
- Best category: {weekly["best_category"]} ({weekly["best_category_revenue"]:,.2f})
- Best country: {weekly["best_country"]} ({weekly["best_country_revenue"]:,.2f})

## Key Insights

{format_list(business_analysis.key_insights)}

## Risks

{format_list(business_analysis.risks)}

## Recommendations

{format_list(business_analysis.recommendations)}
"""

    return report


def format_list(items):
    return "\n".join(f"- {item}" for item in items)


def save_report(report, filename="business_intelligence_report.md"):
    base_dir = Path(__file__).resolve().parent
    report_path = base_dir / filename

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report)

    return report_path