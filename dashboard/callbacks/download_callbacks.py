from dash import Output, Input, no_update, dcc, ctx


def register_callbacks(app, frequency_table, baseline_df):
    @app.callback(
        Output("download-dataframe-csv", "data"),
        Input("btn-download-frequency", "n_clicks"),
        Input("btn-download-baseline", "n_clicks"),
        prevent_initial_call=True
    )
    def download_csv(_, __):
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
