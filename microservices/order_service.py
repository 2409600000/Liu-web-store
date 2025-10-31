
from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

# Order data
orders = {}
order_id_counter = 1

# Health endpoint
@app.route('/health', methods=['GET'])
def get_health():
    return jsonify({"status": "All good"}), 200

@app.route('/', methods=['POST'])
def create_order():
    return jsonify({"error": "not implemented"}, 501) # TODO Implement the body of the POST endpoint

# TODO Implement GET order endpoint


def get_user_object(user_id:str):
    return None # TODO send GET request to user microservice to fetch user object

def get_product_object(product_id:str):
    return None # TODO send GET request to product microservice to fetch product object


def update_stock(product_id:str, stock:int):
    return None # TODO send PUT request to product microservice to set the stock

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5033, debug=True)