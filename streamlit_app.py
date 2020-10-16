import altair as alt
import pandas as pd
import streamlit as st

import coin_metrics


# Get data from coin metrics API

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


@st.cache
def get_exchange_info():
    return coin_metrics.get_exchange_info()


def does_exchange_have_asset(exchange, asset_id):
    for asset in exchange["marketsInfo"]:
        if asset["assetIdBase"] == asset_id:
            return True
    return False


@st.cache
def get_exchanges_for_asset(exchanges_info, asset_id):
    return [exchange for exchange in exchanges_info if does_exchange_have_asset(exchange, asset_id)]


# Display charts in streamlit

def display_title_and_info():
    st.title("Let's analyze some crypto data ₿📊.")
    st.write("Can you get rich on crypto?!")


def display_asset_dropdown():
    asset_map = get_asset_info_map()
    asset_name = st.sidebar.selectbox('Choose an asset', [*asset_map.keys()])
    asset_id, asset_metrics = asset_map[asset_name]
    return asset_name, asset_id, asset_metrics


def display_metrics_dropdown(asset_metrics):
    metrics_info = get_metric_info()
    id_to_info_map, name_to_id_map = get_metric_info_maps(metrics_info)
    metric_choices = [id_to_info_map[metric][0] for metric in asset_metrics]

    metric_name = st.sidebar.selectbox('Choose a metric', metric_choices)
    metric_id = name_to_id_map[metric_name]
    metric_description = id_to_info_map[metric_id][1]

    with st.sidebar.beta_expander("See explanations for metric"):
        st.markdown(metric_description)

    return metric_name, metric_id


def display_main_chart(asset_id, asset_name, metric_id, metric_name):
    df = get_price_data(asset_id, metric_id)

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
    )  # .interactive()

    st.write(chart.add_selection(brush))

    # st.pyplot()


def display_exchange_info(asset_id, asset_name):
    exchange_info = get_exchange_info()
    relevant_exchanges = get_exchanges_for_asset(exchange_info, asset_id)
    relevant_exchange_names = [exchange["id"] for exchange in relevant_exchanges]
    st.header(f"Available exchanges for {asset_name}")
    for exchange in relevant_exchange_names:
        st.markdown(exchange)


if __name__ == "__main__":
    display_title_and_info()
    selected_asset_name, selected_asset_id, selected_asset_metrics = display_asset_dropdown()
    selected_metric_name, selected_metric_id = display_metrics_dropdown(selected_asset_metrics)
    display_main_chart(selected_asset_id, selected_asset_name, selected_metric_id, selected_metric_name)
    display_exchange_info(selected_asset_id, selected_asset_name)
