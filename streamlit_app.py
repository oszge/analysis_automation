"""Start with: python -m streamlit run streamlit_app.py"""

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from dashboard_data import BASE_DIR, load_sales, segment_comparison, totals
from dashboard_style import apply_style, revenue_chart, ranking_chart, comparison_chart, show_chart

st.set_page_config(page_title="Sales Intelligence", page_icon="📊", layout="wide")
apply_style()


@st.cache_data(ttl=300, show_spinner="Loading sales data…")
def cached_sales(source):
    return load_sales(source), datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def metrics(data, previous=None):
    values = totals(data)
    baseline = totals(previous) if previous is not None else None
    for column, (key, label) in zip(st.columns(3), [
        ("revenue", "Revenue (EUR)"), ("quantity", "Units sold"), ("transactions", "Transactions"),
    ]):
        delta = None
        if baseline is not None:
            change = values[key] - baseline[key]
            delta = f"{change:+,.2f} €" if key == "revenue" else f"{change:+,}"
            if key == "revenue" and baseline[key] != 0:
                delta += f" ({change / baseline[key] * 100:+.2f}%)"
        column.metric(label, f"{values[key]:,.2f} €" if key == "revenue" else f"{values[key]:,}", delta)


def display_table(frame, *, hide_index=False):
    """Keep currency values readable and left aligned across all dashboard tables."""
    if isinstance(frame, pd.Series):
        frame = frame.to_frame()
    display = frame.copy()
    column_config = {}
    for column in display.columns:
        name = str(column)
        if "EUR" in name or "revenue" in name.lower() or "Change (EUR)" in name:
            display[column] = pd.to_numeric(display[column], errors="coerce").round(2)
            column_config[column] = st.column_config.NumberColumn(name, format="%,.2f €")
        elif "Change (%)" in name:
            display[column] = pd.to_numeric(display[column], errors="coerce").round(2)
            column_config[column] = st.column_config.NumberColumn(name, format="%.2f%%")
    st.dataframe(display, column_config=column_config, hide_index=hide_index, width="stretch")


st.html('''<div class="hero"><div><div class="eyebrow">SALES INTELLIGENCE / OVERVIEW</div>
<h1>Business Intel<span style="color:#9bb1c5">.</span></h1>
<p>Clear performance. Informed decisions.</p></div>''')

with st.sidebar:
    st.html('<div class="brand"><span class="brand-mark">◈</span> INTELLIGENCE</div>')
    st.header("Data & filters")
    source = st.radio("Data source", ["Neon PostgreSQL", "CSV"],
                      help="CSV uses the local sales_data file, not the live database.")
    if st.button("Refresh data", width="stretch"):
        cached_sales.clear()
    st.caption("Data is cached for 5 minutes. Refreshing does not trigger an AI request.")

try:
    data, loaded_at = cached_sales(source)
except Exception as exc:
    st.error("Unable to load the data source. Check the database connection and data format, or select the local CSV.")
    # Never display exception text: database errors may contain credentials.
    error_type = type(exc).__name__
    sqlstate = getattr(getattr(exc, "orig", None), "pgcode", None)
    hints = {
        "OperationalError": "Database connection failed. Check credentials, network access and SSL settings.",
        "ProgrammingError": "The database query failed. Check that sales_v2 and its required columns exist in the configured database.",
        "ArgumentError": "DATABASE_URL is missing or is not a valid SQLAlchemy connection URL.",
        "ModuleNotFoundError": "A required Python dependency is missing from the deployment.",
        "ValueError": "Check DATABASE_URL and the required sales columns, dates and numeric values.",
    }
    st.caption(hints.get(error_type, "Data loading failed; diagnostic code below."))
    st.code(f"Error type: {error_type}" + (f" | SQLSTATE: {sqlstate}" if sqlstate else ""))
    st.stop()

if data.empty:
    st.info("The data source does not contain any sales yet.")
    st.stop()

with st.sidebar:
    countries = st.multiselect("Country", sorted(data.country.unique()), default=sorted(data.country.unique()))
    categories = st.multiselect("Category", sorted(data.category.unique()), default=sorted(data.category.unique()))
    dates = st.date_input("Overview date range", value=(data.sale_date.min().date(), data.sale_date.max().date()),
                          min_value=data.sale_date.min().date(), max_value=data.sale_date.max().date())
    st.caption(f"Loaded: {loaded_at}")

segment = data[data.country.isin(countries) & data.category.isin(categories)]
if len(dates) != 2:
    st.info("Select both a start date and an end date.")
    st.stop()
filtered = segment[segment.sale_date.between(pd.Timestamp(dates[0]), pd.Timestamp(dates[1]))]
st.caption(f"Source: {source} · Latest data: {data.sale_date.max():%Y-%m-%d} · Currency: EUR (€)")

overview, trends, ai_tab = st.tabs(["Overview", "Weekly & monthly comparison", "AI analysis"])

