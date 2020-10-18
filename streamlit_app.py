import altair as alt
import pandas as pd
import streamlit as st

import coin_metrics


# Get data from coin metrics API

@st.cache
def get_data(asset_id, asset_name, metric):
    rates = coin_metrics.get_reference_rates_pandas(asset, metric=metric)
    df = pd.DataFrame(data=rates)
    df["time"] = pd.to_datetime(df["time"])
    df['year'] = df['time'].dt.year
    df['month'] = df['time'].dt.month
    # Will be useful for combining dataframes for multiple assets
    df["Name"] = asset_name
    return df


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
    asset_options = [*asset_map.keys()]
    asset_names = st.sidebar.multiselect('Choose some assets', asset_options, default=asset_options[0])
    if asset_names:
        asset_ids_and_metrics = [asset_map[asset_name] for asset_name in asset_names]
        # Sort of a hacky way to end up with a flattened list after the zip
        asset_ids = [asset[0] for asset in asset_ids_and_metrics]
        asset_metrics = [asset[1] for asset in asset_ids_and_metrics]
        return list(zip(asset_names, asset_ids, asset_metrics))
    else:
        return []


def display_metrics_dropdown(asset_metrics):
    common_metrics = set.intersection(*asset_metrics)
    metrics_info = get_metric_info()
    id_to_info_map, name_to_id_map = get_metric_info_maps(metrics_info)
    metric_choices = [id_to_info_map[metric][0] for metric in common_metrics]

    metric_name = st.sidebar.selectbox('Choose a metric', metric_choices)
    metric_id = name_to_id_map[metric_name]
    metric_description = id_to_info_map[metric_id][1]

    with st.sidebar.beta_expander("See explanations for metric"):
        st.markdown(f"**{metric_name}**")
        st.markdown(metric_description)

    return metric_name, metric_id


def get_scale():
    return "symlog" if st.sidebar.checkbox("Convert chart to symlog scale") else "linear"


def display_main_chart(assets_info, metric_id, metric_name, scale="linear"):
    dfs = [get_data(asset_id, metric_id, asset_name) for asset_name, asset_id, _ in assets_info]
    df = pd.concat(dfs)

    chart_container = st.beta_container()

    min_date = min(df["time"]).to_pydatetime()
    max_date = max(df["time"]).to_pydatetime()
    selected_min, selected_max = st.slider("Select Date Range", min_date, max_date, (min_date, max_date))

    filtered_df = df[(df["time"] >= selected_min) & (df["time"] <= selected_max)]

    asset_names = [asset_name for asset_name, _, _ in assets_info]

    # the selection brush oriented on the x-axis
    # important not here had to comment out the interactive function below
    # to convert the graph to static
    brush = alt.selection_interval(encodings=['x'])
    chart = alt.Chart(filtered_df).mark_line().encode(
        x=alt.X("time", type="temporal", title="Time"),
        y=alt.Y(metric_id, type="quantitative", title=metric_name, scale=alt.Scale(type=scale)),
        tooltip=[alt.Tooltip("time", type="temporal", title="Time"),
                 alt.Tooltip(metric_id, type="quantitative", title=metric_name)],
        color="Name"
    ).properties(
        width=700, height=700,
        title=", ".join(asset_names)
    )  #.add_selection(select_year).transform_filter(select_year) # .interactive(bind_y = False)

    chart_container.write(chart.add_selection(brush))

    # st.pyplot()


def display_exchange_info(assets):
    num = len(assets)
    cols = st.beta_columns(num)
    exchange_info = get_exchange_info()
    for ind, col in enumerate(cols):
        asset_name, asset_id = assets[ind]
        relevant_exchanges = get_exchanges_for_asset(exchange_info, asset_id)
        relevant_exchange_names = [exchange["id"] for exchange in relevant_exchanges]
        col.header(f"Available exchanges for {asset_name}")
        for exchange in relevant_exchange_names:
            col.markdown(exchange)


if __name__ == "__main__":
    display_title_and_info()
    selected_assets_info = display_asset_dropdown()
    if selected_assets_info:
        selected_metric_name, selected_metric_id = display_metrics_dropdown(
            [set(selected_asset_metric) for _, _, selected_asset_metric in selected_assets_info])
        selected_scale = get_scale()
        display_main_chart(selected_assets_info, selected_metric_id, selected_metric_name, selected_scale)
        display_exchange_info([(asset_name, asset_id) for asset_name, asset_id, _ in selected_assets_info])
    else:
        st.header("Select an asset in the sidebar")
