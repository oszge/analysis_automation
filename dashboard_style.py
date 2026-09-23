from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

PALETTE = ["#286a73", "#477d85", "#638d93", "#799da2", "#91a6aa", "#41666d"]


def apply_style():
    css = Path(__file__).with_name("dashboard.css").read_text(encoding="utf-8")
    st.html(f"<style>{css}</style>")


def chart_layout(fig, height=340):
    fig.update_layout(
        template="plotly_white", height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", size=12, color="#5c6870"),
        margin=dict(l=18, r=24, t=28, b=24),
        hoverlabel=dict(bgcolor="#f7fafa", bordercolor="#9db8bc", font_color="#293238"),
        legend=dict(orientation="h", y=1.14, x=0, title=None),
        colorway=PALETTE, bargap=0.38,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, title=None, tickfont_size=11)
    fig.update_yaxes(gridcolor="rgba(92,125,132,0.14)", zeroline=False, title=None, tickfont_size=11)
    return fig


def revenue_chart(series):
    fig = go.Figure()
    # Identical geometry on each layer: the halo never changes the data curve.
    for width, opacity in [(14, 0.025), (8, 0.055), (4, 0.12)]:
        fig.add_trace(go.Scatter(x=series.index, y=series.values, mode="lines",
                                line=dict(color=f"rgba(40,106,115,{opacity})", width=width),
                                name="Revenue glow", hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(
        x=series.index, y=series.values, mode="lines", name="Revenue (EUR)",
        line=dict(color="#286a73", width=2.5), fill="tozeroy", fillcolor="rgba(40,106,115,0.12)",
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
        marker=dict(color="rgba(40,106,115,0.05)", line=dict(color="rgba(40,106,115,0.08)", width=5)),
        name="Revenue glow", hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Bar(
        x=values.values, y=values.index, orientation="h",
        name="Revenue (EUR)", showlegend=False,
        marker=dict(color=[PALETTE[i % len(PALETTE)] for i in range(len(values))],
                    line=dict(color="rgba(255,255,255,0.8)", width=1)),
        hovertemplate="%{y}<br><b>%{x:,.2f} €</b><extra>Revenue</extra>",
    ))
    chart_layout(fig, max(280, len(values) * 36))
    fig.update_xaxes(ticksuffix=" €", showgrid=True, gridcolor="rgba(92,125,132,0.14)")
    fig.update_yaxes(showgrid=False, categoryorder="array", categoryarray=list(values.index))
    return fig


def comparison_chart(comparison):
    fig = go.Figure()
    for label, color, glow in [("Current revenue (EUR)", "#286a73", "rgba(40,106,115,0.08)"),
                               ("Previous revenue (EUR)", "#adb8bd", "rgba(135,150,156,0.07)")]:
        # Soft translucent underlay creates a restrained platinum glow around each bar.
        fig.add_trace(go.Bar(x=comparison.index, y=comparison[label], name=label + " glow",
                             marker=dict(color=glow, line=dict(color=glow, width=5)),
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
