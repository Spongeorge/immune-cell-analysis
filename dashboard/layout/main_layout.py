from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc


def create_layout(frequency_table, baseline_df, project_counts, response_counts, sex_counts, plots, plot_labels):
    return dbc.Container([
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
                    dcc.Markdown(
                        stat_text,
                        className='stat-markdown',
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

        html.Div("Statistically significant results at p < 0.05 are bolded."),
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
