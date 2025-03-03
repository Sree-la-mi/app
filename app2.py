from flask import Flask, request, jsonify, send_file
import numpy as np
from scipy.optimize import minimize
import matplotlib
matplotlib.use('Agg')  # Set the backend to 'Agg'
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# Constants
PEAK_DEMAND_LIMIT = 10  # kW

def calculate_individual_cost(start_times, durations, power_consumption, prices):
    """Calculates individual costs considering fractional start times."""
    individual_costs = []
    for i in range(len(start_times)):
        cost = 0.0
        start = start_times[i]
        duration = durations[i]
        power = power_consumption[i]
        
        current_time = start
        while current_time < start + duration:
            hour = int(current_time)
            next_hour = hour + 1
            fraction = min(next_hour, start + duration) - current_time
            
            if hour < len(prices):
                cost += power * prices[hour] * fraction
            current_time = next_hour
        
        individual_costs.append(cost)
    return individual_costs

def calculate_detailed_costs(start_times, durations, power_consumption, prices):
    """Calculates detailed costs for each interval of each load considering fractional times."""
    detailed_costs = {}
    for i in range(len(start_times)):
        load_key = f"Load {i + 1}"
        detailed_costs[load_key] = {
            'intervals': [],
            'total_cost': 0.0
        }
        start = start_times[i]
        duration = durations[i]
        power = power_consumption[i]

        current_time = start
        total_cost = 0.0

        while current_time < start + duration:
            hour = int(current_time)
            next_hour = hour + 1
            fraction = min(next_hour, start + duration) - current_time
            
            if hour < len(prices):
                price = prices[hour]
                cost = power * price * fraction
                detailed_costs[load_key]['intervals'].append({
                    'time': f"{current_time:.2f} to {min(next_hour, start + duration):.2f}",
                    'price': price,
                    'cost': cost
                })
                total_cost += cost
            
            current_time = next_hour

        detailed_costs[load_key]['total_cost'] = total_cost
    return detailed_costs

def optimize_schedule(durations, power_consumption, allowed_windows, min_gap, prices):
    """Optimizes load scheduling while considering constraints."""
    num_loads = len(durations)
    time_slots = len(prices)

    # Initial guess: Start times at the cheapest hours within the allowed time windows
    x0 = []
    for i in range(num_loads):
        start, end = allowed_windows[i]
        cheapest_hour = start + np.argmin(prices[start:end])
        x0.append(cheapest_hour)
    x0 = np.array(x0) + np.random.uniform(-1, 1, size=num_loads)

    bounds = [(allowed_windows[i][0], allowed_windows[i][1]) for i in range(num_loads)]

    constraints = []
    if min_gap > 0:
        for i in range(num_loads - 1):
            constraints.append({'type': 'ineq', 'fun': lambda x, i=i: x[i+1] - x[i] - min_gap})

    def peak_demand_constraint(x):
        power_usage = np.zeros(time_slots)
        for i in range(num_loads):
            start = x[i]
            duration = durations[i]
            power = power_consumption[i]
            
            current_time = start
            while current_time < start + duration:
                hour = int(current_time)
                next_hour = hour + 1
                fraction = min(next_hour, start + duration) - current_time
                
                if hour < time_slots:
                    power_usage[hour] += power * fraction
                current_time = next_hour
        
        return PEAK_DEMAND_LIMIT - max(power_usage)
    
    constraints.append({'type': 'ineq', 'fun': peak_demand_constraint})
    
    def objective(x):
        return sum(calculate_individual_cost(x, durations, power_consumption, prices))
    
    result = minimize(
        objective, x0, bounds=bounds, constraints=constraints,
        method='SLSQP', options={'disp': True, 'maxiter': 100}
    )

    if result.success:
        return np.round(result.x, 2)
    else:
        return None

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    durations = data.get('durations')
    power_consumption = data.get('power_consumption')
    allowed_windows = data.get('allowed_windows')
    min_gap = data.get('min_gap')
    prices = data.get('prices')
    
    best_start_times = optimize_schedule(durations, power_consumption, allowed_windows, min_gap, prices)
    
    if best_start_times is not None:
        optimized_costs = calculate_individual_cost(best_start_times, durations, power_consumption, prices)
        non_optimal_start_times = [allowed_windows[i][0] for i in range(len(durations))]
        non_optimized_costs = calculate_individual_cost(non_optimal_start_times, durations, power_consumption, prices)
        detailed_costs = calculate_detailed_costs(best_start_times, durations, power_consumption, prices)
        
        return jsonify({
            'optimal_start_times': best_start_times.tolist(),
            'optimized_costs': optimized_costs,
            'non_optimized_costs': non_optimized_costs,
            'total_optimized_cost': sum(optimized_costs),
            'total_non_optimized_cost': sum(non_optimized_costs),
            'detailed_costs': detailed_costs,
            'graph_url': '/graph'
        })
    else:
        return jsonify({'error': 'Optimization failed'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
