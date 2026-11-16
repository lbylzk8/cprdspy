"""CPR Plotly1 Web App — 全覆盖可视化工具

入口：python app.py  |  访问：http://localhost:8050
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go

from cprdspy import config as plot_config
from components.navbar import MODULES
from components import controls

import pages.arcs    as page_arcs
import pages.circles  as page_circles
import pages.dots     as page_dots
import pages.flowers  as page_flowers
import pages.lines    as page_lines
import pages.spirals  as page_spirals
import pages.stars    as page_stars
import pages.waves    as page_waves

PAGES = {
    "arcs": page_arcs, "circles": page_circles, "dots": page_dots,
    "flowers": page_flowers, "lines": page_lines, "spirals": page_spirals,
    "stars": page_stars, "waves": page_waves,
}

# ── CSS ─────────────────────────────────────────────
THEME_CSS = r"""
:root,[data-theme="classic"]{--bg:#fff;--bg2:#f8f9fa;--text:#1a1a2e;--text2:#6c757d;--border:#e9ecef;--accent:#6366f1;--accent-light:rgba(99,102,241,0.1);--sidebar:#f0f0f5;--card:#fff;--danger:#ef4444;}
[data-theme="dark"]{--bg:#0f0f23;--bg2:#1a1a2e;--text:#e4e4e7;--text2:#a1a1aa;--border:#2d2d5e;--accent:#818cf8;--accent-light:rgba(129,140,248,0.15);--sidebar:#16162e;--card:#1e1e3a;--danger:#f87171;}
[data-theme="deep_sea"]{--bg:#0A192F;--bg2:#112240;--text:#ccd6f6;--text2:#8892B0;--border:#172A45;--accent:#64FFDA;--accent-light:rgba(100,255,218,0.12);--sidebar:#0d1f3c;--card:#112240;--danger:#FF6B6B;}
[data-theme="cyberpunk"]{--bg:#000;--bg2:#0a0a0a;--text:#0F0;--text2:#888;--border:#1A1A1A;--accent:#F0F;--accent-light:rgba(255,0,255,0.12);--sidebar:#050505;--card:#0a0a0a;--danger:#FF1493;}
[data-theme="aurora"]{--bg:#232D3F;--bg2:#2E3A4F;--text:#E5E9F0;--text2:#B0B9C6;--border:#384152;--accent:#88C0D0;--accent-light:rgba(136,192,208,0.12);--sidebar:#1E2838;--card:#2E3A4F;--danger:#B48EAD;}
[data-theme="sunset"]{--bg:#2D142C;--bg2:#3D1E3C;--text:#FFF0E0;--text2:#C08080;--border:#510A32;--accent:#FFA07A;--accent-light:rgba(255,160,122,0.15);--sidebar:#251025;--card:#3D1E3C;--danger:#EE4540;}
[data-theme="forest"]{--bg:#2F4538;--bg2:#3A5444;--text:#E8F0E0;--text2:#AAC0AA;--border:#4A6741;--accent:#8CB369;--accent-light:rgba(140,179,105,0.15);--sidebar:#26382E;--card:#3A5444;--danger:#BC4B51;}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);transition:background .3s,color .3s}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:var(--bg2)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
.app-layout{display:flex;flex-direction:column;min-height:100vh}
.main-area{display:flex;flex:1}
.content-area{flex:1;display:flex;flex-direction:column;overflow:hidden}
.graph-wrap{flex:1;padding:12px;overflow:hidden;display:flex}
.graph-wrap .js-plotly-plot{flex:1}
.sidebar{width:380px;min-width:380px;background:var(--sidebar);border-right:1px solid var(--border);height:calc(100vh-64px);overflow-y:auto;padding:20px;transition:margin-left .3s ease,opacity .3s ease;position:relative;flex-shrink:0}
.sidebar.collapsed{margin-left:-380px;opacity:0;pointer-events:none}
input[type=number]{background:var(--bg)!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:6px!important;padding:4px 8px!important;font-size:13px!important}
.Select-control{background:var(--bg)!important;border-color:var(--border)!important}
.Select-value-label{color:var(--text)!important}
.Select-menu-outer{background:var(--bg)!important;border-color:var(--border)!important}
.Select-option{color:var(--text)!important;background:var(--bg)!important}
.Select-option.is-focused{background:var(--accent-light)!important}
.rc-slider-track{background:var(--accent)!important}
.rc-slider-handle{border-color:var(--accent)!important}
.nav-tab{display:inline-flex;align-items:center;padding:8px 14px;border-radius:8px;font-size:13px;font-weight:600;text-decoration:none;transition:all .2s;white-space:nowrap}
.nav-tab.active{color:var(--accent);background:var(--accent-light)}
.nav-tab:not(.active){color:var(--text2)}
.nav-tab:not(.active):hover{color:var(--text);background:var(--bg2)}
@media(max-width:900px){.sidebar{width:100%!important;min-width:100%!important}.main-area{flex-direction:column}.graph-wrap{height:50vh}}
"""

# ── App ────────────────────────────────────────────
app = Dash(__name__, suppress_callback_exceptions=True,
           update_title="Loading...", title="CPR Plotly1")

app.index_string = f"""<!DOCTYPE html><html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CPR Plotly1</title>{{%favicon%}}{{%css%}}
<script src="/_dash-component-suites/plotly/package_data/plotly.min.js"></script>
<style>{THEME_CSS}</style>
</head><body data-theme="classic">
{{%app_entry%}}
<footer>{{%config%}}{{%scripts%}}{{%renderer%}}</footer>
</body></html>"""

# ── Navbar ─────────────────────────────────────────
def build_navbar(active="arcs"):
    tabs = []
    for m in MODULES:
        is_a = m["id"] == active
        tabs.append(html.A(
            [html.Span(m["icon"], style={"marginRight":"5px"}), m["label"]],
            href=f"/{m['id']}",
            className=f"nav-tab{' active' if is_a else ''}",
        ))
    return html.Nav(
        style={"display":"flex","alignItems":"center","justifyContent":"space-between",
               "padding":"0 20px","height":"64px","background":"var(--bg)",
               "borderBottom":"1px solid var(--border)","position":"sticky","top":"0",
               "zIndex":"1000","backdropFilter":"blur(12px)","flexShrink":"0"},
        children=[
            html.Div([html.Span("CPR",style={"fontSize":"22px","fontWeight":"800","color":"var(--accent)","marginRight":"12px","letterSpacing":"-1px"}),*tabs],
                     style={"display":"flex","alignItems":"center","gap":"2px","overflowX":"auto"}),
            dcc.Dropdown(id="theme-selector",
                options=[{"label":"☀ Classic","value":"classic"},{"label":"🌙 Dark","value":"dark"},
                         {"label":"🌊 Deep Sea","value":"deep_sea"},{"label":"🤖 Cyberpunk","value":"cyberpunk"},
                         {"label":"🌌 Aurora","value":"aurora"},{"label":"🌅 Sunset","value":"sunset"},
                         {"label":"🌲 Forest","value":"forest"}],
                value="classic",clearable=False,searchable=False,
                style={"width":"150px","fontSize":"13px","flexShrink":"0"}),
        ])

# ── Build module page ─────────────────────────────
def build_page(mid):
    """Return the full module page Div."""
    pg = PAGES[mid]
    first_func = next(iter(pg.FUNCTIONS.keys()))
    first_def = pg.FUNCTIONS[first_func]

    return html.Div([
        html.Div([
            # Sidebar
            html.Div([
                html.Button("☰", id=f"{mid}-sidebar-toggle",
                    style={"position":"absolute","top":"10px","right":"-32px","width":"30px","height":"30px",
                           "borderRadius":"0 6px 6px 0","border":"1px solid var(--border)",
                           "background":"var(--sidebar)","color":"var(--text)","cursor":"pointer",
                           "fontSize":"14px","zIndex":"10","display":"flex","alignItems":"center","justifyContent":"center"}),
                dcc.Store(id=f"{mid}-sidebar-toggle-store"),
                html.H2(mid.title(), style={"fontSize":"20px","fontWeight":"700","marginBottom":"16px"}),
                html.Label("Function", style={"fontSize":"11px","fontWeight":"600","color":"var(--text2)",
                           "textTransform":"uppercase","marginBottom":"4px","display":"block"}),
                dcc.Dropdown(id=f"{mid}-func-select",
                    options=[{"label":v["label"],"value":k} for k,v in pg.FUNCTIONS.items()],
                    value=first_func,clearable=False,searchable=False,
                    style={"fontSize":"13px","marginBottom":"16px"}),
                html.Div(id=f"{mid}-params-panel",
                         children=controls.build_panel(mid, first_def)),
            ], id=f"{mid}-sidebar", className="sidebar", style={"position":"relative"}),
            # Graph
            html.Div([
                dcc.Loading(
                    dcc.Graph(id=f"{mid}-graph",style={"height":"100%","width":"100%"},
                              config={"displayModeBar":True,"scrollZoom":True}),
                    type="circle",color="var(--accent)",
                ),
            ], className="graph-wrap"),
        ], className="main-area"),
    ], className="content-area")

# ── Global layout ─────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="theme-store", data="classic"),
    html.Div(id="navbar-container", children=build_navbar("arcs")),
    html.Div(id="page-content"),
], className="app-layout")

# ── Route ─────────────────────────────────────────
@app.callback(
    Output("page-content","children"),
    Output("navbar-container","children"),
    Input("url","pathname"),
)
def route(pathname):
    mid = (pathname or "").lstrip("/").split("/")[0]
    if mid not in PAGES:
        mid = "arcs"
    return build_page(mid), build_navbar(mid)

# ── Theme (clientside) ────────────────────────────
app.clientside_callback(
    "function(theme){if(!theme)return window.dash_clientside.no_update;document.body.setAttribute('data-theme',theme);return theme;}",
    Output("theme-store","data"),
    Input("theme-selector","value"),
)

# ── Sidebar toggle (clientside) ───────────────────
for mid in PAGES:
    app.clientside_callback(
        f"function(n){{if(!n)return window.dash_clientside.no_update;document.getElementById('{mid}-sidebar').classList.toggle('collapsed');return n;}}",
        Output(f"{mid}-sidebar-toggle-store","data"),
        Input(f"{mid}-sidebar-toggle","n_clicks"),
    )

# ── Collect all inputs per module ──────────────────
# Build a mapping: module_id -> list of (component_id, property, param_name)
# where component_id depends on the param type (slider vs dropdown)
MOD_INPUTS = {}
for mid, pg in PAGES.items():
    seen = []
    for fd in pg.FUNCTIONS.values():
        for p in fd["params"]:
            pname = p["name"]
            ptype = p.get("type", "slider")
            pid = f"{mid}-{pname}"
            if ptype == "color":
                cid, prop = f"{pid}-dropdown", "value"
            elif ptype in ("dropdown", "toggle"):
                cid, prop = pid, "value"
            else:
                cid, prop = f"{pid}-slider", "value"
            entry = (cid, prop, pname)
            if entry not in seen:
                seen.append(entry)
    MOD_INPUTS[mid] = seen

# ── func-select → params panel ────────────────────
for mid, pg in PAGES.items():
    @app.callback(
        Output(f"{mid}-params-panel","children"),
        Input(f"{mid}-func-select","value"),
    )
    def on_func_change(func_name, mid=mid, pg=pg):
        return controls.build_panel(mid, pg.FUNCTIONS[func_name])

# ── Master graph callback per module ──────────────
# One callback per module: func-select + theme + ALL param inputs → graph figure
for mid, pg in PAGES.items():
    deps = [Input(f"{mid}-func-select","value"),
            Input("theme-store","data")]
    for cid, prop, pname in MOD_INPUTS[mid]:
        deps.append(Input(cid, prop))

    @app.callback(Output(f"{mid}-graph","figure"), *deps)
    def update_graph(func_name, theme, *values, mid=mid, pg=pg):
        if func_name not in pg.FUNCTIONS:
            return go.Figure()
        fd = pg.FUNCTIONS[func_name]
        # Map param names to their input values
        param_map = {}
        for (cid, prop, pname), val in zip(MOD_INPUTS[mid], values):
            if val is not None:
                param_map[pname] = val
        # Build kwargs: use user value or fallback to default
        kwargs = {}
        for p in fd["params"]:
            pname = p["name"]
            kwargs[pname] = param_map.get(pname, p["default"])

        try:
            plot_config.set_theme(theme or "classic")
            traces = fd["func"](**kwargs)
            if not isinstance(traces, list):
                traces = [traces]
            traces = [t for t in traces if t is not None]
            if not traces:
                fig = go.Figure()
                fig.add_annotation(text="Parameters do not satisfy drawing conditions",
                                   showarrow=False, font=dict(color="var(--text2)",size=14))
            else:
                fig = go.Figure(data=traces)
            plot_config.apply_to_figure(fig)
            return fig
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(text=f"Error: {e}", showarrow=False,
                               font=dict(color="var(--danger)",size=12))
            return fig

# ── Run ──────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8050)
    p.add_argument("--debug", action="store_true", default=True)
    args = p.parse_args()
    print(f"\n  CPR Plotly1 Web App -> http://localhost:{args.port}\n")
    app.run(debug=args.debug, port=args.port)
