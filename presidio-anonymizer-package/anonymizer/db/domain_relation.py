import sqlite3
from db.db import Get_DB_Data


class Domain_Relation:
    '''Create Domain relation related data'''

    def __init__(self):
        sql_create_maxid_table = """ CREATE TABLE IF NOT EXISTS domain_maxid (
                                        domain text PRIMARY KEY,
                                        max_id integer NOT NULL
                                    ); """
 
        sql_create_attr_table = """CREATE TABLE IF NOT EXISTS domain_attr (
                                    domain text NOT NULL,
                                    alias text NOT NULL,
                                    value text NOT NULL,
                                    FOREIGN KEY(domain) REFERENCES domain_maxid(domain)
                                );"""

        try:
            self.conn = Get_DB_Data().get_db_connection()
            cur = self.conn.cursor()
            cur.execute(sql_create_maxid_table)
            cur.execute(sql_create_attr_table)
            self.conn.commit()

        except Exception as e:
            print(e)
            raise e

    def insert_max_id(self, domain_maxid_tuple):
        '''Insert domain and associated max id in the table

        Parameters
        ----------
        domain_maxid_tuple : tuple (text, integer)
            A tuple containing domain_name and max_id

        '''

        insert_statement = 'INSERT OR REPLACE INTO domain_maxid (domain, max_id) VALUES (?, ?)'
        cur = self.conn.cursor()
        try:
            cur.execute(insert_statement, domain_maxid_tuple)
            self.conn.commit()
        except Exception as e:
            print(e)
            raise e
        return cur.lastrowid
        
    def insert_domain_attr(self, domain_attr_tuple):
        '''Insert domain attributes in the domain_attr table

        Parameters
        ----------
        domain_attr_tuple : tuple (text, text, text)
            A tuple containing domain_name, alias and value
        '''

        insert_statement = 'INSERT INTO domain_attr (domain, alias, value) VALUES (?, ?, ?)'
        cur = self.conn.cursor()
        try:
            cur.execute(insert_statement, domain_attr_tuple)
            self.conn.commit()
        except Exception as e:
            print(e)
            raise e
        return cur.lastrowid
        
    def get_domain_attr(self):
        '''Show domains and attributes'''

        select_statement = 'SELECT domain_attr.*, domain_maxid.max_id FROM domain_maxid INNER JOIN domain_attr ON domain_maxid.domain = domain_attr.domain'
        cur = self.conn.cursor()
        try:
            cur.execute(select_statement)
        except Exception as e:
            print(e)
            raise e
        return cur.fetchall()

    def get_domain_attr_by_domain(self, domain_name):
        '''Get attributes by given domain name

        Parameters
        ----------
        domain_name : text
            A str of domain_name
        '''

        select_statement = 'SELECT domain_attr.*, domain_maxid.max_id FROM domain_maxid INNER JOIN domain_attr ON domain_maxid.domain = domain_attr.domain WHERE domain_maxid.domain = ?'
        cur = self.conn.cursor()
        try:
            cur.execute(select_statement, (domain_name,))
        except Exception as e:
            print(e)
            raise e
        return cur.fetchall()
