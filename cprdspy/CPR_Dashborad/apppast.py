from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.graph_objects as go
import CPRSP as CPR
import inspect
import dash
import numpy as np
from dash.dependencies import Input, Output, State

# 定义深色主题的样式
DARK_THEME = {
    "background": "#1a1a1a",
    "text": "#ffffff",
    "primary": "#007bff",
    "secondary": "#6c757d",
    "success": "#28a745",
    "input-bg": "#2d2d2d",
    "card-bg": "#2d2d2d",
}

# 通用样式
COMMON_STYLES = {
    "input": {
        "width": "100%",
        "padding": "8px 12px",
        "margin": "8px 0",
        "border": f'1px solid {DARK_THEME["secondary"]}',
        "borderRadius": "4px",
        "backgroundColor": DARK_THEME["input-bg"],
        "color": DARK_THEME["text"],
        "fontSize": "14px",
    },
    "button": {
        "padding": "10px 20px",
        "margin": "10px 5px",
        "border": "none",
        "borderRadius": "4px",
        "cursor": "pointer",
        "fontSize": "14px",
        "fontWeight": "bold",
        "transition": "all 0.3s ease",
    },
    "container": {
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "20px",
    },
}

# 初始化 Dash 应用
app = Dash(__name__)

# 获取函数参数信息
paran = inspect.signature(CPR.flowers_flower_by_petal_multi).parameters
param_names = list(paran.keys())
param_docs = {
    name: (
        str(param.annotation)
        if param.annotation != inspect.Parameter.empty
        else "未提供说明"
    )
    for name, param in paran.items()
}

# 动态生成输入控件，包含参数说明
inputs = []
for i, name in enumerate(param_names):
    input_control = None

    if i == 0:  # 第一个参数：括号对格式
        input_control = html.Div(
            [
                dcc.Input(
                    id=f"input-{i}-start",
                    type="text",
                    placeholder="起始值",
                    style={**COMMON_STYLES["input"], "width": "45%"},
                ),
                html.Span(",", style={"margin": "0 10px", "color": DARK_THEME["text"]}),
                dcc.Input(
                    id=f"input-{i}-end",
                    type="text",
                    placeholder="结束值",
                    style={**COMMON_STYLES["input"], "width": "45%"},
                ),
            ],
            style={"display": "flex", "alignItems": "center"},
        )

    elif i in [1, 2, 3, 5, 6]:  # 整数下拉列表
        input_control = dcc.Dropdown(
            id=f"input-{i}",
            options=[{"label": str(j), "value": j} for j in range(1, 37)],  # 1-36的整数
            value=1,
            style={
                "backgroundColor": DARK_THEME["input-bg"],
                "color": DARK_THEME["text"],
            },
            className="dark-dropdown",
        )

    elif i == 4:  # 第五个参数：带开方按钮
        input_control = html.Div(
            [
                dcc.Input(
                    id=f"input-{i}",
                    type="text",
                    placeholder="输入数值",
                    style={**COMMON_STYLES["input"], "width": "80%"},
                ),
                html.Button(
                    "√",
                    id=f"sqrt-btn-{i}",
                    style={
                        **COMMON_STYLES["button"],
                        "width": "15%",
                        "marginLeft": "5%",
                        "backgroundColor": DARK_THEME["primary"],
                        "color": "white",
                    },
                ),
            ],
            style={"display": "flex", "alignItems": "center"},
        )

    elif i == 7:  # 第八个参数：θ (圆周倍数)
        input_control = html.Div(
            [
                dcc.Input(
                    id=f"input-{i}",
                    type="number",
                    placeholder="输入圆周数",
                    style={**COMMON_STYLES["input"], "width": "100%"},
                ),
                html.Div(
                    "输入值将自动乘以 2π",
                    style={
                        "fontSize": "12px",
                        "color": DARK_THEME["secondary"],
                        "marginTop": "5px",
                    },
                ),
            ]
        )

    elif i == 8:  # 最后一个参数：颜色输入
        input_control = html.Div(
            [
                dcc.Input(
                    id=f"input-{i}",
                    type="text",
                    placeholder="输入颜色值 (如: #ff0000, red)",
                    style={**COMMON_STYLES["input"], "width": "100%"},
                ),
                html.Div(
                    "支持颜色名称(red, blue等)或十六进制代码(#ff0000)",
                    style={
                        "fontSize": "12px",
                        "color": DARK_THEME["secondary"],
                        "marginTop": "5px",
                    },
                ),
            ]
        )

    else:  # 默认文本输入
        input_control = dcc.Input(
            id=f"input-{i}",
            type="text",
            placeholder=f"输入 {name} 的值",
            style=COMMON_STYLES["input"],
        )

    inputs.extend(
        [
            html.Div(
                [
                    html.Label(
                        [
                            f"参数 {name}",
                            html.Span(
                                " ℹ️",
                                title=param_docs[name],
                                style={"cursor": "help", "marginLeft": "5px"},
                            ),
                        ],
                        style={
                            "color": DARK_THEME["text"],
                            "marginBottom": "5px",
                            "display": "block",
                        },
                    ),
                    input_control,
                ],
                style={"marginBottom": "15px"},
            )
        ]
    )

