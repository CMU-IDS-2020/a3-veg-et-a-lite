import altair as alt
import pandas as pd
import streamlit as st

import coin_metrics


# Get data from coin metrics API

@st.cache
def get_data(asset_id, metrics, asset_name):
    rates = coin_metrics.get_reference_rates_pandas(asset_id, metrics)
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


# @st.cache
# def get_exchange_info():
#     return coin_metrics.get_exchange_info()


@st.cache
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


def display_metrics_dropdown(asset_metrics, id_to_info_map, name_to_id_map):
    metric_choices = [id_to_info_map[metric][0] for metric in asset_metrics]

    metric_name = st.sidebar.selectbox('Choose a metric', metric_choices)
    metric_id = name_to_id_map[metric_name]
    metric_description = id_to_info_map[metric_id][1]

    with st.sidebar.beta_expander("See explanations for metric"):
        st.markdown(f"**{metric_name}**")
        st.markdown(metric_description)

    return metric_name, metric_id


def display_metric_scale_checkbox():
    return "symlog" if st.sidebar.checkbox("Convert metric chart to symlog scale") else "linear"


def display_transaction_scale_checkbox():
    return "log" if st.sidebar.checkbox("Convert transaction count to log scale") else "linear"


def get_aggregated_metrics(assets, metric_ids):
    dfs = [get_data(asset_id, metric_ids, asset_name) for asset_name, asset_id, in assets]
    return pd.concat(dfs).dropna()


def display_date_slider(df):
    min_date = min(df["time"]).to_pydatetime()
    max_date = max(df["time"]).to_pydatetime()
    return st.slider("Select Date Range", min_date, max_date, (min_date, max_date))


def filter_metrics_by_date(df, start_date, end_date):
    return df[(df["time"] >= start_date) & (df["time"] <= end_date)]


def display_main_chart(metrics_df, metric_id, metric_name, asset_names, container, scale="linear"):
    # the selection brush oriented on the x-axis
    # important not here had to comment out the interactive function below
    # to convert the graph to static
    brush = alt.selection(type='interval', encodings=['x'])
    base = alt.Chart(metrics_df).properties(width=800)
    chart = base.mark_line().encode(
        x=alt.X("time", type="temporal", title="Time"),
        y=alt.Y(metric_id, type="quantitative", title=metric_name, scale=alt.Scale(type=scale), stack=True),
        opacity=alt.condition(brush, alt.OpacityValue(1), alt.OpacityValue(0.7)),
        tooltip=[alt.Tooltip("time", type="temporal", title="Time"),
                 alt.Tooltip(metric_id, type="quantitative", title=metric_name)],
        color="Name"
    ).add_selection(
        brush
    )
    line = base.mark_rule().encode(
        y=alt.Y(f"average({metric_id}):Q"),
        size=alt.SizeValue(3),
        color="Name"
    ).transform_filter(
        brush
    )

    container.write(chart + line)

    # st.pyplot()


#  We're no longer using this data
def display_exchange_info(assets, start_date, end_date, scale="linear"):
    # TxCnt
    # This is the total transactions
    tran_count_df = get_aggregated_metrics(assets, ["TxCnt"])
    tran_count_df = filter_metrics_by_date(tran_count_df, start_date, end_date)
    tran_count_df["TxCnt"] = tran_count_df["TxCnt"].astype(float)
    tran_count_df = tran_count_df.groupby("Name").agg({"TxCnt": "mean"}).reset_index()

    exchange_info = get_exchange_info()
    exchange_df = pd.DataFrame({"Name": [], "exchanges": [], "num_exchanges": []})

    for asset_name, asset_id in assets:
        relevant_exchanges = get_exchanges_for_asset(exchange_info, asset_id)
        relevant_exchange_names = [exchange["id"] for exchange in relevant_exchanges]
        exchange_df = exchange_df.append(
            {"Name": asset_name, "exchanges": relevant_exchange_names, "num_exchanges": len(relevant_exchange_names)},
            ignore_index=True)

    merged = pd.merge(exchange_df, tran_count_df)

    chart = alt.Chart(merged).mark_point().encode(
        x=alt.X("num_exchanges", title="Number of Exchanges"),
        y=alt.Y("TxCnt", title="Average Transaction Count", scale=alt.Scale(type=scale)),
        tooltip=[alt.Tooltip("Name", type="nominal", title="Asset"),
                 alt.Tooltip("TxCnt", type="quantitative", title="Average Transaction Count"),
                 alt.Tooltip("exchanges", type="nominal", title="Available Exchanges")],
        color="Name"
    ).properties(
        width=600, height=400,
        title="How does the number of exchanges affect the transaction count?"
    )
    st.write(chart)


