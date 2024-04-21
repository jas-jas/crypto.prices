#!/usr/bin/env python3

# Can also run as ./crypto.py
# Outputs prices to console and to output_html_file path
# Set the following variables:  crypto_symbols & output_html_file
# Requirements tabulate and jinja2

import os
import requests
from datetime import datetime, timedelta
from tabulate import tabulate
from jinja2 import Template
import time

# Variables for Cryptocurrencies and Output
crypto_symbols = ["BTC", "ETH", "SOL", "ENS"]  # Add more symbols here if needed
output_html_file = "/mnt/share/crypto.prices.html"  # Location for the HTML output file

# Initialize global variables
crypto_prices = {}
crypto_changes = {}
timeframes = [
    ("Real-Time", "real_time"),
    ("24 hours", "1d"),
    ("3 days", "3d"),
    ("7 days", "7d"),
    ("30 days", "30d"),
    ("60 days", "60d"),
    ("90 days", "90d"),
    ("1 year", "1y")
]

# Get today's date
today = datetime.now().date().isoformat()

# Calculate previous dates
date_formats = {
    "1d": (datetime.now().date() - timedelta(days=1)).isoformat(),
    "3d": (datetime.now().date() - timedelta(days=3)).isoformat(),
    "7d": (datetime.now().date() - timedelta(days=7)).isoformat(),
    "30d": (datetime.now().date() - timedelta(days=30)).isoformat(),
    "60d": (datetime.now().date() - timedelta(days=60)).isoformat(),
    "90d": (datetime.now().date() - timedelta(days=90)).isoformat(),
    "1y": (datetime.now().date() - timedelta(days=365)).isoformat()
}

def get_price_difference(current_price, prior_price):
    return round(((float(current_price) - float(prior_price)) / float(prior_price)) * 100, 2)

def colorize_output(change):
    if change > 0:
        return f"\033[92m{change}%\033[0m"  # Green for positive change
    elif change < 0:
        return f"\033[91m{change}%\033[0m"  # Red for negative change
    else:
        return f"\033[90m{change}%\033[0m"  # Gray for no change

# Function to fetch data for a cryptocurrency
def fetch_cryptocurrency_data(currency_code):
    global today, crypto_prices, crypto_changes

    coinbase_url = f"https://api.coinbase.com/v2/prices/{currency_code}-USD/spot"
    try:
        coinbase_price_real_time = requests.get(coinbase_url).json()["data"]["amount"]
    except (requests.exceptions.RequestException, KeyError):
        coinbase_price_real_time = "NA"

    previous_prices = {}
    for timeframe, date_format in timeframes:
        if date_format == "real_time":
            previous_prices[timeframe] = coinbase_price_real_time
        else:
            url = f"https://api.coinbase.com/v2/prices/{currency_code}-USD/spot?date={date_formats[date_format]}"
            try:
                response = requests.get(url)
                data = response.json()
                previous_prices[timeframe] = data["data"]["amount"]
            except (requests.exceptions.RequestException, KeyError):
                previous_prices[timeframe] = "NA"

    changes = {}
    for timeframe, price in previous_prices.items():
        if price != "NA":
            percent_change = get_price_difference(coinbase_price_real_time, price)
            changes[timeframe] = round(percent_change, 2)  # Round to 2 decimal places
        else:
            changes[timeframe] = "NA"

    crypto_prices[currency_code] = round(float(coinbase_price_real_time), 2)  # Round real-time price
    crypto_changes[currency_code] = changes

def clear_table():
    # Clear the terminal
    os.system('cls' if os.name == 'nt' else 'clear')  # For Windows and Unix/Linux

def print_table():
    global crypto_prices, crypto_changes

    # Clear the table
    clear_table()

    data_rows = []
    for timeframe, _ in timeframes:
        row = [f"{timeframe}:"]
        for symbol in crypto_symbols:
            if timeframe == "Real-Time":
                if symbol in crypto_prices:
                    row.append(crypto_prices[symbol])
                else:
                    row.append("NA")
            elif symbol in crypto_prices and symbol in crypto_changes and timeframe in crypto_changes[symbol]:
                change = crypto_changes[symbol][timeframe]
                colored_change = colorize_output(change)
                row.append(f"{colored_change}")
            else:
                row.append("NA")
        data_rows.append(row)

    # Prepare headers
    headers = ["Statistic"] + crypto_symbols

    # Print the table
    print(tabulate(data_rows, headers=headers, tablefmt="grid"))

def generate_html():
    global crypto_prices, crypto_changes, output_html_file

    # HTML Template Content
    template_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cryptocurrency Prices and Changes</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    /* Custom CSS */
    .center-text {
    text-align: center;
    }
    .table-hover tbody tr:hover {
    background-color: #f5f5f5; /* Light gray background on hover */
    }
    .table-hover tbody tr:hover td {
    font-weight: bold; /* Bold text on hover */
    }
    </style>
    </head>
    <body>
    <div class="container mt-5">
    <h1 class="mb-4 center-text">Cryptocurrency Prices and Changes</h1>
    <table class="table table-striped table-hover">
    <thead>
    <tr>
    <th scope="col">Statistic</th>
    {% for symbol in crypto_symbols %}
    <th scope="col">{{ symbol }}</th>
    {% endfor %}
    </tr>
    </thead>
    <tbody>
    {% for timeframe, _ in timeframes %}
    <tr>
    <td>{{ timeframe }}</td>
    {% for symbol in crypto_symbols %}
    {% if timeframe == "Real-Time" %}
    {% if symbol in crypto_prices %}
    {% set price = crypto_prices[symbol]|default("NA") %}
    <td>{{ price }}</td>
    {% else %}
    <td>NA</td>
    {% endif %}
    {% else %}
    {% if symbol in crypto_changes and timeframe in crypto_changes[symbol] %}
    {% set change = crypto_changes[symbol][timeframe] %}
    {% if change != "NA" %}
    <td style="color: {{ '#28a745' if change > 0 else '#dc3545' if change < 0 else '#000000' }};">{{ change }}%</td>
    {% else %}
    <td>NA</td>
    {% endif %}
    {% else %}
    <td>NA</td>
    {% endif %}
    {% endif %}
    {% endfor %}
    </tr>
    {% endfor %}
    </tbody>
    </table>
    </div>
    <!-- Bootstrap JS (Optional) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

    # Create a Jinja2 template object
    template = Template(template_content)

    # Add the float function to the template's context
    template.globals['float'] = float

    # Render the template with data
    rendered_html = template.render(
        crypto_symbols=crypto_symbols,
        timeframes=timeframes,
        crypto_prices=crypto_prices,
        crypto_changes=crypto_changes
    )

    # Write the rendered HTML to the output file
    with open(output_html_file, "w") as html_file:
        html_file.write(rendered_html)

def main():
    while True:
        for symbol in crypto_symbols:
            fetch_cryptocurrency_data(symbol)
        print_table()  # Print the table to console
        generate_html()  # Generate the HTML file
        time.sleep(60)  # Fetch data every 60 seconds

if __name__ == "__main__":
    clear_table()  # Clear the screen before running the script
    main()
