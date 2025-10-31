
from typing import Any
from flask import Flask, jsonify, request, send_from_directory, render_template
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='')

# In-memory "databases"
users = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"}
}

products = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
    2: {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50},
    3: {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 30}
}

orders = {}
order_id_counter = 1

# Health endpoint
@app.route('/health', methods=['GET'])
def get_health():
    return jsonify({"status": "All good"}), 200

# User endpoints
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = get_user_object(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

# Product endpoints
@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(list(products.values()))

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = products.get(product_id)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

# Order endpoints
@app.route('/orders', methods=['POST'])
def create_order():
    global order_id_counter
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    # Validate user exists
    if not get_user_object(user_id):
        return jsonify({"error": "User not found"}), 404
    
    # Validate product exists and has stock
    product = get_product_object(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    if product['stock'] < quantity:
        return jsonify({"error": "Insufficient stock"}), 400
    
    # Create order
    order = {
        "id": order_id_counter,
        "user_id": user_id,
        "product_id": product_id,
        "quantity": quantity,
        "total": product['price'] * quantity,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    # Update stock
    products[product_id]['stock'] -= quantity
    
    orders[order_id_counter] = order
    order_id_counter += 1
    
    return jsonify(order), 201

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = orders.get(order_id)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404


# Helper functions for managing orders

def get_user_object(user_id:str) -> Any:
    if user_id in users:
        return users[user_id]
    else:
        return None
        

def get_product_object(product_id:str):
    if product_id in products:
        return products[product_id]
    else:
        return None


def decrement_product_stock(product_id:str, quantity:int):
    if product_id in products:
        products[product_id]["stock"] -= quantity


# Serve the dashboard
@app.route('/')
def dashboard():
    return send_from_directory('static','index.html')

# Optional: serve other static files (CSS, JS, images)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5020, debug=True)