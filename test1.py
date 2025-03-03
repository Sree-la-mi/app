import requests
import json

# Define test cases
test_data = [
    {"power": 2.5, "duration": 3, "user_constraint": "None", "has_start_time": False},
    {"power": 1.8, "duration": 2, "user_constraint": "Morning", "has_start_time": False},
    {"power": 3.2, "duration": 4, "user_constraint": "Evening", "has_start_time": False},
    {"power": 1.0, "duration": 1, "user_constraint": "Night", "has_start_time": False},
]

# Send request
response = requests.post("http://127.0.0.1:5000/optimize_schedule", json=test_data)

# Print response
if response.status_code == 200:
    result = response.json()
    print("\n🔹 **Optimized Load Schedule:**")
    for r in result["results"]:
        print(f"   - Constraint: {r['constraint']}, Start Time: {r['start_time']}")

    print("\n🔹 **Total Cost Comparison:**")
    print(f"   ⚡ **Total Non-Optimized Cost:** ${result['total_non_optimized_cost']}")
    print(f"   ✅ **Total Optimized Cost:** ${result['total_optimized_cost']}")
    print(f"   💰 **Total Savings:** ${result['total_saving']}")
else:
    print(f"❌ Error: {response.text}")
