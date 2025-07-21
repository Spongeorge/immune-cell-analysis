import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, dcc, html, dash_table, Input, Output, State, no_update, ctx
from scipy.stats import mannwhitneyu
from utils.significance import get_significance_code
import dash_bootstrap_components as dbc

db_path = 'database/trial_data.db'
conn = sqlite3.connect(db_path)


def load_frequency_table():
    df = pd.read_sql_query("""
        SELECT 
            sample_id,
            b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
        FROM samples
        JOIN cell_counts USING(sample_id)
        WHERE sample_type = 'PBMC'
    """, conn)

    melted = df.melt(id_vars=['sample_id'], var_name='population', value_name='count')
    totals = melted.groupby('sample_id')['count'].sum().reset_index(name='total_count')
    summary = melted.merge(totals, on='sample_id')
    summary['percentage'] = (summary['count'] / summary['total_count']) * 100
    summary['percentage'] = summary['percentage'].apply(lambda x: round(x, 4))
    summary = summary.sort_values(by='sample_id')
    summary = summary[['sample_id', 'total_count', 'population', 'count', 'percentage']].rename(
        columns={'sample_id': 'sample'})

    return summary


def responder_data():
    df = pd.read_sql_query("""
        SELECT sample_id, response, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
        FROM samples
        JOIN subjects USING(subject_id)
        JOIN cell_counts USING(sample_id)
        WHERE sample_type = 'PBMC' AND condition_id = 'melanoma' AND treatment_id = 'miraclib'
    """, conn)

    melted = df.melt(id_vars=['sample_id', 'response'], var_name='population', value_name='count')
    totals = melted.groupby('sample_id')['count'].sum().reset_index(name='total_count')
    summary = melted.merge(totals, on='sample_id')
    summary['percentage'] = (summary['count'] / summary['total_count']) * 100
    return summary


def load_baseline_summary():
    df = pd.read_sql_query("""
        SELECT sample_id, project_id, subject_id, response, sex
        FROM samples
        JOIN subjects USING(subject_id)
        WHERE sample_type = 'PBMC' AND time_from_treatment_start = 0 AND condition_id = 'melanoma' AND treatment_id = 'miraclib'
    """, conn)

    project_counts = df.groupby('project_id').size().reset_index(name='num_samples')
    response_counts = df.groupby('response')['subject_id'].nunique().reset_index(name='num_subjects')
    sex_counts = df.groupby('sex')['subject_id'].nunique().reset_index(name='num_subjects')

    return df, project_counts, response_counts, sex_counts


app = Dash(__name__, external_stylesheets=[dbc.themes.YETI])

frequency_table = load_frequency_table()
responder_summary = responder_data()

baseline_df, project_counts, response_counts, sex_counts = load_baseline_summary()

plots = []
plot_labels = []

for pop in responder_summary['population'].unique():
    subset = responder_summary[responder_summary['population'] == pop]
    responders = subset[subset['response'] == 'yes']['percentage']
    non_responders = subset[subset['response'] == 'no']['percentage']

    if len(responders) > 0 and len(non_responders) > 0:
        u_stat, p_val = mannwhitneyu(responders, non_responders, alternative='two-sided')
        stat_text = f"""Mann-Whitney U Test\nU={int(u_stat)}, p={p_val:.3e} {get_significance_code(p_val)}\nn1={len(responders)}, n2={len(non_responders)}"""
    else:
        stat_text = "Insufficient data"

    plot_labels.append(stat_text)

    fig = go.Figure()

    fig.add_trace(go.Box(
        y=responders,
        name='yes',
        boxpoints='all',
        pointpos=0,
        jitter=1,
        marker_color='royalblue',
        marker_opacity=.1
    ))

    fig.add_trace(go.Box(
        y=non_responders,
        name='no',
        boxpoints='all',
        pointpos=0,
        jitter=1,
        marker_color='peru',
        marker_opacity=.1
    ))

    fig.update_layout(
        title=pop,
        height=300,
        margin=dict(t=30, b=0, l=0, r=0),
        showlegend=False
    )

    plots.append(dcc.Graph(
        figure=fig,
        style={'display': 'inline-block', 'width': '100%', 'verticalAlign': 'top'}
    ))

