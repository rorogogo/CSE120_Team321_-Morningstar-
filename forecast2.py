import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from statsmodels.tsa.statespace.sarimax import SARIMAX
#Seasonal AutoRegressive Integrated Moving Average with eXogenous regressors (SARIMAX)
#https://medium.com/biased-algorithms/sarima-models-explained-5e3274087fe3
#https://www.geeksforgeeks.org/machine-learning/sarima-seasonal-autoregressive-integrated-moving-average/
#https://www.geeksforgeeks.org/python/complete-guide-to-sarimax-in-python/
from sklearn.metrics import mean_absolute_error

# CONNECT TO DATABASE
conn = sqlite3.connect("data.db")

query = """
SELECT
    "SHIP FROM WAREHOUSE" as warehouse,
    PRODUCT as product,
    "CONTAINERS SHIPPED" as containers,
    "REQUESTED SHIP DATE" as ship_date
FROM shipments
"""

df = pd.read_sql_query(query, conn)

# CLEAN DATE
# remove weekday prefix
df["ship_date"] = df["ship_date"].str[5:]

# convert to datetime safely
df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce")

# drop any rows that failed
df = df.dropna(subset=["ship_date"])

monthly = (
    df.groupby(["warehouse","product","month"])
    ["containers"]
    .sum()
    .reset_index()
)

monthly["month"] = monthly["month"].dt.to_timestamp()

# FORECAST STORAGE
forecasts = []

# TRAIN MODEL FOR EACH PRODUCT + WAREHOUSE
for (warehouse, product), group in monthly.groupby(["warehouse","product"]):

    group = group.sort_values("month")

    ts = group.set_index("month")["containers"]

    if len(ts) < 6:
        continue

    # split data for evaluation
    train = ts[:-3]
    test = ts[-3:]

    model = SARIMAX(train,
                    #p: The number of lag observations included in the model (non-seasonal AR component).
                    #d: The number of times the data has been differenced to make it stationary (non-seasonal differencing).
                    #q: The size of the moving average window (non-seasonal MA component).
                    #P: The seasonal autoregressive order (number of seasonal lags to include).
                    #D: The seasonal differencing order (seasonal differencing needed to make the series stationary).
                    #Q: The size of the seasonal moving average window.
                    #S: The length of the seasonal cycle (e.g., 12 for monthly data with a yearly seasonality).
                    order=(1,1,1),
                    seasonal_order=(1,1,1,12),
                    enforce_stationarity=False,
                    enforce_invertibility=False)

    results = model.fit(disp=False)

    # forecast next 3 months
    forecast = results.forecast(steps=3)

    # evaluate
    if len(test) == 3:
        mae = mean_absolute_error(test, forecast)
    else:
        mae = None

    for i, val in enumerate(forecast):
        forecasts.append({
            "warehouse": warehouse,
            "product": product,
            "forecast_month": forecast.index[i].strftime("%Y-%m"),
            "predicted_containers": int(max(val,0)),
            "mae_error": mae
        })

forecast_df = pd.DataFrame(forecasts)

# SAVE FORECASTS
forecast_df.to_sql(
    "warehouse_product_forecast",
    conn,
    if_exists="replace",
    index=False
)

print("Forecast table saved.")

# GRAPH EXAMPLE

example = monthly.groupby(["warehouse","product"]).size().idxmax()

ex_warehouse, ex_product = example

example_data = monthly[
    (monthly["warehouse"] == ex_warehouse) &
    (monthly["product"] == ex_product)
]

ts = example_data.set_index("month")["containers"]

model = SARIMAX(ts,
                order=(1,1,1),
                seasonal_order=(1,1,1,12),
                enforce_stationarity=False,
                enforce_invertibility=False)

results = model.fit(disp=False)

forecast = results.forecast(steps=3)

plt.figure(figsize=(10,5))
plt.plot(ts, label="Historical")
plt.plot(forecast, label="Forecast")
plt.title(f"Demand Forecast\nWarehouse={ex_warehouse} Product={ex_product}")
plt.legend()
plt.show()