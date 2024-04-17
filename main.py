import xmlrpc.client
from dotenv import load_dotenv
import os
import json
from flask_cors import CORS, cross_origin

load_dotenv(override=False)

url = os.environ.get("URL")
db = os.environ.get("DB")
username = os.environ.get("USER")
password = os.environ.get("PASSWORD")

# aplicacion FLASK
from flask import Flask, jsonify
app = Flask(__name__)
cors = CORS(app)

@app.route("/")
def hello_world():
    return "<h1>Hello, World!</h1>"


@app.route("/products/<int:barcode>")
def product(barcode: int):

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    version = common.version()

    uid = common.authenticate(db, username, password, {})

    # Llamada a metodo a traves de execute_kw
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    product_template = models.execute_kw(db, uid, password, 'product.template', 'search_read', [[('barcode', '=',  str(barcode))]], {'fields': ['id', 'description', 'name', 'barcode']})
    
    if len(product_template) == 0:
         return jsonify("producto no existe"), 404

    # search the product
    product_id = product_template[0]['id']


    # Changes the Product Quantity by creating/editing corresponding quant.
    quantityy = models.execute_kw(db, uid, password, 'stock.change.product.qty', 'search_read', [[]], {'fields': ['new_quantity']})
   
    lastQuantity = quantityy[-1]['new_quantity']

    stock_change_product_qty_id = models.execute_kw(db, uid, password, 'stock.change.product.qty', 'create', [{

    'product_id': product_id,

    'product_tmpl_id': 1,

    'new_quantity': lastQuantity + 1,

    }])

    # Method Trigger: change_product_qty

    models.execute_kw(db, uid, password, 'stock.change.product.qty', 'change_product_qty', [stock_change_product_qty_id])

    return jsonify("producto agregado exitosamente"), 200

