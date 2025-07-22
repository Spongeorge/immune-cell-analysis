import argparse
import sqlite3
from dash import Dash
import dash_bootstrap_components as dbc

from data.loaders import get_frequency_table, get_responder_data, get_baseline_summary
from plotting.responder_boxplots import generate_plots
from layout.main_layout import create_layout
from callbacks.download_callbacks import register_callbacks

parser = argparse.ArgumentParser(description="Run Dash dashboard for clinical trial data.")
parser.add_argument('--db-path', type=str, default='database/trial_data.db',
                    help='Path to the SQLite database file.')
args = parser.parse_args()

app = Dash(__name__, external_stylesheets=[dbc.themes.YETI])
conn = sqlite3.connect(args.db_path)

frequency_table = get_frequency_table(conn)
responder_summary = get_responder_data(conn)
baseline_df, project_counts, response_counts, sex_counts = get_baseline_summary(conn)
plots, plot_labels = generate_plots(responder_summary)

app.layout = create_layout(frequency_table, baseline_df, project_counts, response_counts, sex_counts, plots,
                           plot_labels)
register_callbacks(app, frequency_table, baseline_df)

if __name__ == "__main__":
    app.run(debug=False)
