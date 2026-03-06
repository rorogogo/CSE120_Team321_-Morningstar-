import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from statsmodels.tsa.statespace.sarimax import SARIMAX
import os 

#Seasonal AutoRegressive Integrated Moving Average with eXogenous regressors (SARIMAX)
#https://medium.com/biased-algorithms/sarima-models-explained-5e3274087fe3
#https://www.geeksforgeeks.org/machine-learning/sarima-seasonal-autoregressive-integrated-moving-average/
#https://www.geeksforgeeks.org/python/complete-guide-to-sarimax-in-python/

# ------------------------------
# WHY SARIMAX vs SARIMA:
# SARIMA models seasonal ARIMA (AR, I, MA with seasonality)
# SARIMAX is the same but allows EXOGENOUS variables (X)
# In our current code we are not using exogenous predictors,
# so technically SARIMA would work, but SARIMAX is more flexible
# for future improvements (like including promotions, holidays, etc.)
# ------------------------------

# CONNECT TO SQLITE DATABASE
conn = sqlite3.connect("data.db")

print("Loading shipment data...")

df = pd.read_sql_query("""
SELECT
    ship_from_warehouse AS warehouse,
    ship_to_customer_id AS customer,
    product,
    containers_shipped,
    requested_ship_date
FROM shipments
WHERE containers_shipped IS NOT NULL
""", conn)

# CLEAN DATE FORMAT
print("Cleaning dates...")

# remove weekday prefix if present, e.g., "Wed, 11/05/2025"
df["requested_ship_date"] = df["requested_ship_date"].str[5:]
df["requested_ship_date"] = pd.to_datetime(df["requested_ship_date"], errors="coerce")
df = df.dropna(subset=["requested_ship_date"])

# CREATE MONTH COLUMN
df["month"] = df["requested_ship_date"].dt.to_period("M")
df["month"] = df["month"].dt.to_timestamp()

# AGGREGATE MONTHLY DEMAND BY WAREHOUSE + PRODUCT
print("Aggregating monthly demand by warehouse and product...")

monthly_demand = (
    df.groupby(["warehouse", "product", "month"])["containers_shipped"]
    .sum()
    .reset_index()
)

print("Sample aggregated demand:")
print(monthly_demand.head())

# FORECAST NEXT 3 MONTHS
print("Running forecasting model for next 3 months...")

forecasts = []

# create folder for plots
plot_folder = "forecast_plots"
os.makedirs(plot_folder, exist_ok=True)

pdf_path = os.path.join(plot_folder, "all_forecasts.pdf")
pdf = PdfPages(pdf_path)

groups = monthly_demand.groupby(["warehouse", "product"])

for (warehouse, product), group in groups:

    group = group.sort_values("month")
    
    # require minimum data for modeling
    if len(group) < 6:
        continue

    ts = group.set_index("month")["containers_shipped"]

    try:
        model = SARIMAX(
            ts,
            #p: The number of lag observations included in the model (non-seasonal AR component).
            #d: The number of times the data has been differenced to make it stationary (non-seasonal differencing).
            #q: The size of the moving average window (non-seasonal MA component).
            #P: The seasonal autoregressive order (number of seasonal lags to include).
            #D: The seasonal differencing order (seasonal differencing needed to make the series stationary).
            #Q: The size of the seasonal moving average window.
            #S: The length of the seasonal cycle (e.g., 12 for monthly data with a yearly seasonality).
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 12),
            enforce_stationarity=False,
            enforce_invertibility=False
        )

        model_fit = model.fit(disp=False)

        # In-sample predictions (to compare predicted vs actual for all months)
        pred_in_sample = model_fit.get_prediction(start=ts.index[0], end=ts.index[-1])
        pred_mean = pred_in_sample.predicted_mean
        pred_mean = pred_mean.apply(lambda x: max(0, int(round(x))))

        # Forecast next 3 months
        future_prediction = model_fit.forecast(steps=3)
        future_prediction = future_prediction.apply(lambda x: max(0, int(round(x))))

        for date, value in future_prediction.items():
            forecasts.append({
                "warehouse": warehouse,
                "product": product,
                "forecast_month": date.strftime("%Y-%m"),
                "predicted_containers": value
            })

        # Plot actual vs predicted (in-sample) and forecast, save to PDF
        plt.figure(figsize=(8, 3))
        ts.plot(label="Actual", marker='o')
        pred_mean.plot(label="Predicted (In-Sample)", marker='x')
        future_prediction.plot(label="Forecast Next 3 Months", marker='s')
        plt.title(f"{warehouse} - {product} Forecast & In-Sample")
        plt.xlabel("Month")
        plt.ylabel("Containers Shipped")
        plt.legend()
        plt.tight_layout()
        pdf.savefig()
        plt.close()

    except Exception as e:
        print(f"Skipping {warehouse} - {product} due to error: {e}")
        continue

pdf.close()

forecast_df = pd.DataFrame(forecasts)

print("\nSample forecasts:")
print(forecast_df.head())

# SAVE RESULTS TO SQLITE
print("Saving forecast results to database...")
forecast_df.to_sql("demand_forecast", conn, if_exists="replace", index=False)

# VIEW RESULT SUMMARY
summary = pd.read_sql_query("SELECT * FROM demand_forecast LIMIT 10", conn)
print("\nSample predictions from database:")
print(summary)

conn.close()

print("\nForecasting pipeline complete.")