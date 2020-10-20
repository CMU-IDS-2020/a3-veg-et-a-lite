import json
import re

import requests

# API docs can be found here: https://docs.coinmetrics.io/api/v2/

COIN_METRICS_API = "https://community-api.coinmetrics.io/v2"
ASSETS_ENDPOINT = COIN_METRICS_API + "/assets"


def get(url, params=None):
    """ Performs a GET request to the given url with supplied params. If an error happens that will be printed to the
    console and None is returned """
    response = requests.get(url, params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f"Unable to perform REST call {url} with params {params}. Status {response.status_code}. Message: {response.text}")
        return None


def get_assets():
    """ Returns a list of strings for all assets available """
    assets = get(ASSETS_ENDPOINT)
    if assets:
        return assets["assets"]
    else:
        return []


def get_metrics():
    """ Returns a list of string for all metrics available"""
    metrics = get(COIN_METRICS_API + "/metrics")
    if metrics:
        return metrics["metrics"]
    else:
        return []


def get_reference_rates(asset, metric="PriceUSD", start=None, end=None):
    params = {'metrics': [metric]}
    if start:
        params['start'] = start
    if end:
        params['end'] = end
    return get(f"{ASSETS_ENDPOINT}/{asset}/metricdata", params=params)


def get_reference_rates_pandas(asset, metric="PriceUSD", start=None, end=None):
    reference_rates = get_reference_rates(asset, metric, start, end)
    res = {}
    if reference_rates:
        # convert to pandas friendly format, which is {"col1": [<col1-vals>], "col2": [<col2-vals>], ...}

        # Initialize all columns to empty lists
        res["time"] = []
        metric_columns = reference_rates["metricData"]["metrics"]
        for column in metric_columns:
            res[column] = []

        # Fill in columns
        data = reference_rates["metricData"]["series"]
        for row in data:
            # Add time to row
            res["time"].append(row["time"])
            # Add each value to row
            for ind, val in enumerate(row["values"]):
                column = metric_columns[ind]
                res[column].append(val)
    return res


def get_metric_info():
    metrics_info = get(f"{COIN_METRICS_API}/metric_info")
    metrics_info = metrics_info["metricsInfo"]
    reg = re.compile(r",")
    for metric in metrics_info:
        metric["name"] = reg.sub("", metric["name"])
    return metrics_info


def get_asset_info():
    asset_info = get(f"{COIN_METRICS_API}/asset_info")
    return asset_info["assetsInfo"]


def get_exchange_info():
    exchange_info = get(f"{COIN_METRICS_API}/exchange_info")
    return exchange_info["exchangesInfo"]


# This is just a demo of the API, we should really never run this file
if __name__ == "__main__":
    # print(get_assets())
    # print(get_metrics())
    # print(get_reference_rates_pandas(get_assets()[0]))
    # print(get_asset_info()[0])
    for metric in get_metric_info():
        print(metric)
    # print(get_exchange_info())
