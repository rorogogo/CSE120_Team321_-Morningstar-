import sqlite3
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX

# -------------------------------
# CONNECT TO SQLITE DATABASE
# -------------------------------
conn = sqlite3.connect("data.db")

print("Loading shipment data...")

df = pd.read_sql_query("""
SELECT
    ship_to_customer_id,
    product,
    containers_shipped,
    requested_ship_date
FROM shipments
WHERE containers_shipped IS NOT NULL
""", conn)

# -------------------------------
# CLEAN DATE FORMAT
# -------------------------------
print("Cleaning dates...")

df["requested_ship_date"] = df["requested_ship_date"].str[5:]
df["requested_ship_date"] = pd.to_datetime(df["requested_ship_date"], errors="coerce")

df = df.dropna(subset=["requested_ship_date"])

# -------------------------------
# CREATE MONTH COLUMN
# -------------------------------
df["month"] = df["requested_ship_date"].dt.to_period("M")

# -------------------------------
# MONTHLY DEMAND AGGREGATION
# -------------------------------
print("Aggregating monthly demand...")

monthly_demand = (
    df.groupby(["ship_to_customer_id", "product", "month"])
    ["containers_shipped"]
    .sum()
    .reset_index()
)

monthly_demand["month"] = monthly_demand["month"].dt.to_timestamp()

print("Monthly demand sample:")
print(monthly_demand.head())

# -------------------------------
# FORECAST NEXT 3 MONTHS
# -------------------------------
print("Running forecasting model...")

forecasts = []

groups = monthly_demand.groupby(["ship_to_customer_id", "product"])

for (customer, product), group in groups:

    group = group.sort_values("month")

    # require minimum data for modeling
    if len(group) < 6:
        continue

    ts = group.set_index("month")["containers_shipped"]

    try:
        model = SARIMAX(
            ts,
            order=(1,1,1),
            seasonal_order=(1,1,1,12),
            enforce_stationarity=False,
            enforce_invertibility=False
        )

        model_fit = model.fit(disp=False)

        prediction = model_fit.forecast(steps=3)

        for date, value in prediction.items():

            forecasts.append({
                "ship_to_customer_id": customer,
                "product": product,
                "forecast_month": date.strftime("%Y-%m"),
                "predicted_containers": int(round(value))
            })

    except:
        continue

forecast_df = pd.DataFrame(forecasts)

print("\nForecast sample:")
print(forecast_df.head())

# -------------------------------
# SAVE RESULTS TO SQLITE
# -------------------------------
print("Saving forecast results to database...")

forecast_df.to_sql(
    "demand_forecast",
    conn,
    if_exists="replace",
    index=False
)

print("\nForecast table written to SQLite.")

# -------------------------------
# OPTIONAL: VIEW RESULT SUMMARY
# -------------------------------
summary = pd.read_sql_query(
    "SELECT * FROM demand_forecast LIMIT 10",
    conn
)

print("\nSample predictions:")
print(summary)

conn.close()

print("\nForecasting pipeline complete.")