import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import matplotlib.pyplot as plt

# Load the CSV file (update filename if needed)
filename = "electricity_prices.csv"  
df = pd.read_csv(filename)

# Identify the correct column with electricity prices
price_column = "2022-23 Projected Price(₹/kWh)"  

# Extract hourly price data
df = df[["Hour", price_column]]
df.rename(columns={price_column: "Price"}, inplace=True)

# Convert "Hour" to numerical index for forecasting
df["Hour"] = df["Hour"].astype(str).str.split(":").str[0].astype(int)

# Apply Exponential Smoothing for forecasting
model = ExponentialSmoothing(df["Price"], trend="add", seasonal=None, damped_trend=True)
fit = model.fit()

# Predict prices for the next cycle (24 hours)
future_hours = np.arange(24)  # Predict for 24 hours
predicted_prices = fit.forecast(steps=24)

# Ensure rounding to 2 decimal places
predicted_prices_rounded = [round(price, 2) for price in predicted_prices]

# Generate time range labels (e.g., "00:00 - 01:00", "01:00 - 02:00", ...)
time_ranges = [f"{str(hour).zfill(2)}:00 - {str(hour+1).zfill(2)}:00" for hour in range(24)]

# Create a new DataFrame for predicted prices
predicted_df = pd.DataFrame({
    "Time Range": time_ranges,
    "Predicted Price (₹/kWh)": predicted_prices_rounded
})

# Save as a new CSV file
predicted_df.to_csv("predicted_electricity_prices.csv", index=False)
print("✅ Predicted prices saved as 'predicted_electricity_prices.csv'.")

# Plot the trend for visualization
plt.figure(figsize=(12,5))
plt.plot(range(24), predicted_prices_rounded, marker="o", linestyle="dashed", color="red", label="Predicted Prices")
plt.xticks(ticks=range(24), labels=time_ranges, rotation=45, ha="right")
plt.xlabel("Time Range")
plt.ylabel("Price (₹/kWh)")
plt.title("Electricity Price Trend & Prediction")
plt.legend()
plt.grid()
plt.show()
