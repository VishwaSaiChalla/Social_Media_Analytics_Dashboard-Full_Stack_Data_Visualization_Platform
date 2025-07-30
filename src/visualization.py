import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import requests

# Function to fetch data from the datastore
def fetch_data():
    # Replace with your datastore API endpoint
    response = requests.get('http://localhost:5000/data')  # Example endpoint
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data from datastore")
        return []

# Function to visualize the data
def visualize_data(data):
    df = pd.DataFrame(data)

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Group by category and timestamp
    grouped_data = df.groupby(['category', pd.Grouper(key='timestamp', freq='D')]).sum().reset_index()

    # Create a pivot table for visualization
    pivot_data = grouped_data.pivot(index='timestamp', columns='category', values='value').fillna(0)

    # Plotting
    plt.figure(figsize=(12, 6))
    for category in pivot_data.columns:
        plt.plot(pivot_data.index, pivot_data[category], label=category)

    plt.title('Trends Over Time')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('dashboard.png')  # Save the dashboard as an image
    plt.show()

if __name__ == "__main__":
    data = fetch_data()
    if data:
        visualize_data(data)