# 添加图表控制选项
inputs.extend(
    [
        html.Div(
            [
                html.H4(
                    "图表设置", style={"marginTop": "20px", "marginBottom": "15px"}
                ),
                html.Div(
                    [
                        dcc.Checklist(
                            id="chart-options",
                            options=[
                                {"label": " 显示坐标轴", "value": "show_axes"},
                                {"label": " 显示网格线", "value": "show_grid"},
                            ],
                            value=["show_axes", "show_grid"],
                            style={"color": DARK_THEME["text"]},
                        ),
                    ]
                ),
            ],
            style={
                "backgroundColor": DARK_THEME["card-bg"],
                "padding": "15px",
                "borderRadius": "8px",
                "marginTop": "20px",
            },
        )
    ]
)

# 初始化全局图表对象
global_fig = go.Figure()

# 定义应用布局
app.layout = html.Div(
    style={
        "backgroundColor": DARK_THEME["background"],
        "minHeight": "100vh",
        "color": DARK_THEME["text"],
    },
    children=[
        html.Div(
            [
                html.H1(
                    "CPR 图形生成器",
                    style={
                        "textAlign": "center",
                        "padding": "20px 0",
                        "color": DARK_THEME["text"],
                        "borderBottom": f'1px solid {DARK_THEME["secondary"]}',
                        "marginBottom": "30px",
                    },
                ),
                html.Div(
                    [
                        # 左侧面板：输入和控制
                        html.Div(
                            [
                                html.Div(
                                    style={
                                        "backgroundColor": DARK_THEME["card-bg"],
                                        "padding": "20px",
                                        "borderRadius": "8px",
                                        "boxShadow": "0 2px 4px rgba(0,0,0,0.2)",
                                    },
                                    children=[
                                        html.H3(
                                            "参数设置", style={"marginBottom": "20px"}
                                        ),
                                        *inputs,
                                        html.Div(
                                            [
                                                html.Button(
                                                    "🎨 绘制图表",
                                                    id="submit-btn",
                                                    style={
                                                        **COMMON_STYLES["button"],
                                                        "backgroundColor": DARK_THEME[
                                                            "primary"
                                                        ],
                                                        "color": "white",
                                                    },
                                                ),
                                                html.Button(
                                                    "🗑️ 清除图表",
                                                    id="clear-btn",
                                                    style={
                                                        **COMMON_STYLES["button"],
                                                        "backgroundColor": DARK_THEME[
                                                            "secondary"
                                                        ],
                                                        "color": "white",
                                                    },
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "justifyContent": "space-between",
                                            },
                                        ),
                                        html.Div(
                                            "支持使用 numpy 表达式，如 np.pi, np.sin(0.5) 等",
                                            style={
                                                "marginTop": "15px",
                                                "fontSize": "12px",
                                                "color": DARK_THEME["secondary"],
                                                "textAlign": "center",
                                            },
                                        ),
                                    ],
                                ),
                            ],
                            style={"flex": "1", "marginRight": "20px"},
                        ),
                        # 右侧面板：图表输出
                        html.Div(
                            [
                                html.Div(
                                    id="output",
                                    style={
                                        "backgroundColor": DARK_THEME["card-bg"],
                                        "padding": "20px",
                                        "borderRadius": "8px",
                                        "boxShadow": "0 2px 4px rgba(0,0,0,0.2)",
                                        "minHeight": "600px",
                                    },
                                ),
                            ],
                            style={"flex": "2"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "gap": "20px",
                        "padding": "0 20px",
                        "maxWidth": "1400px",
                        "margin": "0 auto",
                    },
                ),
            ],
            style=COMMON_STYLES["container"],
        )
    ],
)

# 添加CSS样式
app.index_string = (
    """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>CPR 图形生成器</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                background-color: """
    + DARK_THEME["background"]
    + """;
            }
            input:focus {
                outline: none;
                border-color: """
    + DARK_THEME["primary"]
    + """;
                box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
            }
            button:hover {
                opacity: 0.9;
                transform: translateY(-1px);
            }
            button:active {
                transform: translateY(0);
            }
            .dash-dropdown .Select-control {
                background-color: """
    + DARK_THEME["input-bg"]
    + """;
                border-color: """
    + DARK_THEME["secondary"]
    + """;
            }
            .dash-dropdown .Select-menu-outer {
                background-color: """
    + DARK_THEME["input-bg"]
    + """;
                border-color: """
    + DARK_THEME["secondary"]
    + """;
            }
            .dash-dropdown .Select-value-label {
                color: """
    + DARK_THEME["text"]
    + """ !important;
            }
            .dash-dropdown .Select-menu {
                background-color: """
    + DARK_THEME["input-bg"]
    + """;
            }
            .dash-dropdown .Select-option {
                background-color: """
    + DARK_THEME["input-bg"]
    + """;
                color: """
    + DARK_THEME["text"]
    + """;
            }
            .dash-dropdown .Select-option.is-selected {
                background-color: """
    + DARK_THEME["primary"]
    + """;
            }
            .dash-dropdown .Select-option.is-focused {
                background-color: rgba(0,123,255,0.2);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""
)


# 回调函数：处理开方按钮
@app.callback(
    Output(f"input-4", "value"),
    [Input(f"sqrt-btn-4", "n_clicks")],
    [State(f"input-4", "value")],
)
def update_sqrt_value(n_clicks, value):
    if n_clicks is None or value is None or value.strip() == "":
        return dash.no_update
    try:
        # 如果输入已经是 np.sqrt 格式，提取内部值
        if value.startswith("np.sqrt(") and value.endswith(")"):
            value = value[8:-1]
        # 计算开方值
        result = f"np.sqrt({value})"
        return result
    except:
        return dash.no_update


# 主回调函数：更新图表
@app.callback(
    Output("output", "children"),  # 输出到 Div
    [
        Input("submit-btn", "n_clicks"),
        Input("clear-btn", "n_clicks"),
        Input("chart-options", "value"),
    ],
    [State(f"input-0-start", "value"), State(f"input-0-end", "value")]
    + [State(f"input-{i}", "value") for i in range(1, len(paran))],
)
def update_graph(
    submit_clicks, clear_clicks, chart_options, start_val, end_val, *other_args
):
    global global_fig

    # 获取触发回调的组件
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # 如果点击了清除按钮，重置图表
    if trigger_id == "clear-btn":
        global_fig = go.Figure()
        return html.Div(
            "图表已清除，请重新绘制",
            style={"color": DARK_THEME["text"], "padding": "20px"},
        )

    # 如果点击了绘制按钮
    if submit_clicks is None or trigger_id != "submit-btn":
        return html.Div(
            '请点击"绘制图表"按钮以生成图表。',
            style={"color": DARK_THEME["text"], "padding": "20px"},
        )

    # 验证第一个参数的输入
    if (
        start_val is None
        or end_val is None
        or start_val.strip() == ""
        or end_val.strip() == ""
    ):
        return html.Div(
            "请输入完整的起始值和结束值", style={"color": "#dc3545", "padding": "20px"}
        )

    # 验证其他输入是否为空
    if any(
        value is None or (isinstance(value, str) and value.strip() == "")
        for value in other_args
    ):
        return html.Div(
            "请确保所有输入框都已填写。", style={"color": "#dc3545", "padding": "20px"}
        )

    try:
        # 处理第一个参数的括号对格式
        param_0_str = f"({start_val}, {end_val})"

        # 转换所有输入值
        converted_values = []

        # 转换第一个参数
        try:
            converted_values.append(
                eval(param_0_str, {"__builtins__": None}, {"np": np})
            )
        except Exception as e:
            return html.Div(
                f"参数格式错误: {str(e)}", style={"color": "#dc3545", "padding": "20px"}
            )

        # 转换其他参数
        for i, value in enumerate(other_args):
            try:
                # 第7个参数 (θ)，转换为 2π 倍
                if i == 6:
                    try:
                        circles = float(value)
                        value = f"{circles} * 2 * np.pi"
                    except:
                        pass

                # 使用 eval 并传递 numpy 模块上下文
                converted_values.append(
                    eval(str(value), {"__builtins__": None}, {"np": np})
                )
            except Exception:
                # 如果转换失败，保留原始字符串（如颜色值）
                converted_values.append(value)

        # 调用函数生成图表数据
        result = CPR.flowers_flower_by_petal_multi(*converted_values)

        # 处理返回结果
        if isinstance(result, tuple) and len(result) == 2:
            x, y = result
            # 创建新的图表
            global_fig = go.Figure()
            global_fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    line=dict(
                        color=(
                            converted_values[-1]
                            if len(converted_values) > 8
                            and isinstance(converted_values[-1], str)
                            else DARK_THEME["primary"]
                        ),
                        width=2,
                    ),
                )
            )
        else:
            # 尝试处理其他可能的返回格式
            global_fig = go.Figure()
            if hasattr(result, "data"):
                for trace in result.data:
                    global_fig.add_trace(trace)
            else:
                raise ValueError("函数返回值格式不正确，无法绘制图表")

        # 更新图表布局
        layout_update = {
            "plot_bgcolor": DARK_THEME["background"],
            "paper_bgcolor": DARK_THEME["background"],
            "width": 800,
            "height": 800,
            "margin": dict(t=30, r=30, b=30, l=30),
            "font": {"color": DARK_THEME["text"]},
        }

        # 根据选项显示/隐藏坐标轴和网格
        xaxis_update = {"dtick": 1}
        yaxis_update = {"dtick": 1}

        if chart_options is None or "show_axes" not in chart_options:
            xaxis_update["visible"] = False
            yaxis_update["visible"] = False

        if chart_options is None or "show_grid" not in chart_options:
            xaxis_update["showgrid"] = False
            yaxis_update["showgrid"] = False

        layout_update["xaxis"] = xaxis_update
        layout_update["yaxis"] = yaxis_update

        global_fig.update_layout(**layout_update)

        return dcc.Graph(figure=global_fig, style={"height": "100%", "width": "100%"})
    except Exception as e:
        # 捕获错误并返回提示
        return html.Div(
            [
                html.H3("错误", style={"color": "#dc3545"}),
                html.P(str(e), style={"color": DARK_THEME["text"]}),
                html.P(
                    "请检查参数格式和值是否正确。",
                    style={"color": DARK_THEME["secondary"]},
                ),
            ],
            style={"padding": "20px"},
        )


# 运行应用
if __name__ == "__main__":
    app.run(debug=True)
