"""Start with: python -m streamlit run streamlit_app.py"""

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from dashboard_data import BASE_DIR, load_sales, period_comparison, segment_comparison, totals
from dashboard_style import apply_style, revenue_chart, ranking_chart, comparison_chart, show_chart

st.set_page_config(page_title="Sales Intelligence", page_icon="📊", layout="wide")
apply_style()


@st.cache_data(ttl=300, show_spinner="Értékesítési adatok betöltése…")
def cached_sales(source):
    return load_sales(source), datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def metrics(data, previous=None):
    values = totals(data)
    baseline = totals(previous) if previous is not None else None
    for column, (key, label) in zip(st.columns(3), [
        ("revenue", "Bevétel (EUR)"), ("quantity", "Eladott darab"), ("transactions", "Tranzakció"),
    ]):
        delta = None
        if baseline is not None:
            change = values[key] - baseline[key]
            delta = f"{change:+,.2f} €" if key == "revenue" else f"{change:+,}"
            if key == "revenue" and baseline[key] != 0:
                delta += f" ({change / baseline[key] * 100:+.2f}%)"
        column.metric(label, f"{values[key]:,.2f} €" if key == "revenue" else f"{values[key]:,}", delta)


st.html('''<div class="hero"><div><div class="eyebrow">BUSINESS INTELLIGENCE / OVERVIEW</div>
<h1>Sales Intelligence<span style="color:#9bb1c5">.</span></h1>
<p>Átlátható teljesítmény. Megalapozott döntések.</p></div>
<div class="hero-badge">PLATINUM EDITION</div></div>''')

with st.sidebar:
    st.html('<div class="brand"><span class="brand-mark">◈</span> INTELLIGENCE</div>')
    st.header("Adatok és szűrők")
    source = st.radio("Adatforrás", ["Neon PostgreSQL", "CSV"],
                      help="A CSV a projekt helyi sales_data fájlja; nem élő adatbázis.")
    if st.button("Adatok újratöltése", width="stretch"):
        cached_sales.clear()
    st.caption("Az adatgyorsítótár 5 percig érvényes. Az újratöltés nem indít AI-hívást.")

try:
    data, loaded_at = cached_sales(source)
except Exception:
    st.error("Az adatforrás nem tölthető be. Ellenőrizd az adatbázis-kapcsolatot és az adatok formátumát, vagy válaszd a helyi CSV-t.")
    st.stop()

if data.empty:
    st.info("Az adatforrás még nem tartalmaz értékesítéseket.")
    st.stop()

with st.sidebar:
    countries = st.multiselect("Ország", sorted(data.country.unique()), default=sorted(data.country.unique()))
    categories = st.multiselect("Kategória", sorted(data.category.unique()), default=sorted(data.category.unique()))
    dates = st.date_input("Áttekintés időszaka", value=(data.sale_date.min().date(), data.sale_date.max().date()),
                          min_value=data.sale_date.min().date(), max_value=data.sale_date.max().date())
    st.caption(f"Betöltve: {loaded_at}")

segment = data[data.country.isin(countries) & data.category.isin(categories)]
if len(dates) != 2:
    st.info("Válaszd ki az időszak kezdő- és záródátumát.")
    st.stop()
filtered = segment[segment.sale_date.between(pd.Timestamp(dates[0]), pd.Timestamp(dates[1]))]
st.caption(f"Forrás: {source} · Legfrissebb adat: {data.sale_date.max():%Y-%m-%d} · Pénznem: EUR (€)")

overview, trends, ai_tab = st.tabs(["Áttekintés", "Heti és havi összehasonlítás", "Mentett AI-értékelés"])