def display_scatter_matrix(assets, start_date, end_date, available_metrics, id_info_map):
    metrics = ["PriceUSD", "TxCnt", "VtyDayRet30d"]
    usable_metrics = []
    for metric in metrics:
        if metric in available_metrics:
            usable_metrics.append(metric)

    df = get_aggregated_metrics(assets, metrics)
    df = filter_metrics_by_date(df, start_date, end_date)

    usable_metrics_names = []
    for metric in usable_metrics:
        metric_name = id_info_map[metric][0]
        df[metric_name] = df[metric]
        usable_metrics_names.append(metric_name)

    chart = alt.Chart(df).mark_circle().encode(
        x=alt.X(alt.repeat("column"), type="quantitative", scale=alt.Scale(type="log")),
        y=alt.Y(alt.repeat("row"), type="quantitative", scale=alt.Scale(type="log")),
        color="Name:N",
        tooltip=usable_metrics_names
    ).properties(
        width=200,
        height=200
    ).repeat(
        row=usable_metrics_names,
        column=usable_metrics_names
    )

    st.write(chart)


def display_heat_map(assets, start_date, end_date):
    metrics = ['ROI30d']

    df = get_aggregated_metrics(assets, metrics)
    st.write(df)
    df = filter_metrics_by_date(df, start_date, end_date)

    heat = alt.Chart(
        df,
        title="When to BUY? / When to SELL?"
    ).mark_rect().encode(
        x=alt.X('monthdate(time):T', title="Time"),
        y=alt.Y('Name:O', title="Assets"),
        color=alt.Color('ROI30d:Q', title='ROI Index', scale=alt.Scale(scheme="inferno"), aggregate="mean"),
        tooltip=[
            alt.Tooltip('monthdate(time):T', title='Date'),
            alt.Tooltip('ROI30d:Q', title='ROI', aggregate="mean")
        ]
    ).properties(height=500, width=1000)
    st.write(heat)


if __name__ == "__main__":
    display_title_and_info()
    selected_assets_info = display_asset_dropdown()
    if selected_assets_info:
        common_metrics = set.intersection(
            *[set(selected_asset_metric) for _, _, selected_asset_metric in selected_assets_info])

        metrics_info = get_metric_info()
        id_to_info_map, name_to_id_map = get_metric_info_maps(metrics_info)

        selected_metric_name, selected_metric_id = display_metrics_dropdown(common_metrics, id_to_info_map,
                                                                            name_to_id_map)
        selected_scale = display_metric_scale_checkbox()

        metric_df = get_aggregated_metrics([(asset_name, asset_id) for asset_name, asset_id, _ in selected_assets_info],
                                           [selected_metric_id])
        chart_container = st.beta_container()
        selected_start_date, selected_end_date = display_date_slider(metric_df)
        metric_df = filter_metrics_by_date(metric_df, selected_start_date, selected_end_date)
        display_main_chart(metric_df, selected_metric_id, selected_metric_name,
                           [asset_name for asset_name, _, _ in selected_assets_info], chart_container, selected_scale)
        display_scatter_matrix([(asset_name, asset_id) for asset_name, asset_id, _ in selected_assets_info],
                               selected_start_date, selected_end_date, common_metrics, id_to_info_map)
        display_heat_map([(asset_name, asset_id) for asset_name, asset_id, _ in selected_assets_info],
                         selected_start_date, selected_end_date)
    else:
        st.header("Select an asset in the sidebar")
