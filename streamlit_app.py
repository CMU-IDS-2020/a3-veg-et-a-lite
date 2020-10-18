import altair as alt
import pandas as pd
import streamlit as st

import coin_metrics


@st.cache
def get_price_data(asset, metric):
    rates = coin_metrics.get_reference_rates_pandas(asset, metric=metric)
    return pd.DataFrame(data=rates)


@st.cache
def get_assets():
    return coin_metrics.get_assets()


@st.cache
def get_metrics():
    return coin_metrics.get_metrics()


@st.cache
def get_metric_info():
    return coin_metrics.get_metric_info()


@st.cache
def get_asset_info_map():
    asset_info = coin_metrics.get_asset_info()
    res = {}
    for asset in asset_info:
        name = asset["name"]
        asset_id = asset["id"]
        metrics = asset["metrics"]
        res[name] = (asset_id, metrics)
    return res


@st.cache
def get_metric_info_maps(metric_info):
    # Map of metric id to description and name
    id_to_info = {}
    # Map of metric name to id
    name_to_id = {}
    for metric in metric_info:
        name = metric["name"]
        metric_id = metric["id"]
        description = metric["description"]

        name_to_id[name] = metric_id
        id_to_info[metric_id] = (name, description)
    return id_to_info, name_to_id


def title_and_info():
    st.title("Let's analyze some crypto data ₿📊.")
    st.write("Can you get rich on crypto?!")


def asset_dropdown():
    asset_map = get_asset_info_map()
    asset_name = st.sidebar.selectbox('Choose an asset', [*asset_map.keys()])
    asset_id, asset_metrics = asset_map[asset_name]
    return asset_name, asset_id, asset_metrics


def metrics_dropdown(asset_metrics):
    metrics_info = get_metric_info()
    id_to_info_map, name_to_id_map = get_metric_info_maps(metrics_info)
    metric_choices = [id_to_info_map[metric][0] for metric in asset_metrics]

    metric_name = st.sidebar.selectbox('Choose a metric', metric_choices)
    metric_id = name_to_id_map[metric_name]
    metric_description = id_to_info_map[metric_id][1]

    with st.sidebar.beta_expander("See explanations for metric"):
        st.markdown(metric_description)

    return metric_name, metric_id


def main_chart(asset_id, asset_name, metric_id, metric_name):
    df = get_price_data(asset_id, metric_id)
    df['year'] = df['time'].str[:4].astype(int)
    df['month'] = df['time'].str[5:7].astype(int)
    st.write(df.head(100000)) # Only for testing
    slider_year = alt.binding_range(min=2017, max=2020, step=1)
    select_year = alt.selection_single(name="year", fields=['year'], bind=slider_year, init={'year': 2020})
    # the selection brush oriented on the x-axis
    # important not here had to comment out the interactive function below
    # to convert the graph to static
    brush = alt.selection_interval(encodings=['x'])
    chart = alt.Chart(df).mark_line().encode(
        x=alt.X("time", type="temporal", title="Time"),
        y=alt.Y(metric_id, type="quantitative", title=metric_name),
        tooltip=[alt.Tooltip("time", type="temporal", title="Time"),
                 alt.Tooltip(metric_id, type="quantitative", title=metric_name)],

    ).properties(
        width=900, height=1000,
        title=asset_name
    ).add_selection(select_year).transform_filter(select_year) # .interactive(bind_y = False)

    st.write(chart.add_selection(brush))

    # st.pyplot()


if __name__ == "__main__":
    title_and_info()
    selected_asset_name, selected_asset_id, selected_asset_metrics = asset_dropdown()
    selected_metric_name, selected_metric_id = metrics_dropdown(selected_asset_metrics)
    main_chart(selected_asset_id, selected_asset_name, selected_metric_id, selected_metric_name)
