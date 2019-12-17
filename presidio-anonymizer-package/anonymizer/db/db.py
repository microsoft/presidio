import json
import sqlite3
import os


class Get_DB_Data:
    '''Get DB Data Conection'''
    def get_db_connection(self):
        '''Connect to SQLite DB and return a connection'''
        file_path = os.path.dirname(os.path.abspath(__file__))
        connection = None
        with open(file_path + '/config_local.json') as db_config_file:
            db_data = json.load(db_config_file)
        db_path = file_path + '/' + db_data['sqlite_path']
        
        try:
            connection = sqlite3.connect(db_path)
            return connection
        except Exception as e:
            print(e)
        
        return connection