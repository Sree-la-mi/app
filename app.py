import pandas as pd
import numpy as np
import requests
from scipy.optimize import minimize

# Constants
PEAK_DEMAND_LIMIT = 10  # kW (example)

# Function to fetch real-time electricity prices from an API
def fetch_real_time_prices():
    try:
        response = requests.get("YOUR_API_ENDPOINT_HERE")
        if response.status_code == 200:
            prices = response.json()  # Adjust based on API response format
            return prices["hourly_prices"]  # Modify according to actual API structure
        else:
            print("⚠️ Error fetching real-time prices. Using CSV instead.")
            return None
    except Exception as e:
        print(f"⚠️ API error: {e}")
        return None

# Function to load electricity prices from CSV
def load_csv_prices(filename="predicted_electricity_prices.csv"):
    try:
        df = pd.read_csv(filename)
        return df["Predicted Price (₹/kWh)"].tolist()
    except FileNotFoundError:
        print("⚠️ CSV file not found! Please provide the correct file.")
        return None

# Function to calculate total cost
def calculate_cost(start_times, durations, power_consumption, prices):
    total_cost = 0
    for i in range(len(start_times)):
        start = int(round(start_times[i]))  # Ensure integer start time
        for j in range(int(durations[i])):  # Ensure duration is integer
            if start + j < len(prices):  # Ensure index does not exceed time slots
                total_cost += power_consumption[i] * prices[start + j]
    return total_cost

# Function to optimize load scheduling
def optimize_schedule(loads, durations, power_consumption, allowed_windows, min_gaps, prices):
    num_loads = len(loads)
    time_slots = len(prices)

    # Decision variables (start times for each load)
    x0 = np.array([allowed_windows[i][0] for i in range(num_loads)])

    # Constraints
    constraints = []

    # Time window constraints
    for i in range(num_loads):
        constraints.append({'type': 'ineq', 'fun': lambda x, i=i: x[i] - allowed_windows[i][0]})  # Start time >= min
        constraints.append({'type': 'ineq', 'fun': lambda x, i=i: allowed_windows[i][1] - x[i]})  # Start time <= max

    # Minimum gap constraint (ensuring specific loads don't start too close)
    for i in range(num_loads - 1):
        constraints.append({'type': 'ineq', 'fun': lambda x, i=i: x[i+1] - x[i] - min_gaps[i]})

    # Peak demand constraint
    def peak_demand_constraint(x):
        power_usage = np.zeros(time_slots)
        for i in range(num_loads):
            start = int(round(x[i]))
            for j in range(int(durations[i])):
                if start + j < time_slots:
                    power_usage[start + j] += power_consumption[i]
        return PEAK_DEMAND_LIMIT - max(power_usage)

    constraints.append({'type': 'ineq', 'fun': peak_demand_constraint})

    # Objective function (minimize total cost)
    def objective(x):
        return calculate_cost(x, durations, power_consumption, prices)

    # Solve the optimization problem
    result = minimize(objective, x0, constraints=constraints, method='SLSQP', options={'disp': False})

    return np.round(result.x) if result.success else None  # Round final start times

# Main function
def main():
    print("🔹 Load Scheduling Optimization 🔹")

    # Choose data source
    data_source = input("Choose price data source (1: API, 2: CSV): ").strip()
    prices = fetch_real_time_prices() if data_source == "1" else load_csv_prices()

    if prices is None:
        print("⚠️ No price data available. Exiting.")
        return

    num_loads = int(input("Enter the number of loads: "))
    durations = []
    power_consumption = []
    allowed_windows = []
    min_gaps = []

    for i in range(num_loads):
        durations.append(float(input(f"Duration for load {i+1} (hours): ")))  # Store as float but ensure conversion
        power_consumption.append(float(input(f"Power consumption for load {i+1} (kW): ")))

    for i in range(num_loads):
        start, end = map(int, input(f"Enter allowed time window for load {i+1} (start end): ").split())
        allowed_windows.append((start, end))

    if num_loads > 1:
        min_gaps = list(map(float, input("Enter minimum gap (hours) between loads (space-separated, press Enter for 0): ").split()))
    else:
        min_gaps = [0]

    # Non-optimized schedule (earliest start time within allowed window)
    non_optimal_start_times = [allowed_windows[i][0] for i in range(num_loads)]
    non_optimized_cost = calculate_cost(non_optimal_start_times, durations, power_consumption, prices)

    # Optimized schedule
    best_start_times = optimize_schedule(range(num_loads), durations, power_consumption, allowed_windows, min_gaps, prices)

    if best_start_times is not None:
        optimized_cost = calculate_cost(best_start_times, durations, power_consumption, prices)
        savings = non_optimized_cost - optimized_cost
        savings_percentage = (savings / non_optimized_cost) * 100 if non_optimized_cost > 0 else 0

        print("\n✅ Optimal Start Times:", best_start_times)
        print(f"💰 Optimized Cost: ₹{round(optimized_cost, 2)}")
        print(f"⚡ Non-Optimized Cost: ₹{round(non_optimized_cost, 2)}")
        print(f"💡 Cost Savings: ₹{round(savings, 2)} ({round(savings_percentage, 2)}% reduction)")

    else:
        print("⚠️ Optimization failed. Please check constraints and input data.")

if __name__ == "__main__":
    main()
