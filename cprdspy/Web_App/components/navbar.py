"""顶部导航栏 — 模块标签页 + 主题切换"""

from dash import html, dcc

THEME_OPTIONS = [
    {"label": "☀️ Classic", "value": "classic"},
    {"label": "🌙 Dark", "value": "dark"},
    {"label": "🌊 Deep Sea", "value": "deep_sea"},
    {"label": "🤖 Cyberpunk", "value": "cyberpunk"},
    {"label": "🌌 Aurora", "value": "aurora"},
    {"label": "🌅 Sunset", "value": "sunset"},
    {"label": "🌲 Forest", "value": "forest"},
]

MODULES = [
    {"id": "arcs", "label": "Arcs", "icon": "⌒"},
    {"id": "circles", "label": "Circles", "icon": "○"},
    {"id": "dots", "label": "Dots", "icon": "∙"},
    {"id": "flowers", "label": "Flowers", "icon": "✿"},
    {"id": "lines", "label": "Lines", "icon": "╱"},
    {"id": "spirals", "label": "Spirals", "icon": "◎"},
    {"id": "stars", "label": "Stars", "icon": "★"},
    {"id": "waves", "label": "Waves", "icon": "≈"},
]


def create_navbar(current_module="arcs"):
    """生成顶部导航栏"""
    tabs = []
    for m in MODULES:
        active = m["id"] == current_module
        tabs.append(
            dcc.Link(
                html.Span([
                    html.Span(m["icon"], style={"marginRight": "6px", "fontSize": "16px"}),
                    m["label"],
                ], style={
                    "display": "inline-flex",
                    "alignItems": "center",
                    "padding": "10px 18px",
                    "borderRadius": "10px",
                    "fontSize": "13px",
                    "fontWeight": "600",
                    "color": "var(--accent)" if active else "var(--text-secondary)",
                    "background": "var(--accent-light)" if active else "transparent",
                    "transition": "all 0.2s ease",
                }),
                href=f"/{m['id']}",
                style={"textDecoration": "none"},
            )
        )

    return html.Nav(
        style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "padding": "0 24px",
            "height": "64px",
            "background": "var(--bg)",
            "borderBottom": "1px solid var(--border)",
            "position": "sticky",
            "top": "0",
            "zIndex": "1000",
            "backdropFilter": "blur(12px)",
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "4px",
                    "overflowX": "auto",
                    "scrollbarWidth": "none",
                },
                children=[
                    html.Span("CPR", style={
                        "fontSize": "22px",
                        "fontWeight": "800",
                        "color": "var(--accent)",
                        "marginRight": "16px",
                        "letterSpacing": "-1px",
                    }),
                    *tabs,
                ],
            ),
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "8px",
                    "flexShrink": "0",
                },
                children=[
                    dcc.Dropdown(
                        id="theme-selector",
                        options=THEME_OPTIONS,
                        value="classic",
                        clearable=False,
                        searchable=False,
                        style={"width": "160px", "fontSize": "13px"},
                    ),
                ],
            ),
        ],
    )