app.layout = dbc.Container([
    html.H2("Initial Analysis - Data Overview"),
    dash_table.DataTable(
        data=frequency_table.to_dict('records'),
        columns=[{"name": i, "id": i} for i in frequency_table.columns],
        page_size=10
    ),
    html.Button("Download CSV", id="btn-download-frequency"),
    dcc.Download(id="download-dataframe-csv"),
    html.Hr(),

    html.H2("Statistical Analysis"),
    html.Div([
        html.Div([
            html.Div([
                fig,
                html.Div(
                    stat_text,
                    style={
                        'textAlign': 'center',
                        'fontSize': '14px',
                        'whiteSpace': 'pre-wrap',
                        'userSelect': 'text',
                        'padding': '10px',
                        'border': '1px solid #ccc',
                        'borderRadius': '8px',
                        'backgroundColor': '#f9f9f9',
                        'marginTop': '10px',
                        'width': '100%',
                    }
                )
            ], style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'marginRight': '20px',
                'padding': '10px',
                'width': '320px',  # fixed width instead of 100%
                'minWidth': '100px'  # optional minimum width
            })
            for fig, stat_text in zip(plots, plot_labels)
        ],
            style={
                'display': 'flex',
                'flexDirection': 'row',
                'justifyContent': 'center',
                'flexWrap': 'wrap'
            })
    ]),

    html.Div("Signif. codes: 0.001 \'***\' | 0.01 \'**\' | 0.05 \'*\' | 0.1 \'.\' | 1 \'ns\'"),

    html.Hr(),

    html.H2("Data Subset Analysis"),
    html.H4("Melanoma PBMC samples at baseline from patients treated with Miraclib."),

    dash_table.DataTable(
        data=baseline_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in baseline_df.columns],
        page_size=10
    ),
    dcc.Store(id="stored-baseline-df", data=baseline_df.to_dict("records")),
    dcc.Store(id="stored-filename", data="baseline_data.csv"),

    html.Button("Download CSV", id="btn-download-baseline"),
    dcc.Download(id="download-dataframe-csv"),

    html.Div([
        html.Div([
            html.H4("Samples per Project", style={"textAlign": "center"}),
            dash_table.DataTable(
                data=project_counts.to_dict('records'),
                columns=[{"name": i, "id": i} for i in project_counts.columns]
            ),
        ], style={"flex": "1", "margin": "10px"}),

        html.Div([
            html.H4("Responders vs Non-Responders", style={"textAlign": "center"}),
            dash_table.DataTable(
                data=response_counts.to_dict('records'),
                columns=[{"name": i, "id": i} for i in response_counts.columns]
            ),
        ], style={"flex": "1", "margin": "10px"}),

        html.Div([
            html.H4("Sex Breakdown", style={"textAlign": "center"}),
            dash_table.DataTable(
                data=sex_counts.to_dict('records'),
                columns=[{"name": i, "id": i} for i in sex_counts.columns]
            ),
        ], style={"flex": "1", "margin": "10px"}),
    ], style={"display": "flex", "flexDirection": "row"})
], className="p-4")


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-download-frequency", "n_clicks"),
    Input("btn-download-baseline", "n_clicks"),
    prevent_initial_call=True
)
def download_csv(n1, n2):
    triggered_id = ctx.triggered_id

    if triggered_id == "btn-download-frequency":
        df = frequency_table
        filename = "frequency_data.csv"
    elif triggered_id == "btn-download-baseline":
        df = baseline_df
        filename = "baseline_melanoma_miraclib_pbmc_samples.csv"
    else:
        return no_update

    return dcc.send_data_frame(df.to_csv, filename=filename, index=False)



if __name__ == '__main__':
    app.run(debug=True)
