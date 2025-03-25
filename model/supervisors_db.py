import sqlite3
from model.handle_db import HandleDB

class SupervisorDB(HandleDB):
    def insert_supervisors(self, supervisor_id, employee_id: int):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO supervisors (supervisor_id,employee_id)
                VALUES (?, ?)
                """,
                (supervisor_id, employee_id)
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al insertar en employee_departments: {e}")
            raise
        finally:
            conn.close()

    def get_supervisor_for_current_user(self, username: str):
        try:
            with self._connect() as conn:
                cur = conn.cursor()

                query = """
                SELECT e.employee_id, e.firstname || ' ' || e.lastname AS name
                FROM users u
                JOIN employees e ON u.employee_id = e.employee_id
                WHERE u.username = ?
                """

                cur.execute(query, (username,))
                row = cur.fetchone()

                if row:
                    return {"employee_id": row[0], "name": row[1]}
                else:
                    raise ValueError("No se encontró el supervisor para el usuario")

        except sqlite3.Error as e:
            print(f"Error al obtener el supervisor: {e}")
            raise