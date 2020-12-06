"""
export database: mysqldump -u username -p database_name > data-dump.sql
import database:
    mysql -u root -p
    CREATE DATABASE new_database;
    mysql -u username -p new_database < data-dump.sql
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
import pandas as pd
import os


class DatabaseClient:
    def __init__(self):
        self._username = ""
        self._password = ""
        self.localDir = os.path.dirname(os.path.realpath(__file__))
        self.readAuthority()

        self.engine = create_engine(
            'mysql+pymysql://{}:{}@localhost:3306/finance'.format(self._username, self._password))
        # self.mydb = MySQLdb.connect(
        #     host="localhost",
        #     port=3306,
        #     user=self._username,
        #     password=self._password,
        #     db = "finance"
        # )
        DB_Session = sessionmaker(bind=self.engine)
        self.session = DB_Session()
        # self.mycursor.execute("USE finance")

    def disconnect(self):
        self.session.close()

    def readAuthority(self):
        with open(os.path.join(self.localDir, "password.txt"), 'r') as file:
            lines = file.readlines()
            if len(lines) != 2:
                print("Alert: cannot read username and password!")
                return
            self._username = lines[0].rstrip('\n')
            self._password = lines[1].rstrip('\n')

    """
    show methods
    """

    def showTable(self, tableName):
        df = pd.read_sql("SELECT * FROM " + tableName, con=self.engine)
        print(df)
        print("====================")

    def tableExist(self, tableName):
        return self.engine.dialect.has_table(self.engine, tableName)

    def showAllTables(self):
        df = pd.read_sql("SHOW TABLES", con=self.engine)
        print(df)
        print("====================")

    """
    read methods
    """

    def readTableNames(self):
        return pd.read_sql("SHOW TABLES", con=self.engine)

    def readTable(self, tableName):
        return pd.read_sql("SELECT * FROM " + tableName, con=self.engine)

    def readColumn(self, colName, tableName):
        """
        @param colName:
        @param tableName:
        @return:
        """
        return pd.read_sql("SELECT {} FROM {}".format(colName, tableName), con=self.engine)

    def readUnderHardCondition(self, tableName, condition):
        """
        @param tableName:
        @param condition: name = 'Mike' or key = 1
        @return:
        """
        return pd.read_sql("SELECT * FROM {} WHERE {}".format(tableName, condition), con=self.engine)

    def readUnderSoftCondition(self, tableName, colName, pattern):
        """
        @param tableName:
        @param colName: e.g. name
        @param pattern: e.g. 'Mi%'
        @return:
        """
        return pd.read_sql("SELECT * FROM {} WHERE {} LIKE {}".format(tableName, colName, pattern), con=self.engine)

    def readRows(self, tableName, start, length):
        return pd.read_sql("SELECT * FROM {} LIMIT {} OFFSET {}".format(tableName, length, start), con=self.engine)

    """
    store methods
    """

    def createTable(self, tableName, head, primaryKey):
        """
        @param tableName:
        @param head: name type
        @param primaryKey:
        @return:
        """
        self.session.execute("CREATE TABLE {} ({}, PRIMARY KEY ({}));".format(tableName, ','.join(head), primaryKey))

    def insertData(self, tableName, values):
        temp = self.readTable(tableName)
        head = temp.head()

        pattern = "INSERT INTO {:} ({:}) VALUES ({:});"

        if isinstance(values, list):
            if len(values) == len(head):
                strValue = [str(value) for value in values]
                command = pattern.format(tableName, ",".join(head), self.mergeString(strValue))
                print("command:", command)
                self.session.execute(command)
            else:
                print("wrong value list length: wanted", len(head), ", got", len(values))
        elif isinstance(values, dict):
            command = pattern.format(tableName, ",".join(values.keys()), self.mergeString(values.values()))
            print("command:", command)
            self.session.execute(command)

    def storeData(self, tableName, dataFrame, ifExists='fail'):
        dataFrame.to_sql(tableName, con=self.engine, if_exists=ifExists, index=False)

    def updateData(self, tableName, pair, condition=None):
        """
        @param tableName:
        @param pair: dict (key, value)
        @param condition: e.g. name = 'Bob'
        @return:
        """
        conditionStr = ""
        if condition:
            condition = "WHERE {}".format(condition)
        for key, value in pair.items():
            self.session.execute("UPDATE {} SET {} = {} {};".format(tableName, key, value, condition))

    """
    Drop (Delete) table
    """

    def deleteTable(self, tableName):
        self.session.execute("DROP TABLE IF EXISTS {};".format(tableName))

    def mergeString(self, values):
        ret = ""
        for index, value in enumerate(values):
            if isinstance(value, str):
                ret += "\'"+value+"\'"
            if index < len(values)-1:
                ret += ","
        return ret


if __name__ == '__main__':
    client = DatabaseClient()
    client.showAllTables()
    client.showTable("fonds")
