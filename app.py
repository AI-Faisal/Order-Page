from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
import math

app = Flask(__name__)
server = app.server

directory = os.getcwd()
path = "Test_info.xlsx"
data = pd.read_excel(path)

# Extract necessary columns
data = data[['Name', 'Price($)', 'Weight(g)']]

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
    items = data.to_dict(orient='records')
    return render_template('index.html', items=items)

@app.route('/place_order', methods=['POST'])
def place_order():
    selected_items = request.json['selected_items']
    items = [data.loc[data['Name'] == item].to_dict(orient='records')[0] for item in selected_items]

    total_price = sum(item['Price($)'] for item in items)
    total_weight = sum(item['Weight(g)'] for item in items)

    packages = []
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

if __name__ == '__main__':
    app.run(debug=False)
