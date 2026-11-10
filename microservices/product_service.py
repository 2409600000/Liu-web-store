
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory product database
products = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
    2: {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50},
    3: {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 30}
}


@app.route('/health', methods=['GET'])
def get_health():
    return jsonify({"status": "All good"}), 200


# Get all products
@app.route('/', methods=['GET'])
@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(list(products.values())), 200


# Get a specific product
@app.route('/<int:product_id>', methods=['GET'])
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = products.get(product_id)

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(product), 200


# Update product stock
@app.route('/<int:product_id>/stock', methods=['PUT'])
@app.route('/products/<int:product_id>/stock', methods=['PUT'])
def update_product_stock(product_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid data"}), 400

    stock = data.get('stock')

    if type(stock) is not int or stock < 0:
        return jsonify({
            "error": "Stock must be a non-negative integer"
        }), 400

    product = products.get(product_id)

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    product['stock'] = stock

    return jsonify(product), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5032, debug=True)
