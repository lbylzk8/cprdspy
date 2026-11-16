"""通用控件工厂 — slider+input、color、dropdown、toggle"""

from dash import html, dcc
import numpy as np

# 预设色板
PRESET_COLORS = [
    {"label": "🔴 红", "value": "#e74c3c"},
    {"label": "🔵 蓝", "value": "#3498db"},
    {"label": "🟢 绿", "value": "#2ecc71"},
    {"label": "🟠 橙", "value": "#e67e22"},
    {"label": "🟣 紫", "value": "#9b59b6"},
    {"label": "🟡 金", "value": "#f1c40f"},
    {"label": "🩵 青", "value": "#1abc9c"},
    {"label": "🩷 粉", "value": "#e91e90"},
    {"label": "⚪ 白", "value": "#ecf0f1"},
    {"label": "🌸 玫红", "value": "#c2185b"},
    {"label": "🌊 深蓝", "value": "#1565c0"},
    {"label": "🌿 墨绿", "value": "#2e7d32"},
]

CMAP_OPTIONS = [
    {"label": "Viridis", "value": "viridis"},
    {"label": "Plasma", "value": "plasma"},
    {"label": "Inferno", "value": "inferno"},
    {"label": "Magma", "value": "magma"},
    {"label": "Turbo", "value": "turbo"},
    {"label": "Coolwarm", "value": "coolwarm"},
    {"label": "Spectral", "value": "Spectral"},
]

CTRL_STYLE = {
    "marginBottom": "16px",
}

LABEL_STYLE = {
    "fontSize": "12px",
    "fontWeight": "600",
    "color": "var(--text-secondary)",
    "marginBottom": "4px",
    "display": "block",
    "textTransform": "uppercase",
    "letterSpacing": "0.5px",
}

INPUT_STYLE = {
    "width": "80px",
    "height": "32px",
    "border": "1px solid var(--border)",
    "borderRadius": "6px",
    "padding": "4px 8px",
    "fontSize": "13px",
    "background": "var(--bg)",
    "color": "var(--text)",
}


def make_slider(module_id, name, label, min_val, max_val, step, default, marks=None):
    """slider + number input 联动控件"""
    cid = f"{module_id}-{name}"
    if marks is None:
        marks = {min_val: str(min_val), max_val: str(max_val)}
    return html.Div(
        [
            html.Label(label, style=LABEL_STYLE),
            html.Div(
                [
                    html.Div(dcc.Slider(
                        id=f"{cid}-slider", min=min_val, max=max_val, step=step,
                        value=default, marks=marks,
                        tooltip={"placement": "bottom", "always_visible": False},
                    ), style={"flex": "1", "marginRight": "10px"}),
                    dcc.Input(
                        id=f"{cid}-input", type="number",
                        min=min_val, max=max_val, step=step, value=default,
                        style=INPUT_STYLE,
                    ),
                ],
                style={"display": "flex", "alignItems": "center"},
            ),
        ],
        style=CTRL_STYLE,
    )


def make_color(module_id, name, default="#3498db"):
    """颜色选择器：预设 dropdown + 自定义 hex input"""
    cid = f"{module_id}-{name}"
    return html.Div(
        [
            html.Label("颜色", style=LABEL_STYLE),
            html.Div(
                [
                    dcc.Dropdown(
                        id=f"{cid}-dropdown",
                        options=PRESET_COLORS,
                        value=default,
                        clearable=False,
                        searchable=False,
                        style={"width": "160px", "fontSize": "13px"},
                    ),
                    dcc.Input(
                        id=f"{cid}-input", type="text", value=default,
                        placeholder="#RRGGBB",
                        style={**INPUT_STYLE, "width": "100px", "marginLeft": "8px"},
                    ),
                ],
                style={"display": "flex", "alignItems": "center"},
            ),
        ],
        style=CTRL_STYLE,
    )


def make_dropdown(module_id, name, label, options, default):
    """通用 dropdown"""
    return html.Div(
        [
            html.Label(label, style=LABEL_STYLE),
            dcc.Dropdown(
                id=f"{module_id}-{name}",
                options=options, value=default, clearable=False,
                style={"fontSize": "13px"},
            ),
        ],
        style=CTRL_STYLE,
    )


def make_toggle(module_id, name, label, options, default):
    """RadioItems 切换"""
    return html.Div(
        [
            html.Label(label, style=LABEL_STYLE),
            dcc.RadioItems(
                id=f"{module_id}-{name}",
                options=options, value=default,
                style={"fontSize": "13px"},
                inputStyle={"marginRight": "6px"},
                labelStyle={"marginRight": "16px", "display": "inline-block"},
            ),
        ],
        style=CTRL_STYLE,
    )


def build_panel(module_id, func_def):
    """根据函数定义生成完整参数控制面板"""
    children = []
    for p in func_def["params"]:
        name = p["name"]
        ptype = p.get("type", "slider")
        if ptype == "slider":
            fm = p.get("marks")
            marks = {fm[i]: str(fm[i]) for i in range(0, len(fm))} if fm else None
            children.append(make_slider(
                module_id, name, p["label"],
                p["min"], p["max"], p.get("step", 1), p["default"], marks,
            ))
        elif ptype == "color":
            children.append(make_color(module_id, name, p.get("default", "#3498db")))
        elif ptype == "dropdown":
            children.append(make_dropdown(
                module_id, name, p["label"],
                p.get("options", []), p["default"],
            ))
        elif ptype == "toggle":
            children.append(make_toggle(
                module_id, name, p["label"],
                p.get("options", []), p["default"],
            ))
    return children
