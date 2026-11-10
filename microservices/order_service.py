
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

# Service addresses
USER_SERVICE_URL = "http://127.0.0.1:5031"
PRODUCT_SERVICE_URL = "http://127.0.0.1:5032"

# In-memory order database
orders = {}
order_id_counter = 1


@app.route('/health', methods=['GET'])
def get_health():
    return jsonify({"status": "All good"}), 200


# Get user information from User Service
def get_user_object(user_id):
    response = requests.get(
        f"{USER_SERVICE_URL}/{user_id}",
        timeout=5
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()


# Get product information from Product Service
def get_product_object(product_id):
    response = requests.get(
        f"{PRODUCT_SERVICE_URL}/{product_id}",
        timeout=5
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()


# Update stock through Product Service
def update_stock(product_id, stock):
    response = requests.put(
        f"{PRODUCT_SERVICE_URL}/{product_id}/stock",
        json={"stock": stock},
        timeout=5
    )

    response.raise_for_status()
    return response.json()


# Create an order
@app.route('/', methods=['POST', 'PUT'])
@app.route('/orders', methods=['POST', 'PUT'])
def create_order():
    global order_id_counter

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid data"}), 400

    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    # Validate input
    if type(user_id) is not int or user_id <= 0:
        return jsonify({"error": "Invalid user ID"}), 400

    if type(product_id) is not int or product_id <= 0:
        return jsonify({"error": "Invalid product ID"}), 400

    if type(quantity) is not int or quantity <= 0:
        return jsonify({
            "error": "Quantity must be a positive integer"
        }), 400

    try:
        # Step 1: Check user exists
        user = get_user_object(user_id)

        if user is None:
            return jsonify({"error": "User not found"}), 404

        # Step 2: Check product exists
        product = get_product_object(product_id)

        if product is None:
            return jsonify({"error": "Product not found"}), 404

        # Step 3: Check available stock
        if product['stock'] < quantity:
            return jsonify({
                "error": "Insufficient stock"
            }), 400

        # Step 4: Calculate new stock
        new_stock = product['stock'] - quantity

        # Step 5: Update Product Service
        update_stock(product_id, new_stock)

        # Step 6: Create order
        order = {
            "id": order_id_counter,
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "total": round(product['price'] * quantity, 2),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

        # Step 7: Save order
        orders[order_id_counter] = order
        order_id_counter += 1

        return jsonify(order), 201

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Service timeout",
            "message": "A dependent service timed out"
        }), 504

    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Service unavailable",
            "message": "Cannot connect to User or Product Service"
        }), 503

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Service communication error"
        }), 502

    except (ValueError, KeyError, TypeError):
        return jsonify({
            "error": "Invalid response from dependent service"
        }), 502


# Get an order by ID
@app.route('/<int:order_id>', methods=['GET'])
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = orders.get(order_id)

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    return jsonify(order), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5033, debug=True)
