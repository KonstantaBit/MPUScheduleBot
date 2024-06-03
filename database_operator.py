import sqlite3
import logging


class Operator:
    DB_FILE = 'db.db'

    def __init__(self):

        con = sqlite3.connect(self.DB_FILE)
        cursor = con.cursor()
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS groups(
                   group_n TEXT UNIQUE PRIMERY KEY,
                   hash_json TEXT)''')
        except (sqlite3.Error, sqlite3.Warning) as err:
            logging.error(err)
        finally:
            con.commit()
            con.close()

    def check_hash(self, group: str, hash: str) -> bool:
        con = sqlite3.connect(self.DB_FILE)
        cursor = con.cursor()
        try:
            cursor.execute('''SELECT hash_json FROM groups WHERE group_n = :group''', {'group': group})
            logging.debug(f'Hash checked')
            return cursor.fetchone() == hash
        except (sqlite3.Error, sqlite3.Warning) as err:
            logging.error(err)
        finally:
            con.commit()
            con.close()
            return False

    def check_group(self, group: str) -> bool:
        con = sqlite3.connect(self.DB_FILE)
        cursor = con.cursor()
        try:
            cursor.execute('''SELECT group_n FROM groups WHERE group_n = :group''', {'group': group})
            logging.debug(f'Group checked')
            return cursor.fetchone()
        except (sqlite3.Error, sqlite3.Warning) as err:
            logging.error(err)
        finally:
            con.commit()
            con.close()
            return False

    def add_record(self, group: str, hash: str) -> None:
        con = sqlite3.connect(self.DB_FILE)
        cursor = con.cursor()
        try:
            cursor.execute('''INSERT INTO groups (group_n, hash_json) VALUES (:group, :hash)''', {'group': group, 'hash': hash})
            logging.info(f'Record added - {group} {hash}')
        except (sqlite3.Error, sqlite3.Warning) as err:
            logging.error(err)
        finally:
            con.commit()
            con.close()

    def update_record(self, group: str, hash: str) -> None:
        con = sqlite3.connect(self.DB_FILE)
        cursor = con.cursor()
        try:
            cursor.execute('''UPDATE groups SET hash_json = :hash WHERE group_n = :group''', {'group': group, 'hash': hash})
            logging.info(f'Record updated - {group} {hash}')
        except (sqlite3.Error, sqlite3.Warning) as err:
            logging.error(err)
        finally:
            con.commit()
            con.close()

    def get_all_records(self) -> list:
        con = sqlite3.connect(self.DB_FILE)
        cursor = con.cursor()
        try:
            cursor.execute('''SELECT * FROM groups''')
            return cursor.fetchall()
        except (sqlite3.Error, sqlite3.Warning) as err:
            logging.error(err)
        finally:
            con.commit()
            con.close()