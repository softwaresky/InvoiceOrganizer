import sqlite3

SQL_CREATE_DB = """
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "lista_na_firmi" (
	"id"	INTEGER,
	"naziv"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "faktura" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"firma_id"	INTEGER,
	"druga_firma_id"	INTEGER,
	"tip_faktura_id"	INTEGER,
	"reden_broj"	INTEGER,
	"data_na_priem"	TEXT,
	"data_na_faktura"	TEXT,
	"broj_na_faktura"	TEXT,
	"iznos"	REAL,
	"zabeleska"	TEXT,
	FOREIGN KEY("tip_faktura_id") REFERENCES "firma"("id"),
	FOREIGN KEY("druga_firma_id") REFERENCES "lista_na_firmi"("id")
);
CREATE TABLE IF NOT EXISTS "tip_faktura" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"tip"	INTEGER,
	"ime"	TEXT
);
CREATE TABLE IF NOT EXISTS "firma" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"ime"	TEXT
);
INSERT INTO "tip_faktura" VALUES (1,1,'влезна');
INSERT INTO "tip_faktura" VALUES (2,2,'излезна');
COMMIT;
"""

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class SmetKnigaDB:

    def __init__(self, db_path=""):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)

    def close_connection(self):
        self.conn.close()

    def sql_execute(self, sql_query="", is_insert = False):

        self.cursor = self.conn.cursor()
        if is_insert:
            self.cursor.execute(sql_query)
            self.conn.commit()
            return None
        else:
            self.cursor.row_factory = dict_factory
            self.cursor.execute(sql_query)
            return self.cursor.fetchall()


    def get_firma(self):
        lst_result = self.sql_execute(sql_query="SELECT * FROM firma")
        return lst_result

    def insert_firma(self, name = ""):
        sql_query = "INSERT INTO firma (ime) VALUES ('{0}')".format(name)
        self.sql_execute(sql_query=sql_query, is_insert=True)

    def get_tip_faktura(self):
        lst_result = self.sql_execute(sql_query="SELECT * FROM tip_faktura")
        return lst_result

    def get_fakturi(self, firma_id=0, tip_faktura_id=0):

        # lst_result = self.sql_execute(sql_query="SELECT * FROM faktura WHERE firma_id='{0}' AND tip_faktura_id='{1}'".format(firma_id, tip_faktura_id))
        sql_query = """
        SELECT faktura.id, faktura.reden_broj, lista_na_firmi.naziv, tip_faktura.ime, faktura.broj_na_faktura, faktura.data_na_priem, faktura.data_na_faktura, faktura.iznos, faktura.zabeleska
        FROM faktura, tip_faktura, lista_na_firmi
        WHERE firma_id='{0}' AND faktura.tip_faktura_id=tip_faktura.id AND faktura.druga_firma_id=lista_na_firmi.id AND faktura.tip_faktura_id='{1}'
        """.format(firma_id, tip_faktura_id)
        lst_result = self.sql_execute(sql_query=sql_query)
        return lst_result

    def insert_faktura(self, firma_id=-1, tip_faktura_id=-1, druga_firma_id=-1, reden_broj=-1, data_na_priem='', data_na_faktura='', broj_na_faktura='', iznos=0.0, zabeleska=''):
        sql_query = """
        INSERT INTO faktura(firma_id, tip_faktura_id, druga_firma_id, reden_broj, data_na_priem, data_na_faktura, broj_na_faktura, iznos, zabeleska)
                    VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')
        """.format(firma_id, tip_faktura_id, druga_firma_id, reden_broj, data_na_priem, data_na_faktura, broj_na_faktura, iznos, zabeleska)
        self.sql_execute(sql_query=sql_query, is_insert=True)

    def remove_faktura(self, faktura_id=-1):
        sql_query = "DELETE FROM faktura WHERE id = '{0}'".format(faktura_id)
        self.sql_execute(sql_query=sql_query, is_insert=True)

    def remove_firma(self, firma_id=-1):
        sql_query = "DELETE FROM firma WHERE id = '{0}'".format(firma_id)
        self.sql_execute(sql_query=sql_query, is_insert=True)

    def get_last_record(self, table_name=""):
        if table_name:
            self.cursor = self.conn.cursor()
            self.cursor.row_factory = dict_factory
            self.cursor.execute("SELECT * FROM '{0}' ORDER BY id DESC LIMIT 1".format(table_name))
            return self.cursor.fetchone()
        else:
            return None

    def get_lista_na_firmi(self):
        lst_result = self.sql_execute(sql_query="SELECT * FROM lista_na_firmi ORDER BY naziv")
        return lst_result

    def insert_druga_firma(self, naziv=""):
        sql_query = "INSERT INTO lista_na_firmi (naziv) VALUES ('{0}')".format(naziv)
        self.sql_execute(sql_query=sql_query, is_insert=True)

    def remove_all_row(self, table_name=""):
        self.sql_execute(sql_query="delete from {0};".format(table_name), is_insert=True)