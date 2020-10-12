import altair as alt
import pandas as pd
import streamlit as st

import coin_metrics

st.title("Let's analyze some Penguin Data 🐧📊.")


@st.cache  # add caching so we load the data only once
def load_data():
    # Load the penguin data from https://github.com/allisonhorst/palmerpenguins.
    penguins_url = "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/v0.1.0/inst/extdata/penguins.csv"
    return pd.read_csv(penguins_url)


@st.cache
def get_price_data(asset, metric):
    rates = coin_metrics.get_reference_rates(asset, metric=metric)
    return pd.DataFrame(data=rates)


@st.cache
def get_assets():
    return coin_metrics.get_assets()


@st.cache
def get_metrics():
    return coin_metrics.get_metrics()


@st.cache
def get_metric_info():
    metrics = coin_metrics.get_metric_info()
    return pd.DataFrame(data=metrics)


@st.cache
def get_asset_names():
    assets = coin_metrics.get_asset_full_names()
    return pd.DataFrame(data=assets)


if __name__ == "__main__":
    selected_asset = st.selectbox('Choose an asset', get_assets())

    asset_names = get_asset_names()
    st.write(asset_names)

    selected_metric = st.selectbox('Choose a metric', get_metrics())

    metric_info = get_metric_info()
    st.write(metric_info)

    df = get_price_data(selected_asset, selected_metric)

    # st.write("Let's look at raw data in the Pandas Data Frame.")

    # st.write(df)

    # chart = alt.Chart(df).mark_point().encode(
    #     x=alt.X("body_mass_g", scale=alt.Scale(zero=False)),
    #     y=alt.Y("flipper_length_mm", scale=alt.Scale(zero=False)),
    #     color=alt.Y("species")
    # ).properties(
    #     width=600, height=400
    # ).interactive()
    #

    chart = alt.Chart(df).mark_line().encode(
        x=alt.X("time", type="temporal"),
        y=alt.Y(selected_metric, type="quantitative"),
        tooltip=["time", selected_metric]
    ).properties(
        width=1000, height=1000
    ).interactive()

    st.write(chart)
