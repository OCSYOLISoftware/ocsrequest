import sqlite3
from model.handle_db import HandleDB

class DepartmentDB(HandleDB):
    def get_all_departments(self):  #   Esta funcion es el ejemplo para modificar las de abajo
        try:
            # Usamos 'with' para manejar la conexión automáticamente
            with self._connect() as conn:
                # Creamos el cursor manualmente
                cur = conn.cursor()
                cur.execute("SELECT department_id, department FROM departments")
                departments = [{"department_id": row[0], "department": row[1]} for row in cur.fetchall()]
            return departments
        except sqlite3.Error as e:
            print(f"Error al obtener los departamentos: {e}")
            raise
        
    def get_departments_by_employee(self, employee_id):
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT d.department_id, d.department 
                    FROM departments d
                    JOIN employee_departments ed ON d.department_id = ed.department_id
                    WHERE ed.employee_id = ?
                    """,
                    (employee_id,),
                )
                return [
                    {"department_id": row[0], "department": row[1]}
                    for row in cur.fetchall()
                ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener los departamentos del empleado: {e}") from e
