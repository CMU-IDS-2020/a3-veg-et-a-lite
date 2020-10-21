# Veg-et-a Lite

![](https://github.com/CMU-IDS-2020/a3-veg-et-a-lite/blob/master/main_chart_condensed%202.0.png)
![](https://github.com/CMU-IDS-2020/a3-veg-et-a-lite/blob/master/scatter_plots%20screenshot.png)
![](https://github.com/CMU-IDS-2020/a3-veg-et-a-lite/blob/master/heat_map%20screenshot.png)

Let's go super saiyan on Crypto currency. Our graphs allow you to interactively analyze the most up to date information on the most popular cryptocurrencies on the market.

![](images/crypto_saiyan.jpeg?raw=true)

## Project Goals

### Mission Statement
Provide a visualization tool that enables end users interested in trading cryptocurrency to make informed unbiased decisions. Our team aims to provide an easy to navigate application that displays critical data points necessary for customers to formulate their own forecasting analysis.

### Background
Cryptocurrency - The popularity of cryptocurrency has increased since its introduction in 2009. The rapid growth of cryptocurrency is attributed to the foundational characteristics that surround decentralized currency. The same features that have lured many investors have also contributed to the high degree of volatility index. The associated risk and overwhelming introduction of other cryptocurrencies have forced novice investors to be reluctant in investing. 

Cryptocurrency Performance – The cryptocurrency market seems to be unaffected by the current trying times. Initial analysis suggests that there is a typical drop in price in the fall with a steady climb peaking late spring early summer time period. This is a very generalized summary of the findings while utilizing the interactive chart that is provided to users on a public trading platform. 

Brokerage applications – In recent months the popularity of mobile trading platforms have soared. Apps like Robinhood provide users with varying experience, the ability to participate in daily exchanges. Typical stock trading applications provide the users with an interface consisting of one chart with little interactive tools,  running estimate on statistics with no explanation, and inundate the user with headlines and third party analysis that provide suggestive advice. 

### Objective 
The primary objective of the team was to build an application that illustrated comprehensive data of asset(s) in question and key metrics over time. Additionally, providing the user with features that display corresponding data values pertaining to previous ROI. The purpose of the app is to provide the user with quick, dynamic interactive illustrations of past performance in order to enable the user the ability to forecast future performance and assist in the investment decision making process. 

## Design
Some of these design decisions are covered in the development section but we wanted to highlight some important ones here

Critical data points that drive successful investment decisions that our illustration captures

### Realtime Data
Our customers expect the very best from us; our product wouldn't be very useful to them if we didn't show them the most up to date metrics available. It was for this reason that we chose to not use static csv files as our data source, but instead integrate with a web API to be able to continuously pull and display the most up date, realtime metrics available. 

### Main Chart
We chose a classic line chart with time on the x axis and a metric on the y axis. This is how most stock and asset related charts are constructed. We wanted our main chart to be famiiliar and easy to understand and we felt that this was the best way to do that. In terms of the scale of the y-axis we ran into a bit of an issue. Some assets have very similar scaled metrics and are easy to compare while some have orders of magnitude of difference. Additionally some metrics can be negative. For this reason we added a symlog scale toggle button to allow the user to toggle between symlog and linear scale. Symlog allows metrics with hugely different values to be compared easily while still working on negative numbers. When the metrics are similar the user can just use a standard linear scale.
Aditionally we added an average line for each asset so the user can see how any given data points compares to the average. We allow the user to narrow the time frame of the average without having to change the time frame of the entire graph. This was so user can compare the average of a specific time period to any data points.

### Date Slider
It's important that users of our charts can drill down into specific time frames. Perhaps they want to see how COVID affects certain metrics, or maybe how an the presidential debates affects Bitcoin price. They wouldn't be able to answer these questions easily by looking at the entire lifetime of an asset. It was crucial to allow users to drill down into specific date ranges for this exact reason. This is why we added the date slider to our chart.

### Scatter Matrix
For this particular dataset, the purpose of a scatter matrix is to help one understand the general shape (and density, for those who can recognize it through overlap of color) of the data relations between variables. Hence, one would gain better intuition by choosing 3 features that potentially have (interesting) real-world implications when related to one another. Hence, these 3 features need to be quite different in measuring units. With cryptocurrency being related to economics, price (in USD; it is more relatable to clients) is the first feature chosen. The next feature chosen is the number of transactions. The reason for including this feature is that it highlights the value of the bitcoin in the currency network. The last feature included is the metric for volatility daily returns. Transactions and pricing play a factor in economic stability, so it is a feature to include in the matrix.

## Development

### Getting the Data
The team was originally comprised of just Joe and Josh. We thought that analyzing some cryptocurrency metrics would be interesting and provide us with a good amount of data. We found this site [Coin Metrics](https://coinmetrics.io/community-network-data/) which provided fairly clean and robust data on a bunch of different coins. We were originally going to use static csv files for uploading data and converting to data frames, but this introduced a significant issue. What use are our charts if they only show data up to some arbitrary date in which we decided to download the CSV. This is when we discovered that Coin Metrics also exposes a free [Web API](https://docs.coinmetrics.io/api/v2/). If we could connect to the web API then we wouldn't have stale data, and can continuously show the most up to date metrics. The other cool thing is that as Coin Metrics adds or removes different types of metrics, we can dynamically add and remove these metrics from our charts. 

Joe, who has previous experience in web development, got to work on [coin_metrics.py](coin_metrics.py) which exposes a bunch of python methods for communicating with the web API. It took roughly 2 hours to complete. The most tricky thing was that in order to convert the data into a dataframe we needed it in a specific format for pandas to accept it, specifically something like this
```
{
  "column1": [<column1-values>],
  "column2": [<column2-values>],
  ...
}
```
Our data looked like this
```
[
  {
    "col1": <row1-col1-value>,
    "col2": <row1-col2-value>,
    ...
  },
  {
    "col1": <row2-col1-value>,
    "col2": <row2-col2-value>,
    ...
  },
  ...
]
```
After some preprocessing of our data though we were able to easily convert it to a dataframe.

### The Main Chart
For the main chart we wanted to allow people to see any metric for any crypto asset. We decided to plot the metric on the y axis and time on the x. Our goal was to make it look like any other stock chart you'd see if you googled "Stock X prices", but we'd show crypto currency coins and we'd allow you to see any metric. After roughly 3-5 hours of pair programming, Joe and Josh created a chart that worked in the following way:
1. The user would see a drop down menu of all available crypto coins that they could select from. This would default to the first coin returned by the API.
2. The user would then see a drop down menu of all available metrics for that coin that they could select from. This would default to the first metric returned by the API.
3. The user would then see that metric plotted 
Since some of the metrics are not immediately obvious, Joe added a little blurb to explain to currently selected metric. This took roughly 45 minutes. 
It originally looked like this
![](https://github.com/CMU-IDS-2020/a3-veg-et-a-lite/blob/master/main_chart_condensed%202.0.png)

### Addition of Jeffrey
At this point we heard Jeffrey still hadn't found a group, so we added him to ours to become a group of 3.

### Date slider 
The main chart by default shows the data for the entire timeframe that the asset has existed. Jeff and Joe worked together to add a slider under the graph that let's you pick the date range. Originally we only had a slider that only let you select the target year, this was built using altiar and filtered the chart directly. Eventually though we managed to use streamlit to to be able to select a range of date down to the day granularity. The downside was that it would filter the dataframe and redraw the chart instead of filtering the chart directly. The whole process took us roughly 3 hours.

### Moving Average
Josh realized that users of the main chart needed a way to evaluate the metric at any given time. How does that value stack up against the rest? So he added a line to the chart to indicate the average value for the metric. Additionally he added a brush to the chart so that the average reflects the timeframe highlighted by the brush. The process took about 1.5 hrs.

### Multi-Select and Symlog
At this point we realized that looking at a single asset doesn't tell you much, the isnights are gained from comparing it to multiple assets. So Joe added the feature to be able to select multiple assets at once and they would all be graphed on the same chart with the same metric. One issue was that some assets were orders of magnitude greater for a certain metric. However we couldn't use log scales because some metrics were negative. For this reason we add a toggle to allow the user to switch between a symlog and linear scale depending on the assets and metrics. This was actually a decently difficult process and the performance does take a hit with a large amount of assets. The whole thing took about 5-7 hours.

### Scatter Matrix
We wanted a way to compare different metrics that we thought could be related. So we created a scatter plot matrix of the following three metrics, Price in USD, Transactions count, and Volatility Daily Returns 30d. Josh came up with the concept and idea, Jeff came up with the chosen metrics, and Joe put the chart together. The scatter matrix is connected to the date range slider. The whole process took 2 hours.
