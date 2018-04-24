from flask import Flask, jsonify
from query import *
from firebase import *
from firebase_admin import db

app = Flask(__name__)

@app.route("/")
def home():
    return "hello world!"

@app.route("/update")
def update():
    update_data = check_twitter() 
    return jsonify(update_data)

@app.route("/links")
def links():
    link_resources_in_db = [value["link"] for key, value in db.reference("resources").get().items() if value["resource_type"] == "link"]
    return jsonify(link_resources_in_db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
