import os
import pandas as pd
from ml import PredictionModel, read_stop
from ml.serialize import PickleSerializer,SQLSerializer

DB_HOST = os.getenv('DB_HOST', "")
DB_PORT = os.getenv("DB_PORT", 0)
DB_USER = os.getenv("DB_USER", "")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "")


if __name__ == '__main__':
    pSer = PickleSerializer("model.pkl", "stop.txt")
    sqlSer = SQLSerializer(DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME)

    model = pSer.load()
    sqlSer.save(model)