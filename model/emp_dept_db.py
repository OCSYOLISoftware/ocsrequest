import sqlite3
from model.handle_db import HandleDB

class EmployeeDepartmentDB(HandleDB):
    def insert_employee_department(self, employee_id: int, department_id: int):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO employee_departments (employee_id, department_id)
                VALUES (?, ?)
                """,
                (employee_id, department_id)
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al insertar en employee_departments: {e}")
            raise
        finally:
            conn.close()

    def update_employee_department(self, employee_id: int, department_id: int):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE employee_departments
                SET department_id = ?
                WHERE employee_id = ?;
                """,
                (department_id, employee_id),
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al actualizar el departamento del empleado: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()