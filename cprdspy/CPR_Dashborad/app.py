from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.graph_objects as go
import CPRSP as CPR
import inspect
import dash
import numpy as np

# 初始化 Dash 应用
app = Dash()

# 动态生成输入框，根据函数参数数量
paran = inspect.signature(CPR.flowers_flower_by_petal_multi).parameters
inputs = [
    dcc.Input(id=f"input-{i}", type="text", placeholder=f"参数 {i + 1}")
    for i in range(len(paran))
]

# 初始化全局图表对象
global_fig = go.Figure()

# 定义应用布局
app.layout = html.Div(
    [
        html.H1(children="CPR Dash App", style={"textAlign": "center"}),
        html.Div(
            [
                # 左侧输入框
                html.Div(
                    children=inputs
                    + [
                        html.Button(
                            "绘制图表", id="submit-btn", style={"marginTop": "10px"}
                        ),
                        html.Button(
                            "清除图表",
                            id="clear-btn",
                            style={"marginTop": "10px", "marginLeft": "10px"},
                        ),
                    ],
                    style={"flex": "1", "padding": "10px"},
                ),
                # 右侧输出图表
                html.Div(
                    id="output",
                    style={"flex": "2", "paddingLeft": "10px", "width": "100%"},
                ),
            ],
            style={"display": "flex"},
        ),
    ]
)


# 定义回调函数
@app.callback(
    Output("output", "children"),  # 输出到 Div
    [Input("submit-btn", "n_clicks"), Input("clear-btn", "n_clicks")],
    [State(f"input-{i}", "value") for i in range(len(paran))],
)
def update_graph(submit_clicks, clear_clicks, *input_values):
    global global_fig

    # 如果点击了清除按钮，重置图表
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("clear-btn"):
        global_fig = go.Figure()  # 重置图表
        return "图表已清除，请重新绘制。"

    # 如果点击了绘制按钮
    if submit_clicks is None:
        return "请点击“绘制图表”按钮以生成图表。"

    # 验证输入是否为空
    if any(value is None or value.strip() == "" for value in input_values):
        return "请确保所有输入框都已填写。"

    try:
        # 转换输入值为适当的类型（支持 numpy 表达式）
        converted_values = []
        for value in input_values:
            try:
                # 使用 eval 并传递 numpy 模块上下文
                converted_values.append(eval(value, {"__builtins__": None}, {"np": np}))
            except Exception:
                # 如果转换失败，保留原始字符串
                converted_values.append(value)

        # 调用函数生成新的图表数据
        new_fig = CPR.flowers_flower_by_petal_multi(*converted_values)

        # 将新数据添加到全局图表中
        for trace in new_fig.data:
            global_fig.add_trace(trace)

        # 更新布局
        global_fig.update_layout(
            xaxis=dict(dtick=1), yaxis=dict(dtick=1), width=800, height=800
        )

        return dcc.Graph(
            figure=global_fig, style={"height": "100%", "width": "100%"}
        )  # 返回图表
    except Exception as e:
        # 捕获错误并返回提示
        return f"生成图表时出错：{str(e)}"


# 运行应用
if __name__ == "__main__":
    app.run(debug=True)
