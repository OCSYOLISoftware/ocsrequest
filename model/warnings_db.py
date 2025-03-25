import sqlite3
from model.handle_db import HandleDB

class WarningDB(HandleDB):
    def get_all_warnings(self):
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT warning_id, warning FROM warnings")
                warnings = [{"warning_id": row[0], "warning": row[1]} for row in cur.fetchall()]
                return warnings
        except sqlite3.Error as e:
            print(f"Error al obtener todas los warnings: {e}")