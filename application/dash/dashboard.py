from datetime import timedelta
import pandas as pd
import joblib

import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_dashboard(server, prefix=None):
    dash_app = dash.Dash(server=server, routes_pathname_prefix=f"/{prefix}/report/" if prefix else "/report/",
        external_stylesheets=["/static/css/dash.css"]
        )

    def add_common_annotations(fig, yref_stripes="y", yref_annotations="y2"):
        fig.update_layout(
            annotations=list([
                {
                    "x":"2019-11-04 22:19:15+00:00",
                    "y": -2,
                    "text":"cohesion de España",
                    "xref":"x",
                    "yanchor":"bottom",
                    "yref": yref_stripes,
                    "align": "center",
                    "showarrow": False,
                    #"font": {"color": "rgba(183, 129, 118, 1)"},
                },
                {
                    "x":"2019-11-04 23:02:54+00:00",
                    "y": -2,
                    "text":"economía",
                    "xref":"x",
                    "yanchor":"bottom",
                    "yref": yref_stripes,
                    "align": "center",
                    "showarrow": False,
                    #"font": {"color": "rgba(181, 137, 170, 1)"},
                },
                {
                    "x":"2019-11-04 23:30:00+00:00",
                    "y": -2,
                    "text":"p. social",
                    "xref":"x",
                    "yanchor":"bottom",
                    "yref": yref_stripes,
                    "align": "center",
                    "showarrow": False,
                    #"font": {"color": "rgba(240, 179, 197, 1)"},
                },
                {
                    "x":"2019-11-05 00:03:05+00:00",
                    "y": -2,
                    "text":"calidad dem.",
                    "xref":"x",
                    "yanchor":"bottom",
                    "yref": yref_stripes,
                    "align": "center",
                    "showarrow": False,
                    #"font": {"color": "rgba(187, 150, 75, 1)"},
                },
                {
                    "x":"2019-11-05 00:30:45+00:00",
                    "y": -2,
                    "text":"p. internacional",
                    "xref":"x",
                    "yanchor":"bottom",
                    "yref": yref_stripes,
                    "align": "center",
                    "showarrow": False,
                    #"font": {"color": "rgba(75, 104, 117, 1)"},
                },
                {
                    "x":"2019-11-05 00:47:25+00:00",
                    "y": -2,
                    "text":"m. oro",
                    "xref":"x",
                    "yanchor":"bottom",
                    "yref": yref_stripes,
                    "align": "center",
                    "showarrow": False,
                    #"font": {"color": "rgba(251, 226, 9, 1)"},
                },
                {
                    "x":"2019-11-04 22:00:00+00:00",
                    "y": 102,
                    "text":"inicio del debate",
                    "xref":"x",
                    "yanchor":"bottom",
                    "yref": yref_annotations,
                },
                {
                    "x":"2019-11-04 22:14:30+00:00",
                    "y": 646,
                    "text": "Rivera enseña adoquín",
                    "xref": "x",
                    "yanchor": "top",
                    "yref": yref_annotations,
                },
                {
                    "x":"2019-11-04 22:25:30+00:00",
                    "y": 603,
                    "text": "Rivera enseña Listado Concesiones PP",
                    "xref": "x",
                    "yanchor": "bottom",
                    "yref": yref_annotations,
                },
                {
                    "x":"2019-11-04 22:38:30+00:00",
                    "y": 471,
                    "text": "pausa",
                    "xref": "x",
                    "yanchor": "top",
                    "yref": yref_annotations,
                },
                {
                    "x":"2019-11-04 22:49:20+00:00",
                    "y": 473,
                    "text": "fin pausa",
                    "xref": "x",
                    "yanchor": "bottom",
                    "yref": yref_annotations,
                },
                {
                    "x":"2019-11-04 23:17:15+00:00",
                    "y": 375,
                    "text": "Blanco: 'ninguna candidata mujer'",
                    "xref": "x",
                    "yanchor": "bottom",
                    "yref": yref_annotations,
                },
                {
                    "x":"2019-11-04 23:22:46+00:00",
                    "y": 662,
                    "text": "Iglesias dice 'mamadas'",
                    "xref": "x",
                    "yanchor": "top",
                    "yref": yref_annotations,
                },
                {
                    "x":"2019-11-04 23:43:20+00:00",
                    "y": 450,
                    "text": "pausa",
                    "xref": "x",
                    "yanchor": "bottom",
                    "yref": yref_annotations,
                },
                {
                    "x":"2019-11-04 23:49:50+00:00",
                    "y": 542,
                    "text": "fin pausa",
                    "xref": "x",
                    "yanchor": "top",
                    "yref": yref_annotations,
                },
                {
                    "x":"2019-11-05 00:50:20+00:00",
                    "y": 91,
                    "text":"fin del debate",
                    "xref":"x",
                    "yanchor":"bottom",
                    "yref": yref_annotations,
                }
            ])
        )

        fig.update_layout(
            shapes=[
                dict(
                    #cohesión de España, economía, política sociales e igualdad, calidad democrática, política internacional
                    fillcolor="rgba(183, 129, 118, .2)",
                    line={"width": 0},
                    type="rect",
                    x0="2019-11-04 22:00:00+00:00",
                    x1="2019-11-04 22:38:30+00:00",
                    xref="x",
                    y0=0,
                    y1=1,
                    yref="paper",
                ),
                dict(
                    #economía, política sociales e igualdad, calidad democrática, política internacional
                    fillcolor="rgba(181, 137, 170, .2)",
                    line={"width": 0},
                    type="rect",
                    x0="2019-11-04 22:49:20+00:00",
                    x1="2019-11-04 23:16:48+00:00",
                    xref="x",
                    y0=0,
                    y1=1,
                    yref="paper",
                ),
                dict(
                    #política sociales e igualdad, calidad democrática, política internacional
                    fillcolor="rgba(240, 179, 197, .2)",
                    line={"width": 0},
                    type="rect",
                    x0="2019-11-04 23:16:49+00:00",
                    x1="2019-11-04 23:43:20+00:00",
                    xref="x",
                    y0=0,
                    y1=1,
                    yref="paper",
                ),
                dict(
                    #calidad democrática, política internacional
                    fillcolor="rgba(187, 150, 75, .2)",
                    line={"width": 0},
                    type="rect",
                    x0="2019-11-04 23:49:50+00:00",
                    x1="2019-11-05 00:17:00+00:00",
                    xref="x",
                    y0=0,
                    y1=1,
                    yref="paper",
                ),
                dict(
                    #política internacional
                    fillcolor="rgba(75, 104, 117, .2)",
                    line={"width": 0},
                    type="rect",
                    x0="2019-11-05 00:17:00+00:00",
                    x1="2019-11-05 00:44:30+00:00",
                    xref="x",
                    y0=0,
                    y1=1,
                    yref="paper",
                ),
                dict(
                    #minuto de oro
                    fillcolor="rgba(251, 226, 9, .2)",
                    line={"width": 0},
                    type="rect",
                    x0="2019-11-05 00:44:30+00:00",
                    x1="2019-11-05 00:50:20+00:00",
                    xref="x",
                    y0=0,
                    y1=1,
                    yref="paper",
                ),
            ],
        )

    try:
        a = pd.read_csv(server.config["DASHBOARD_PATH"] + "a.csv", index_col=0)
        resampled = pd.read_csv(server.config["DASHBOARD_PATH"] + "resampled.csv", index_col=0)
        todos_partido = pd.read_csv(server.config["DASHBOARD_PATH"] + "todos_partido.csv", index_col=0)

        resampled2 = joblib.load(server.config["DASHBOARD_PATH"] + "resampled.joblib.pkl")
        resampled2_neg = joblib.load(server.config["DASHBOARD_PATH"] + "resampled_neg.joblib.pkl")
        resampled2_neu = joblib.load(server.config["DASHBOARD_PATH"] + "resampled_neu.joblib.pkl")

    except:
        todos = pd.read_csv(server.config["DASHBOARD_PATH"] + "todos_sentiment_polar.csv", index_col=0)
        todos.created_at = pd.to_datetime(todos.created_at)
        todos = todos.sort_values(by="created_at")


        resampled = todos.copy()
        resampled.index = resampled.created_at + timedelta(hours=1)
        resampled = resampled.resample("30S").mean()
        resampled.to_csv(server.config["DASHBOARD_PATH"] + "resampled.csv")

        a = todos.copy()
        a.index = a.created_at + timedelta(hours=1)
        a = a.resample("30S").count()
        a.to_csv("a.csv")

        etiquetado = pd.read_csv(server.config["DASHBOARD_PATH"] + "etiquetado.csv", dtype=dict(document_sentiment="str", PP="str", Cs="str", PSOE="str", UP="str", VOX="str",
            auto_PP="str", auto_Cs="str", auto_VOX="str", auto_PSOE="str", auto_UP="str",
        ))

        for etiqueta in ["PP", "Cs", "VOX", "PSOE", "UP"]:
            etiquetado.loc[etiquetado[etiqueta].isna(), etiqueta] = etiquetado[f"auto_{etiqueta}"][etiquetado[etiqueta].isna()]
            etiquetado[etiqueta] = etiquetado[etiqueta].fillna("neutral")

        #todoNA = etiquetado.PP.isna() & etiquetado.Cs.isna() & etiquetado.VOX.isna() & etiquetado.PSOE.isna() & etiquetado.UP.isna() & etiquetado.auto_PP.isna() & etiquetado.auto_Cs.isna() & etiquetado.auto_VOX.isna() & etiquetado.auto_PSOE.isna() & etiquetado.auto_UP.isna()

        etiquetado = etiquetado.loc[~etiquetado.tweet_id.isna(), :]
        etiquetado = etiquetado.loc[:, ["tweet_id", "PP", "Cs", "VOX", "PSOE", "UP"]]
        etiquetado.tweet_id = etiquetado.tweet_id.astype("int")
        etiquetado.rename({"tweet_id": "id"}, axis="columns", inplace=True)
        todos_partido = todos.merge(etiquetado, on="id", how="outer")
        todos_partido["partido"] = todos_partido.apply(lambda row: [partido for partido in ["PP", "Cs", "VOX", "PSOE", "UP"] if row[partido] == "positive"], axis="columns")
        todos_partido["partido_negativo"] = todos_partido.apply(lambda row: [partido for partido in ["PP", "Cs", "VOX", "PSOE", "UP"] if row[partido] == "negative"], axis="columns")
        todos_partido["partido_neutral"] = todos_partido.apply(lambda row: [partido for partido in ["PP", "Cs", "VOX", "PSOE", "UP"] if row[partido] == "neutral"], axis="columns")
        todos_partido.to_csv(server.config["DASHBOARD_PATH"] + "todos_partido.csv")

        aux_df = todos_partido.copy()
        aux_df.index = aux_df.created_at + timedelta(hours=1)
        resampled2 = {partido: aux_df.copy().loc[aux_df.partido.map(lambda x: partido in x), :].resample("30S").mean() for partido in ["PP", "Cs", "VOX", "PSOE", "UP"]}
        resampled2_neg = {partido: aux_df.copy().loc[aux_df.partido_negativo.map(lambda x: partido in x), :].resample("30S").mean() for partido in ["PP", "Cs", "VOX", "PSOE", "UP"]}
        resampled2_neu = {partido: aux_df.copy().loc[aux_df.partido_neutral.map(lambda x: partido in x), :].resample("30S").mean() for partido in ["PP", "Cs", "VOX", "PSOE", "UP"]}
        joblib.dump(resampled2, server.config["DASHBOARD_PATH"] + "resampled.joblib.pkl")
        joblib.dump(resampled2_neg, server.config["DASHBOARD_PATH"] + "resampled_neg.joblib.pkl")
        joblib.dump(resampled2_neu, server.config["DASHBOARD_PATH"] + "resampled_neu.joblib.pkl")

    finally:
        fig = go.Figure()
        add_common_annotations(fig)
        
        fig.add_trace(go.Scatter(x=resampled.index, y=resampled.Polar_BERT, name="Polar BERT", yaxis="y"))
        fig.add_trace(go.Scatter(x=resampled.index, y=resampled.Polar_ML, name="Polar ML", yaxis="y"))
        fig.add_trace(go.Scatter(x=resampled.index, y=resampled.Polar_O3, name="Polar O3", yaxis="y"))
        fig.add_trace(go.Scatter(x=a.index, y=a.id, name="Tweet Count", yaxis="y2", line={"color": "#FF6692"}))

        fig.update_layout(
            height=700,
            xaxis=dict({
                "autorange": True,
                "rangeslider": {
                    "autorange": True,
                },
                "type": "date",
            }),
            yaxis={
                "anchor": "x",
                "autorange": True,
                "domain": (0, .7),
                "title": "polarization",
                "linecolor": "#607d8b",
                "side": "left",
            },
            yaxis2={
                "anchor": "x",
                #"autorange": True,
                "range": (0, 700),
                "domain": (.7, 1),
                "title": "no. Tweets",
                "titlefont": {"color": "#FF6692"},
                "tickfont": {"color": "#FF6692"},
                "linecolor": "#FF6692",
                "side": "left",
            },
        )


        fig2 = go.Figure()
        add_common_annotations(fig2, yref_stripes="y1", yref_annotations="y6")

        for i, partido in enumerate(reversed(["PP", "Cs", "VOX", "PSOE", "UP"])):
            fig2.add_trace(go.Scatter(x=resampled2[partido].index, y=resampled2[partido].Polar_BERT, name=f"pos {partido}", yaxis=f"y{i + 1}"))
            fig2.add_trace(go.Scatter(x=resampled2_neu[partido].index, y=resampled2_neu[partido].Polar_BERT, name=f"neu {partido}", yaxis=f"y{i + 1}"))
            fig2.add_trace(go.Scatter(x=resampled2_neg[partido].index, y=resampled2_neg[partido].Polar_BERT, name=f"neg {partido}", yaxis=f"y{i + 1}"))
        
        fig2.add_trace(go.Scatter(x=a.index, y=a.id, name="Tweet Count", yaxis="y6", line={"color": "#FF6692"}))

        fig2.update_layout(
            height=1000,
            xaxis=dict({
                "autorange": True,
                "rangeslider": {
                    "autorange": True,
                },
                "type": "date",
            }),
            yaxis1={
                "anchor": "x",
                "autorange": True,
                "domain": (0, .18),
                "title": "UP polar.",
                "linecolor": "#607d8b",
                "side": "left",
                "range": (-2, 4),
            },
            yaxis2={
                "anchor": "x",
                "autorange": True,
                "domain": (.18, .36),
                "title": "PSOE polar.",
                "linecolor": "#607d8b",
                "side": "left",
                "range": (-2, 4),
            },
            yaxis3={
                "anchor": "x",
                "autorange": True,
                "domain": (.36, .54),
                "title": "VOX polar.",
                "linecolor": "#607d8b",
                "side": "left",
                "range": (-2, 4),
            },
            yaxis4={
                "anchor": "x",
                "autorange": True,
                "domain": (.54, .72),
                "title": "Cs polar.",
                "linecolor": "#607d8b",
                "side": "left",
                "range": (-2, 4),
            },
            yaxis5={
                "anchor": "x",
                "autorange": True,
                "domain": (.72, .9),
                "title": "PP polar.",
                "linecolor": "#607d8b",
                "side": "left",
                "range": (-2, 4),
            },
            yaxis6={
                "anchor": "x",
                "autorange": True,
                "domain": (.9, 1),
                "title": "no. tweets",
                "linecolor": "#607d8b",
                "side": "left",
                "range": (0, 700),
            },
            legend=dict(traceorder="reversed"),
        )


        pie = make_subplots(
            cols=5, specs=[[{"type": "pie"} for _ in range(5)]],
            subplot_titles=["PP", "Cs", "VOX", "PSOE", "UP"]
        )

        for i, etiqueta in enumerate(["PP", "Cs", "VOX", "PSOE", "UP"]):
            e = todos_partido[etiqueta].value_counts()
            pie.add_trace(
                go.Pie(labels=e.index, values=e.values, name=etiqueta, marker={
                    "colors": [
                        "#DB1F48",
                        "#E5DDC8",
                        "#01949A",
                    ]
                }),
                row=1, col=i+1,
            )


        dash_app.layout = html.Div(children=[
            html.H1(children="Polarization Algorithms Comparison"),
            html.Blockquote(children=
                """
                Evolution of general polarization through time. A positive value
                stands for documents with positive polarization meanwhile negative
                values represent documents with negative polarization. Distributions
                are centered in axis OY but they are not normalized, hence we cannot
                compare values of different algorithms (we provide several
                algorithms for comparison purposes). Results are sampled using
                30-second windows and aggregated using the arithmetic mean. Notice
                that the polarization variability is higher when the number of
                tweets is lower and it keeps more stable as the number of tweets
                increases.
                """
            ),
            dcc.Graph(
                id="alg_comparison",
                figure=fig
            ),

            html.H1(children="Tweet Count for each Sentiment Category and Party"),
            html.Blockquote(children=
                """
                Count of tweets for, against and neutral (or w/o information)
                towards each political party. Keep distribution in mind in order
                to better understand the variability of each polarization
                distribution in the following graphs.
                """
            ),
            dcc.Graph(
                id="pies",
                figure=pie,
            ),
            
            html.H1(children="Party Polarization Comparison"),
            html.Blockquote(children=
                """
                Evolution of party polarization through time using BERT DNN. A
                positive value stands for documents with positive polarization
                meanwhile negative values represent documents with negative
                polarization. Distributions are computed using the same algorithm,
                hence it is possible to compare values between labels. For each
                political party, we compute the polarization of those tweets whose
                authors have been categorised for, against and neutral (or w/o info)
                towards the party (posLabel, neuLabel and negLabel respectively).
                Results are sampled using 30-second windows and aggregated using the
                arithmetic mean. Notice that the sentiment variability is higher for
                those labels in which we have a lower number of tweets.
                """
            ),
            dcc.Graph(
                id="party_comparison",
                figure=fig2
            ),
        ])

    return dash_app.server