"""可折叠侧边栏控制面板"""

from dash import html, dcc


def create_sidebar(module_id, functions_dict):
    """生成模块侧边栏：函数选择器 + 参数面板 + 折叠按钮"""
    func_options = [
        {"label": v["label"], "value": k}
        for k, v in functions_dict.items()
    ]
    first_func = next(iter(functions_dict.keys()))

    return html.Aside(
        id=f"{module_id}-sidebar",
        style={
            "width": "380px",
            "minWidth": "380px",
            "background": "var(--sidebar)",
            "borderRight": "1px solid var(--border)",
            "height": "calc(100vh - 64px)",
            "overflowY": "auto",
            "padding": "20px",
            "transition": "margin-left 0.3s ease, width 0.3s ease, min-width 0.3s ease",
        },
        children=[
            # 折叠按钮
            html.Button(
                "◀",
                id=f"{module_id}-sidebar-toggle",
                style={
                    "position": "absolute",
                    "top": "12px",
                    "right": "-14px",
                    "width": "28px",
                    "height": "28px",
                    "borderRadius": "50%",
                    "border": "1px solid var(--border)",
                    "background": "var(--bg)",
                    "color": "var(--text-secondary)",
                    "cursor": "pointer",
                    "fontSize": "12px",
                    "zIndex": "10",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                },
            ),
            # 模块标题
            html.H2(
                module_id.title(),
                style={
                    "fontSize": "20px",
                    "fontWeight": "700",
                    "color": "var(--text)",
                    "marginBottom": "20px",
                },
            ),
            # 函数选择器
            html.Label(
                "绘图函数",
                style={
                    "fontSize": "12px",
                    "fontWeight": "600",
                    "color": "var(--text-secondary)",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px",
                    "marginBottom": "6px",
                    "display": "block",
                },
            ),
            dcc.Dropdown(
                id=f"{module_id}-func-select",
                options=func_options,
                value=first_func,
                clearable=False,
                searchable=False,
                style={"fontSize": "13px", "marginBottom": "24px"},
            ),
            # 动态参数面板
            html.Div(id=f"{module_id}-params-panel"),
            # 侧边栏状态存储
            dcc.Store(id=f"{module_id}-sidebar-state", data={"open": True}),
        ],
    )
