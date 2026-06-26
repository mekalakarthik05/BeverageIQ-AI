import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Enterprise Color Palette
COLORS = ["#6D5BFF", "#3B82F6", "#2DD4BF", "#F59E0B", "#EF4444", "#8B5CF6", "#22C55E"]
BG_COLOR = "#161B2F"
PAPER_COLOR = "#0B1020"
TEXT_COLOR = "#94A3B8"
GRID_COLOR = "rgba(255,255,255,0.08)"

def apply_enterprise_theme(fig):
    """Applies the enterprise dark theme to a plotly figure, standardizing heights and paddings."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B1020",
        plot_bgcolor="#0B1020",
        font=dict(
            family="Inter",
            color="#F8FAFC",
            size=13,
        ),
        title_font=dict(
            color="#F8FAFC",
            size=20,
        ),
        legend=dict(
            font=dict(color="#F8FAFC"),
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(
            color="#CBD5E1",
            gridcolor="#293042"
        ),
        yaxis=dict(
            color="#CBD5E1",
            gridcolor="#293042"
        ),
        height=450,
        margin=dict(l=30, r=30, t=60, b=80),
        colorway=COLORS,
        hoverlabel=dict(bgcolor=BG_COLOR, font_size=13, font_family="Inter", bordercolor=GRID_COLOR)
    )
    # strictly placing legend BELOW the chart to prevent overlapping
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    return fig

# Basic chat chart generator
def generate_chart(intent: str, df: pd.DataFrame):
    if df is None or df.empty:
        return None
    try:
        if intent in ["sales", "revenue"] and 'category' in df.columns:
            fig = px.bar(df, x='category', y='revenue', title="Revenue by Category", color='category', color_discrete_sequence=COLORS)
            return apply_enterprise_theme(fig)
        elif intent == "promotion" and 'promotion_type' in df.columns:
            fig = px.pie(df, values='revenue', names='promotion_type', title="Revenue by Promotion Type", color_discrete_sequence=COLORS, hole=0.4)
            return apply_enterprise_theme(fig)
        elif intent == "trend" and 'week' in df.columns:
            fig = px.line(df, x='week', y='revenue', title="Weekly Revenue Trend", markers=True, color_discrete_sequence=[COLORS[1]])
            fig.update_traces(line=dict(width=3), marker=dict(size=6))
            return apply_enterprise_theme(fig)
        elif intent in ["top_products", "bottom_products"] and 'product_name' in df.columns:
            df_sorted = df.sort_values(by='revenue', ascending=True)
            fig = px.bar(df_sorted, x='revenue', y='product_name', orientation='h', title="Product Performance", color='revenue', color_continuous_scale=[COLORS[2], COLORS[0]])
            return apply_enterprise_theme(fig)
        elif intent in ["inventory", "stockout"] and 'region' in df.columns:
            fig = px.bar(df, x='region', y='stockout_flag', title="Stockout Incidents by Region", color='region', color_discrete_sequence=COLORS)
            return apply_enterprise_theme(fig)
        elif intent == "comparison" and 'region' in df.columns:
            fig = px.bar(df, x='region', y='revenue', title="Revenue Comparison by Region", color='region', color_discrete_sequence=COLORS)
            return apply_enterprise_theme(fig)
    except Exception as e:
        print(f"Error generating chart: {e}")
    return None

# Advanced dashboard charts
def create_bar_chart(df, x_col, y_col, title, color_col=None, orientation='v'):
    if df.empty: return None
    fig = px.bar(df, x=x_col, y=y_col, title=title, color=color_col if color_col else None, orientation=orientation, color_discrete_sequence=COLORS)
    return apply_enterprise_theme(fig)

def create_line_chart(df, x_col, y_col, title, color_col=None):
    if df.empty: return None
    fig = px.line(df, x=x_col, y=y_col, title=title, color=color_col if color_col else None, markers=True, color_discrete_sequence=COLORS)
    fig.update_traces(line=dict(width=3), marker=dict(size=6))
    return apply_enterprise_theme(fig)

def create_donut_chart(df, names_col, values_col, title):
    if df.empty: return None
    fig = px.pie(df, names=names_col, values=values_col, title=title, hole=0.6, color_discrete_sequence=COLORS)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return apply_enterprise_theme(fig)
