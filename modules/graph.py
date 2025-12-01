
from shiny import App, ui, render, reactive
import plotly.graph_objects as go
import networkx as nx
import pandas as pd
import base64
from pathlib import Path


from graphCode import G, pos, deg_stats, comm_id, G_viz, communities


deg_map = dict(G.degree())
in_deg_map = dict(G.in_degree())
out_deg_map = dict(G.out_degree())


eig = nx.eigenvector_centrality(G_viz, max_iter=1000)
clust = nx.clustering(G_viz)
community_of = comm_id

#  DataFrame
df = pd.DataFrame(
    {
        "node": list(G.nodes()),
        "degree": [deg_map[n] for n in G.nodes()],
        "in_degree": [in_deg_map[n] for n in G.nodes()],
        "out_degree": [out_deg_map[n] for n in G.nodes()],
        "eigenvector": [eig.get(n, 0.0) for n in G.nodes()],
        "clustering": [clust.get(n, 0.0) for n in G.nodes()],
        "community": [community_of.get(n, -1) for n in G.nodes()],
    }
)


_static_dir = Path(__file__).parent / "static_results"
def _img_data_uri(name: str) -> str | None:
    p = _static_dir / name
    if p.exists():
        b = p.read_bytes()
        return "data:image/png;base64," + base64.b64encode(b).decode("ascii")
    return None

_degree_img = _img_data_uri("degree_distribution.png")
_centrality_img = _img_data_uri("centrality_findings.png")
_community_img = _img_data_uri("community_detection.png")

edges_x, edges_y = [], []
for u, v in G.edges():
    ux, uy = pos[u]
    vx, vy = pos[v]
    edges_x += [ux, vx, None]
    edges_y += [uy, vy, None]

# Slider
_stats = deg_stats(G)
max_deg = int(_stats.get("max_deg", _stats.get("max_degrees", max(deg_map.values()) if deg_map else 0)))

