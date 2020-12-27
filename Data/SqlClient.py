"""
export database: mysqldump -u username -p database_name > data-dump.sql
import database:
    mysql -u root -p
    CREATE DATABASE new_database;
    mysql -u username -p new_database < data-dump.sql
"""

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

import pymysql
import numpy as np
import pandas as pd
import os


class DatabaseClient:
    def __init__(self):
        self._username = ""
        self._password = ""
        self.localDir = os.path.dirname(os.path.realpath(__file__))
        self.readAuthority()

        self.db = pymysql.connect(
            host='localhost',
            port=3306,
            user=self._username,
            passwd=self._password,
            db='finance',
            charset='utf8'
        )

        # self.engine = create_engine(
        #     'mysql+pymysql://{}:{}@localhost:3306/finance'.format(self._username, self._password))
        # DB_Session = sessionmaker(bind=self.engine)
        # self.session = DB_Session()
        # self.mycursor.execute("USE finance")

    def disconnect(self):
        self.db.close()

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
        df = pd.read_sql("SELECT * FROM " + tableName, con=self.db)
        print(df)
        print("====================")

    def tableExist(self, table_name):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{0}'".format(table_name))
            data = cursor.fetchone()
            if data and len(data) > 0:
                if data[0] == 1:
                    return True
                else:
                    return False

    def showAllTables(self):
        df = pd.read_sql("SHOW TABLES", con=self.db)
        print(df)
        print("====================")

    """
    read methods
    """

    def readTableNames(self):
        return pd.read_sql("SHOW TABLES", con=self.db)

    def readTable(self, tableName):
        return pd.read_sql("SELECT * FROM " + tableName, con=self.db)

    def readColumn(self, colName, tableName):
        """
        @param colName:
        @param tableName:
        @return:
        """
        return pd.read_sql("SELECT {} FROM {}".format(colName, tableName), con=self.db)

    def readUnderHardCondition(self, tableName, condition):
        """
        @param tableName:
        @param condition: name = 'Mike' or key = 1
        @return:
        """
        return pd.read_sql("SELECT * FROM {} WHERE {}".format(tableName, condition), con=self.db)

    def readUnderSoftCondition(self, tableName, colName, pattern):
        """
        @param tableName:
        @param colName: e.g. name
        @param pattern: e.g. 'Mi%'
        @return:
        """
        return pd.read_sql("SELECT * FROM {} WHERE {} LIKE {}".format(tableName, colName, pattern), con=self.db)

    def readRows(self, tableName, start, length):
        return pd.read_sql("SELECT * FROM {} LIMIT {} OFFSET {}".format(tableName, length, start), con=self.db)

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
        with self.db.cursor() as cursor:
            cursor.execute("CREATE TABLE {} ({}, PRIMARY KEY ({}));".format(tableName, ','.join(head), primaryKey))
        self.db.commit()

    def insertData(self, table_name, values, primary_key=None):
        temp = self.readTable(table_name)
        head = temp.head()

        if primary_key:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT {0} FROM {1} WHERE {0}=\'{2}\';".format(primary_key, table_name, values[primary_key]))
                data = cursor.fetchone()
                if data:
                    return

        pattern = "INSERT INTO {:} ({:}) VALUES ({:});"

        if isinstance(values, list):
            if len(values) == len(head):
                strValue = [str(value) for value in values]
                command = pattern.format(table_name, ",".join(head), self.mergeString(strValue))
                print("command:", command)
                with self.db.cursor() as cursor:
                    cursor.execute(command)
                self.db.commit()
            else:
                print("wrong value list length: wanted", len(head), ", got", len(values))
        elif isinstance(values, dict):
            command = pattern.format(table_name, ",".join(values.keys()), self.mergeString(values.values()))
            print("command:", command)
            with self.db.cursor() as cursor:
                cursor.execute(command)
            self.db.commit()

    def storeData(self, tableName, dataFrame, ifExists='fail'):
        dataFrame.to_sql(tableName, con=self.db, if_exists=ifExists, index=False)

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

        with self.db.cursor() as cursor:
            for key, value in pair.items():
                cursor.execute("UPDATE {} SET {} = {} {};".format(tableName, key, value, condition))
        self.db.commit()

    """
    Drop (Delete) table
    """

    def deleteTable(self, tableName):
        with self.db.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS {};".format(tableName))
        self.db.commit()

    def mergeString(self, values):
        ret = ""
        for index, value in enumerate(values):
            if isinstance(value, str):
                ret += "\'"+value+"\'"
            if isinstance(value, int):
                ret += str(value)
            if index < len(values)-1:
                ret += ","
        return ret


if __name__ == '__main__':
    client = DatabaseClient()
    client.showAllTables()
    client.showTable("fonds")
