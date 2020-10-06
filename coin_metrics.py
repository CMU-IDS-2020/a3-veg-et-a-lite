import json

import requests

# API docs can be found here: https://docs.coinmetrics.io/api/v2/

COIN_METRICS_API = "https://community-api.coinmetrics.io/v2"
ASSETS_ENDPOINT = COIN_METRICS_API + "/assets"
# TODO I think we should just add static CSVs in case something happens with the API. Then we can use this to toggle
# between the API and CSV file
USE_API = True


def get(url, params=None):
    """ Performs a GET request to the given url with supplied params. If an error happens that will be printed to the
    console and None is returned """
    response = requests.get(url, params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f"Unable to perform REST call. Status {response.status_code}. Message: {response.text}")
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


def get_reference_rates(asset, metrics=None, start=None, end=None):
    """ Gets metrics for a particular asset between start and end. Metrics retrieved is specified by metrics array.
    Response is a list where each entry is of the form"
        {
          "time": "yyyy-mm-ddTHH:MM:SSZ",
          "values": []
        }
    Where values array is in the same order as supplied metrics """
    if metrics is None:
        metrics = ["PriceUSD"]
    params = {'metrics': metrics}
    if start:
        params['start'] = start
    if end:
        params['end'] = end
    reference_rates = get(f"{ASSETS_ENDPOINT}/{asset}/metricdata", params=params)
    if reference_rates:
        return reference_rates["metricData"]["series"]
    else:
        return []


# This is just a demo of the API, we should really never run this file
if __name__ == "__main__":
    print(get_assets())
    print(get_metrics())
    print(get_reference_rates(get_assets()[0]))
