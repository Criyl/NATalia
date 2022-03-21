from typing import Optional

import pandas as pd

from ml import PredictionModel, read_stop
from sqlalchemy import create_engine
from sqlalchemy.engine import Connectable


class Serializable:
    def save(self, model: PredictionModel) -> None:
        pass

    def load(self) -> PredictionModel:
        pass


class PickleSerializer(Serializable):
    filePath: str = None
    stopList: list = None

    def __init__(self, picklePath, stopPath):
        self.filePath = picklePath
        self.stopList = read_stop(stopPath)

    def save(self, model: PredictionModel) -> None:
        model.dataframe.to_pickle(self.filePath)

    def load(self) -> PredictionModel:
        return PredictionModel(pd.read_pickle(self.filePath), self.stopList)


class SQLSerializer(Serializable):
    DB_HOST = None
    DB_PORT = 0
    DB_USER = None
    DB_PASS = None
    DB_NAME = None
    dbConnection: Connectable

    modelTable = "model"
    stopTable = "stop"

    def __init__(self, dbHost, dbPort, dbUser, dbPass, dbName):

        self.DB_HOST = dbHost
        self.DB_PORT = dbPort
        self.DB_USER = dbUser
        self.DB_PASS = dbPass
        self.DB_NAME = dbName
        engine = create_engine('postgresql+psycopg2://%s:%s@%s:%s/%s' % (
            self.DB_USER, self.DB_PASS, self.DB_HOST, self.DB_PORT, self.DB_NAME),
                               pool_recycle=3600)
        self.dbConnection = engine.connect()

    def save(self, model: PredictionModel) -> None:
        try:
            model.dataframe.to_sql(self.modelTable, self.dbConnection, if_exists="replace")
        except ValueError as vx:
            print(vx)
        except Exception as ex:
            print(ex)
        else:
            print("PostgreSQL Table %s has been created successfully." % self.modelTable)

        try:
            pd.DataFrame(model.stop_list).to_sql(self.stopTable, self.dbConnection, if_exists="replace")
        except ValueError as vx:
            print(vx)
        except Exception as ex:
            print(ex)
        else:
            print("PostgreSQL Table %s has been created successfully." % self.stopTable)

    @property
    def load(self) -> PredictionModel:
        if not self.checkDB():
            return None
        try:
            dataFrame = pd.read_sql(self.modelTable, self.dbConnection)
            stopFrame = pd.read_sql(self.stopTable, self.dbConnection)
            return PredictionModel(dataFrame, stopFrame.values)
        except:
            return PredictionModel(None, [])

    def checkDB(self):
        return self.dbConnection is not None