# -----------------------------
# 2) Define the Shiny UI
# -----------------------------
app_ui = ui.page_fluid(
    ui.navset_tab(
        ui.nav_panel("Home",
        ui.div(
            ui.h1("Math Topics", class_="text-center", style="font-size: 4rem; font-weight: bold; margin-top: 10rem; margin-bottom: 3rem;"),
            ui.p("Jacob Lembach, Nathan Brown, Sam Ly", class_="text-center", style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;"),
            ui.div(
                ui.h4("About this project", style="text-align:center; color:#2f4a5a; margin-top:1rem;"),
                ui.p(
                    "Mathematics is often described as a hierarchical and interconnected body of knowledge, where foundational concepts support more advanced theories and applications. "
                    "This project explores the structural organization of mathematical knowledge by analyzing it as a network. Using Wikipedia's mathematical articles as a representative sample for the global landscape of mathematical thought, "
                    "we constructed a directed graph where nodes represent mathematical topics and edges represent hyperlinks between articles.",
                    style="max-width: 80%; margin-left: auto; margin-right: auto; font-size: 1.05rem; line-height:1.4; color:#333;"
                ),
                ui.p(
                    "The purpose of this analysis is to gain insight into how mathematical concepts can reveal which ideas are foundational and how subfields cluster together. This analysis has educational applications by identifying central topics along with central communities that reveal the natural groupings within mathematics.",
                    style="max-width: 80%; margin-left: auto; margin-right: auto; font-size: 1.0rem; line-height:1.4; color:#333; margin-bottom: 1rem;"
                ),
                ui.h5("Research questions", style="text-align:center; color:#2f4a5a; margin-top:0.5rem;"),
                ui.tags.ul(
                    ui.tags.li("Which mathematical topics are the most central or influential in the overall structure of mathematics?"),
                    ui.tags.li("Are there distinct clusters or communities of related topics (e.g., pure vs. applied mathematics, discrete vs. continuous)?"),
                    ui.tags.li("Does the mathematical knowledge network exhibit properties similar to known network models (small-world, scale-free)?"),
                    style="max-width: 80%; margin-left: auto; margin-right: auto; color:#222; font-size:0.98rem; text-align:left; padding-left: 1.1rem;"
                ),
                style="padding-bottom: 3rem;",
            ),
        )
    ),
    ui.nav_panel("Visualization",
        ui.layout_sidebar(
            ui.sidebar(
                ui.h5("Graph Visualization"),
                ui.input_slider(
                    "min_deg", "Min degree filter",
                    min=0, max=max_deg, value=0, step=1,
                ),
                ui.input_select(
                    "color_by", "Color nodes by",
                    choices={
                        "degree": "Degree",
                        "eigenvector": "Eigenvector Centrality",
                        "community": "Community",
                    },
                    selected="community",
                ),
                ui.input_checkbox("show_labels", "Show node labels", False),
                ui.input_checkbox("fix_aspect", "Fix aspect ratio (1:1)", True),
            ),
            ui.h3("Interactive Network Visualization"),
            ui.output_ui("graph_ui"),
            ui.p("Use your mouse to zoom and pan. Adjust filters and color options in the sidebar."),
        )
    ),
    ui.nav_panel("Data",
        ui.layout_sidebar(
            ui.sidebar(
                ui.h5("Selection Menu"),
                ui.input_radio_buttons(
                    "choice_type",
                    "I want to choose a...",
                    choices={"metric": "Metric", "community": "Community"},
                    selected="metric",
                ),
                ui.output_ui("chooser"),
            ),
            ui.h3("Selection Menu Results"),
            ui.p("Pick a metric or a community on the left; summary and table will update here."),
            ui.output_text_verbatim("summary"), 
            ui.output_table("preview"),
        )
    )
    ,
    ui.nav_panel("Graphs",
        ui.layout_sidebar(
            ui.sidebar(
                ui.h5("Metric plots & filters"),
                ui.input_select(
                    "metric_choice", "Metric to inspect",
                    {
                        "degree": "Degree (total)",
                        "in_degree": "In-Degree",
                        "out_degree": "Out-Degree",
                        "eigenvector": "Eigenvector Centrality",
                        "clustering": "Clustering Coefficient",
                    },
                    selected="degree",
                ),
                # optional community filter
                ui.input_select(
                    "metric_comm",
                    "Limit to community",
                    # community choices will be filled server-side if needed, but provide a default 'All'
                    choices={"all": "All communities", **{str(c): f"Community {c}" for c in sorted(df['community'].unique()) if c >= 0}},
                    selected="all",
                ),
                ui.input_checkbox("metric_log", "Log scale on x-axis", False),
            ),
            ui.h3("Metric histogram"),
            ui.output_ui("metric_hist"),
            ui.h3("Metric vs Degree scatter"),
            ui.output_ui("metric_scatter"),
            ui.h3("Metric summary"),
            ui.output_text_verbatim("metric_summary"),
            ui.output_table("metric_table"),
        )
    )
    ,
    ui.nav_panel("Results",
        ui.layout_sidebar(
            ui.sidebar(
                ui.h5("Summary & figures"),
            ),
            ui.tags.div(
                ui.tags.img(src=_degree_img or "static_results/degree_distribution.png", style="max-width: 100%; height: auto; border: 1px solid #ddd;"),
                style="margin-bottom: 2rem;",
            ),

            ui.h2("Centrality Findings", style="color: #2f4a5a; margin-top: 2rem;"),
            ui.tags.div(
                ui.tags.img(src=_centrality_img or "static_results/centrality_findings.png", style="max-width: 100%; height: auto; border: 1px solid #ddd;"),
            ),

            ui.h2("Community Detection Results", style="color: #2f4a5a; margin-top: 2rem;"),
            ui.tags.div(
                ui.tags.img(src=_community_img or "static_results/community_detection.png", style="max-width: 100%; height: auto; border: 1px solid #ddd;"),
            ),
        )
    )
    )
)

# -----------------------------
# 3) Server logic 
# -----------------------------
def server(input, output, session):

    # Filter nodes by min degree
    @reactive.calc
    def filtered_nodes():
        m = input.min_deg()
        return [n for n, d in deg_map.items() if d >= m]

    @output
    @render.ui
    def graph_ui():
        nodes = filtered_nodes()
        node_set = set(nodes)

        # choose color
        color_by = input.color_by()

        # build node arrays
        x = [pos[n][0] for n in nodes]
        y = [pos[n][1] for n in nodes]

        # color values per node
        if color_by == "degree":
            colors = [deg_map.get(n, 0) for n in nodes]
            colorbar_title = "degree"
        elif color_by == "eigenvector":
            colors = [eig.get(n, 0.0) for n in nodes]
            colorbar_title = "eigenvector"
        else: 
            colors = [community_of.get(n, 0) for n in nodes]
            colorbar_title = "community"

        # labels and hover text
        labels = [str(n) for n in nodes] if input.show_labels() else None
        hovertext = [
            f"node = {n}<br>degree = {deg_map.get(n, 0)}<br>eigenvector = {eig.get(n, 0.0):.3f}<br>community = {community_of.get(n, -1)}"
            for n in nodes
        ]

        # rebuild edges 
        fx, fy = [], []
        for u, v in G.edges():
            if u in node_set and v in node_set:
                ux, uy = pos[u]
                vx, vy = pos[v]
                fx += [ux, vx, None]
                fy += [uy, vy, None]

        # edge layer
        edge_trace = go.Scatter(
            x=fx if nodes else [], y=fy if nodes else [],
            mode="lines",
            line=dict(width=1),
            hoverinfo="skip",
            showlegend=False,
        )

        # node layer
        node_trace = go.Scatter(
            x=x, y=y,
            mode="markers+text" if input.show_labels() else "markers",
            text=labels,
            textposition="top center",
            marker=dict(
                size=12,
                color=colors,
                showscale=True,
                colorbar=dict(title=colorbar_title),
            ),
            hoverinfo="text",
            hovertext=hovertext,
            showlegend=False,
        )

        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        if input.fix_aspect():
            fig.update_yaxes(scaleanchor="x", scaleratio=1)

        return ui.HTML(fig.to_html(include_plotlyjs="cdn", full_html=False))


    
    # Dynamically generate the second dropdown based on "metric" vs "community".
    @output
    @render.ui
    def chooser():
        if input.choice_type() == "metric":
            # If "metric", provide a dropdown of columns to choose from.
            return ui.input_select(
                "metric",
                "Metric",
                {
                    "degree": "Degree (Total)",
                    "in_degree": "In-Degree",
                    "out_degree": "Out-Degree",
                    "eigenvector": "Eigenvector Centrality",
                    "clustering": "Clustering Coefficient",
                },
                selected="degree",
            )
        else:
            # If "community", list unique community ids discovered in the graph.
            comm_choices = {str(c): f"Community {c}" for c in sorted(df["community"].unique()) if c >= 0}
            if not comm_choices:
                comm_choices = {"0": "Community 0"}
            first_key = next(iter(comm_choices.keys()))
            return ui.input_select("comm", "Community", comm_choices, selected=first_key)

    # A short textual summary; content depends on which "choice_type" is active.
    @output
    @render.text
    def summary():
        if input.choice_type() == "metric":
            m = input.metric()
            return f"Selected metric: {m}. Mean={df[m].mean():.3f}, Std={df[m].std():.3f}, Min={df[m].min():.3f}, Max={df[m].max():.3f}"
        else:
            c = int(input.comm())
            size = int((df["community"] == c).sum())
            return f"Selected community: {c}. Size={size} nodes."

   
    @output
    @render.table
    def preview():
        if input.choice_type() == "metric":
            m = input.metric()
            return df[["node", m]].sort_values(m, ascending=False).head(10)
        else:
            c = int(input.comm())
            comm_df = df[df["community"] == c][["node", "degree", "eigenvector", "clustering"]].head(10)
            return comm_df if not comm_df.empty else pd.DataFrame({"node": [], "degree": [], "eigenvector": [], "clustering": []})

    # -----------------------------
    # Metrics tab outputs
    # -----------------------------

    @output
    @render.ui
    def metric_hist():
        m = input.metric_choice()
        comm = input.metric_comm()
        log_x = input.metric_log()

        # subset the dataframe
        subset = df if comm == "all" else df[df["community"] == int(comm)]
        vals = subset[m].dropna().tolist() if not subset.empty else []

        # build histogram
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=vals, nbinsx=40, marker_color="#636EFA"))
        fig.update_layout(title=f"Distribution of {m}", xaxis_title=m, yaxis_title="Count", bargap=0.05, template="plotly_white")
        if log_x:
            fig.update_xaxes(type="log")

        return ui.HTML(fig.to_html(include_plotlyjs="cdn", full_html=False))

    @output
    @render.ui
    def metric_scatter():
        m = input.metric_choice()
        comm = input.metric_comm()

        subset = df if comm == "all" else df[df["community"] == int(comm)]

        # pick scatter y metric
        y_metric = m if m != "degree" else "eigenvector"

        x = subset["degree"].tolist() if not subset.empty else []
        y = subset[y_metric].tolist() if not subset.empty else []
        nodes = subset["node"].tolist() if not subset.empty else []

        fig = go.Figure()
        hovertext = [f"node={n}<br>degree={int(d)}<br>{y_metric}={float(v):.4f}" for n, d, v in zip(nodes, x, y)] if nodes else []
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker=dict(color="#EF553B", size=8, opacity=0.8),
            hovertext=hovertext,
            hoverinfo="text",
        ))

        fig.update_layout(title=f"{y_metric} vs degree", xaxis_title="degree", yaxis_title=y_metric, template="plotly_white")
        return ui.HTML(fig.to_html(include_plotlyjs="cdn", full_html=False))

    @output
    @render.text
    def metric_summary():
        m = input.metric_choice()
        comm = input.metric_comm()
        subset = df if comm == "all" else df[df["community"] == int(comm)]
        if subset.empty:
            return f"Selected metric: {m}. No data in selection."
        return f"Selected metric: {m}. Mean={subset[m].mean():.4f}, Std={subset[m].std():.4f}, Min={subset[m].min():.4f}, Max={subset[m].max():.4f}"

    @output
    @render.table
    def metric_table():
        m = input.metric_choice()
        comm = input.metric_comm()
        subset = df if comm == "all" else df[df["community"] == int(comm)]
        if subset.empty:
            return pd.DataFrame({"node": [], m: []})
        return subset[["node", m, "degree", "eigenvector"]].sort_values(m, ascending=False).head(10)

app = App(app_ui, server)
