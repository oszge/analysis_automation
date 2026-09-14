"""Shared platinum theme and interactive chart styling."""

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

PALETTE = ["#8cabc4", "#a6b6d0", "#9ebdb9", "#bab2cc", "#c6baa7", "#aab6c4"]


def apply_style():
    css = Path(__file__).with_name("dashboard.css").read_text(encoding="utf-8")
    st.html(f"<style>{css}</style>")


def chart_layout(fig, height=340):
    fig.update_layout(
        template="plotly_white", height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, sans-serif", size=12, color="#596a7c"),
        margin=dict(l=12, r=24, t=24, b=20),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#cbd8e3", font_color="#273a4d"),
        legend=dict(orientation="h", y=1.14, x=0, title=None),
        colorway=PALETTE, bargap=0.38,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, title=None, tickfont_size=11)
    fig.update_yaxes(gridcolor="rgba(151,170,189,0.16)", zeroline=False, title=None, tickfont_size=11)
    return fig


def revenue_chart(series):
    fig = go.Figure()
    # Identical geometry on each layer: the halo never changes the data curve.
    for width, opacity in [(24, 0.10), (14, 0.16), (7, 0.24)]:
        fig.add_trace(go.Scatter(x=series.index, y=series.values, mode="lines",
                                line=dict(color=f"rgba(103,151,189,{opacity})", width=width),
                                hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(
        x=series.index, y=series.values, mode="lines", name="Revenue",
        line=dict(color="#739bbd", width=2.3), fill="tozeroy", fillcolor="rgba(150,182,207,0.10)",
        hovertemplate="%{x|%Y. %m. %d.}<br><b>%{y:,.2f} €</b><extra>Revenue</extra>",
        showlegend=False,
    ))
    chart_layout(fig, 360)
    fig.update_layout(hovermode="x unified")
    fig.update_yaxes(rangemode="tozero", tickformat=",.0f", ticksuffix=" €")
    return fig


def ranking_chart(ranking):
    values = ranking.head(10).iloc[::-1]
    fig = go.Figure()
    # A translucent wider bar is a visual halo; the foreground bar remains the data.
    fig.add_trace(go.Bar(
        x=values.values, y=values.index, orientation="h",
        marker=dict(color="rgba(125,164,194,0.20)", line=dict(color="rgba(125,164,194,0.20)", width=16)),
        hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Bar(
        x=values.values, y=values.index, orientation="h",
        marker=dict(color=[PALETTE[i % len(PALETTE)] for i in range(len(values))],
                    line=dict(color="rgba(255,255,255,0.8)", width=1)),
        hovertemplate="%{y}<br><b>%{x:,.2f} €</b><extra>Revenue</extra>",
    ))
    chart_layout(fig, max(280, len(values) * 36))
    fig.update_xaxes(ticksuffix=" €", showgrid=True, gridcolor="rgba(151,170,189,0.16)")
    fig.update_yaxes(showgrid=False, categoryorder="array", categoryarray=list(values.index))
    return fig


def comparison_chart(comparison):
    fig = go.Figure()
    for label, color in [("Current revenue (EUR)", "#91adc5"), ("Previous revenue (EUR)", "#c7cbd7")]:
        # Soft translucent underlay creates a restrained platinum glow around each bar.
        fig.add_trace(go.Bar(x=comparison.index, y=comparison[label], name="",
                             marker=dict(color="rgba(145,173,197,0.20)", line=dict(color="rgba(145,173,197,0.22)", width=12)),
                             hoverinfo="skip", showlegend=False, offsetgroup=label))
        fig.add_trace(go.Bar(x=comparison.index, y=comparison[label], name=label,
                             marker=dict(color=color, line=dict(color="#ffffff", width=1)),
                             hovertemplate="%{x}<br><b>%{y:,.2f} €</b><extra>" + label + "</extra>", offsetgroup=label))
    chart_layout(fig, 380)
    fig.update_layout(barmode="group")
    fig.update_yaxes(ticksuffix=" €")
    return fig


def show_chart(fig, key):
    st.plotly_chart(fig, theme=None, width="stretch", key=key,
                    config={"displayModeBar": False, "scrollZoom": False, "responsive": True})
