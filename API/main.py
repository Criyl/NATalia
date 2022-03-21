import os
import re
from flask import Flask, jsonify, request
from ml import PredictionModel
from ml.serialize import PickleSerializer, SQLSerializer

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

HOST_DOMAIN = os.getenv("HOST_DOMAIN")
HOST_PORT = os.getenv("HOST_PORT")

serializer = SQLSerializer(DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME)
model: PredictionModel
app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/top', methods=['GET'])
def top():
    temp = model.dataframe.copy()
    temp['diff'] = temp['word|pos'] - temp['word|neg']
    temp = temp.sort_values(by=['diff'], ascending=False)
    return temp.to_json()


@app.route('/predict', methods=['GET'])
def predict():
    args = request.args
    positivity = model.message_is_positive(args['msg'])
    return "%s" % positivity


@app.route('/add', methods=['POST'])
def add():
    jsonRequest = request.get_json()
    text = jsonRequest["text"]
    positive = jsonRequest["positive"]

    app.logger.info("Model:\n%s" % model)
    model.add_data(text, positive)

    wordList = re.split("[\W]+", text)
    tempDict = {}
    for words in wordList:
        tempDict[words] = False

    unique = tempDict.keys()
    df = model.dataframe
    filtered = df[df.index.isin(unique)]
    return filtered.to_json()


@app.route('/save', methods=['GET'])
def save():
    serializer.save(model)
    return "saved database"


if __name__ == '__main__':
    model = serializer.load
    print("loaded")
    app.run(host=HOST_DOMAIN, port=int(HOST_PORT))
    serializer.save(model)