with overview:
    st.subheader(f"{dates[0]:%Y-%m-%d} – {dates[1]:%Y-%m-%d}")
    metrics(filtered)
    if filtered.empty:
        st.info("A választott szűrőkkel nincs megjeleníthető értékesítés.")
    else:
        st.subheader("Bevétel alakulása")
        frequency = st.radio("Felbontás", ["Napi", "Heti", "Havi"], horizontal=True)
        rule = {"Napi": "D", "Heti": "W-SUN", "Havi": "MS"}[frequency]
        daily = filtered.groupby("sale_date").revenue.sum().reindex(
            pd.date_range(dates[0], dates[1]), fill_value=0)
        series = daily.resample(rule).sum().rename("Bevétel (EUR)")
        show_chart(revenue_chart(series), "revenue_chart")
        st.caption("A szélső heti/havi pontok a választott dátumhatároknál részidőszakot is tartalmazhatnak.")
        for dimension, title in [("category", "Kategóriák"), ("country", "Országok"), ("product", "Top 10 termék")]:
            with st.expander(title, expanded=dimension != "product"):
                ranking = filtered.groupby(dimension).revenue.sum().sort_values(ascending=False)
                show_chart(ranking_chart(ranking), f"ranking_{dimension}")
                st.dataframe(ranking.rename("Bevétel (EUR)").round(2), width="stretch")
        with st.expander("Tranzakciók"):
            st.dataframe(filtered.rename(columns={"revenue": "Bevétel (EUR)"}), hide_index=True, width="stretch")
        st.download_button("Szűrt adatok letöltése (CSV)", filtered.to_csv(index=False).encode("utf-8-sig"),
                           "sales_filtered.csv", "text/csv")

with trends:
    choice = st.radio("Összehasonlítás", ["Havi", "Heti"], horizontal=True)
    current, previous, bounds = period_comparison(segment, dates[1], "monthly" if choice == "Havi" else "weekly")
    start, end, previous_start, previous_end = bounds
    st.caption(f"Aktuális: {start:%Y-%m-%d} – {end:%Y-%m-%d} | Előző: {previous_start:%Y-%m-%d} – {previous_end:%Y-%m-%d}")
    st.info("Az összehasonlítás az áttekintés záródátumához igazodik, és megtartja az ország- és kategóriaszűrőt. A kezdődátumot nem használja.")
    if choice == "Havi" and end != end + pd.offsets.MonthEnd(0):
        st.warning("Részleges aktuális hónapot hasonlítunk a teljes előző hónaphoz, a meglévő riport logikája szerint.")
    if previous_start < data.sale_date.min():
        st.warning("Az előző időszak részben vagy teljesen az adatforrás dátumtartományán kívül esik.")
    metrics(current, previous)
    if previous.revenue.sum() == 0:
        st.caption("Nulla előző bevételnél százalékos változás nem számítható.")
    dimension = st.selectbox("Bontás", ["category", "country", "product"],
                            format_func=lambda key: {"category": "Kategória", "country": "Ország", "product": "Termék"}[key])
    comparison = segment_comparison(current, previous, dimension)
    if comparison.empty:
        st.info("Ezekben az időszakokban nincs adat a kiválasztott szegmensekre.")
    else:
        show_chart(comparison_chart(comparison.head(10)), "comparison_chart")
        st.dataframe(comparison, width="stretch")

with ai_tab:
    st.subheader("Korábban elkészített üzleti értékelés")
    st.warning("Ez a mentett értékelés a teljes korábbi elemzéshez tartozik. A szűrők nem módosítják; az aktuális adatokkal való egyezése nem igazolt.")
    st.caption("A dashboard nem hívja meg az AI-t, és nem futtatja a riportgeneráló folyamatot.")
    ai_path = BASE_DIR / "ai_response.json"
    try:
        saved = json.loads(ai_path.read_text(encoding="utf-8"))
        if not isinstance(saved, dict) or not isinstance(saved.get("executive_summary"), str):
            raise ValueError("Invalid summary")
        for key in ("key_insights", "risks", "recommendations"):
            if not isinstance(saved.get(key), list) or not all(isinstance(x, str) for x in saved[key]):
                raise ValueError("Invalid section")
    except (OSError, ValueError):
        st.info("Még nincs olvasható, megfelelő formátumú mentett AI-értékelés.")
    else:
        st.caption(f"Fájl módosítva: {datetime.fromtimestamp(ai_path.stat().st_mtime):%Y-%m-%d %H:%M} (nem az elemzett időszak)")
        st.markdown(saved["executive_summary"])
        for key, label in [("key_insights", "Fő megállapítások"), ("risks", "Kockázatok"), ("recommendations", "Javaslatok")]:
            st.subheader(label)
            for item in saved[key]:
                st.markdown(f"- {item}")
    report_path = BASE_DIR / "business_intelligence_report.md"
    if report_path.is_file():
        st.download_button("Korábban mentett riport letöltése", report_path.read_bytes(),
                           report_path.name, "text/markdown")
