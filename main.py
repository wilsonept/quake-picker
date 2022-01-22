from flask import Flask
import database
from json_reader import load_json
from application import app



@app.route("/")
def home():
    return "<h1>quakePicker</h1>"

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000, debug=True)