with overview:
    today = pd.Timestamp.now(tz="Europe/Budapest").tz_localize(None).normalize()
    yesterday = today - pd.Timedelta(days=1)
    today_sales = segment[segment.sale_date.eq(today)]
    yesterday_sales = segment[segment.sale_date.eq(yesterday)]
    st.subheader("Today vs yesterday")
    st.caption(f"Today: {today:%Y-%m-%d} · Yesterday: {yesterday:%Y-%m-%d} · Europe/Budapest. Country and category filters apply; the date range applies only to the charts and tables below. Today is still in progress.")
    metrics(today_sales, yesterday_sales)
    if today_sales.empty or yesterday_sales.empty:
        st.info("A day without matching records is shown as zero. This may indicate no sales or data that has not arrived yet.")
    if filtered.empty:
        st.info("No sales match the selected filters.")
    else:
        st.subheader(f"Revenue trend · {dates[0]:%Y-%m-%d} – {dates[1]:%Y-%m-%d}")
        frequency = st.radio("Frequency", ["Daily", "Weekly", "Monthly"], horizontal=True)
        rule = {"Daily": "D", "Weekly": "W-SUN", "Monthly": "MS"}[frequency]
        daily = filtered.groupby("sale_date").revenue.sum().reindex(
            pd.date_range(dates[0], dates[1]), fill_value=0)
        series = daily.resample(rule).sum().rename("Revenue (EUR)")
        show_chart(revenue_chart(series), "revenue_chart")
        st.caption("The first and last weekly or monthly points may represent partial periods within the selected date range.")
        for dimension, title in [("category", "Categories"), ("country", "Countries"), ("product", "Top 10 products")]:
            with st.expander(title, expanded=dimension != "product"):
                ranking = filtered.groupby(dimension).revenue.sum().sort_values(ascending=False)
                show_chart(ranking_chart(ranking), f"ranking_{dimension}")
                display_table(ranking.rename("Revenue (EUR)").round(2))
        with st.expander("Transactions"):
            display_table(filtered.rename(columns={"revenue": "Revenue (EUR)"}), hide_index=True)
        st.download_button("Download filtered data (CSV)", filtered.to_csv(index=False).encode("utf-8-sig"),
                           "sales_filtered.csv", "text/csv")

with trends:
    choice = st.radio("Comparison", ["Monthly", "Weekly"], horizontal=True)
    frequency = "M" if choice == "Monthly" else "W-SUN"
    periods = list(pd.period_range(data.sale_date.min(), data.sale_date.max(), freq=frequency)[::-1])

    def period_label(value):
        if choice == "Monthly":
            return value.start_time.strftime("%Y-%m")
        return f"{value.start_time:%Y-%m-%d} – {value.end_time:%Y-%m-%d} (Mon–Sun)"

    left, right = st.columns(2)
    selected = left.selectbox("Current period", periods, format_func=period_label, key=f"current_{choice}")
    baseline = right.selectbox("Baseline period", periods, index=min(1, len(periods) - 1), format_func=period_label, key=f"baseline_{choice}")
    start, end = selected.start_time, selected.end_time.normalize()
    previous_start, previous_end = baseline.start_time, baseline.end_time.normalize()
    current = segment[segment.sale_date.between(start, end)]
    previous = segment[segment.sale_date.between(previous_start, previous_end)]
    st.caption(f"Current: {start:%Y-%m-%d} – {end:%Y-%m-%d} | Previous: {previous_start:%Y-%m-%d} – {previous_end:%Y-%m-%d}")
    st.caption("Country and category filters apply. Comparison periods are independent of the overview date range. Changes show the current period minus the baseline period.")
    if selected == baseline:
        st.info("Both selections refer to the same period.")
    if any(a < data.sale_date.min() or b > data.sale_date.max() for a, b in [(start, end), (previous_start, previous_end)]):
        st.warning("A selected period extends beyond the available data range; its totals may be incomplete.")
    metrics(current, previous)
    if previous.revenue.sum() == 0:
        st.caption("Percentage change is unavailable when previous revenue is zero.")
    dimension = st.selectbox("Breakdown", ["category", "country", "product"],
                            format_func=lambda key: {"category": "Category", "country": "Country", "product": "Product"}[key])
    comparison = segment_comparison(current, previous, dimension)
    if comparison.empty:
        st.info("No data is available for the selected segments in these periods.")
    else:
        show_chart(comparison_chart(comparison.head(10)), "comparison_chart")
        display_table(comparison)

with ai_tab:
    st.subheader("Previously generated business analysis")
    st.warning("This saved analysis covers the previous full dataset. Filters do not change it, and its consistency with the current data has not been verified.")
    st.caption("The dashboard does not trigger AI requests or run the report generation pipeline.")
    ai_path = BASE_DIR / "ai_response.json"
    try:
        saved = json.loads(ai_path.read_text(encoding="utf-8"))
        if not isinstance(saved, dict) or not isinstance(saved.get("executive_summary"), str):
            raise ValueError("Invalid summary")
        for key in ("key_insights", "risks", "recommendations"):
            if not isinstance(saved.get(key), list) or not all(isinstance(x, str) for x in saved[key]):
                raise ValueError("Invalid section")
    except (OSError, ValueError):
        st.info("No readable, correctly formatted saved AI analysis is available yet.")
    else:
        st.caption(f"File updated: {datetime.fromtimestamp(ai_path.stat().st_mtime):%Y-%m-%d %H:%M} (not the analysis period)")
        st.markdown(saved["executive_summary"])
        for key, label in [("key_insights", "Key insights"), ("risks", "Risks"), ("recommendations", "Recommendations")]:
            st.subheader(label)
            for item in saved[key]:
                st.markdown(f"- {item}")
    report_path = BASE_DIR / "business_intelligence_report.md"
    if report_path.is_file():
        st.download_button("Download saved report", report_path.read_bytes(),
                           report_path.name, "text/markdown")
