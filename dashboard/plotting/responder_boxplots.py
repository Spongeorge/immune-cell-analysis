import plotly.graph_objs as go
from dash import dcc
from stats.significance import get_mannwhitneyu_string


def generate_plots(responder_summary):
    plots = []
    plot_labels = []

    for pop in responder_summary['population'].unique():
        subset = responder_summary[responder_summary['population'] == pop]
        responders = subset[subset['response'] == 'yes']['percentage']
        non_responders = subset[subset['response'] == 'no']['percentage']

        plot_labels.append(get_mannwhitneyu_string(responders, non_responders))

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

    return plots, plot_labels
