from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
import math

app = Flask(__name__)


# Locate data
directory = os.getcwd()
path = "order_packaging/Test_info.xlsx"
data = pd.read_excel(path)

# Extract necessary columns
data = data[['Name', 'Price($)', 'Weight(g)']]

# Weight price range condition
def calculate_courier_charge(weight):
    if weight <= 200:
        return 5
    elif weight <= 500:
        return 10
    elif weight <= 1000:
        return 15
    else:
        return 20

@app.route('/')
def index():
    items = data.to_dict(orient='records') # Convert data to a list
    return render_template('index.html', items=items) # Render the HTML template with the items

@app.route('/place_order', methods=['POST'])
def place_order():
    selected_items = request.json['selected_items'] # Get selected items
    items = [data.loc[data['Name'] == item].to_dict(orient='records')[0] for item in selected_items] # Get item details

    total_price = sum(item['Price($)'] for item in items) # Total price cal
    total_weight = sum(item['Weight(g)'] for item in items) # Total weight cal

    packages = [] # Empty list to store packages
    if total_price <= 250:
        packages.append({'items': items, 'total_weight': total_weight, 'total_price': total_price, 'courier_charge': calculate_courier_charge(total_weight)})
    else:
        num_packages = math.ceil(total_price / 250)
        items.sort(key=lambda x: x['Weight(g)'], reverse=True)

        # Initialize empty packages
        for _ in range(num_packages):
            packages.append({'items': [], 'total_weight': 0, 'total_price': 0})

        # Distribute items
        for item in items:
            lightest_package = min(packages, key=lambda x: x['total_weight'])
            if lightest_package['total_price'] + item['Price($)'] < 250:
                lightest_package['items'].append(item)
                lightest_package['total_weight'] += item['Weight(g)']
                lightest_package['total_price'] += item['Price($)']

        # Calculate courier charges
        for package in packages:
            package['courier_charge'] = calculate_courier_charge(package['total_weight'])

    return jsonify({
        'order_id': request.json.get('order_id', 1),
        'total_price': total_price,
        'total_weight': total_weight,
        'packages': packages
    })

#server = app.server
if __name__ == '__main__':
    app.run(debug=True) # Run flask in debug
