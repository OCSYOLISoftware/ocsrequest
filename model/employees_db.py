import sqlite3
from model.handle_db import HandleDB

class EmployeesDB(HandleDB):
    def insert_employee(
        self,
        employee_id: int,
        firstname: str,
        lastname: str,
        position_id: int,
        hiredate: str,
        branch_id: int,
        modality_id: int,
        status_id: int  # Añadir status_id como parámetro
    ):
        """
        Inserta un nuevo empleado en la tabla employees.
        """
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO employees (
                    employee_id, firstname, lastname, position_id,
                    hiredate, branch_id, modality_id, status_id  -- Añadir status_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    employee_id, firstname, lastname, position_id, hiredate, branch_id, modality_id, status_id
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al insertar el empleado: {e}")
            raise
        finally:
            conn.close()

    def get_all_employees(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT 
                    e.employee_id, 
                    e.firstname, 
                    e.lastname,
                    GROUP_CONCAT(d.department, ', ') AS department,  -- Concatenar departamentos separados por coma
                    p.position AS position,  
                    b.branch AS branch,  
                    m.modality AS modality,
                    STRFTIME('%m-%d-%Y', e.hiredate) AS hiredate, 
                    e.update_date,
                    es.status AS active_status  -- Cambiar a 'status' de la tabla 'employee_status'
                FROM employees e
                LEFT JOIN positions p ON e.position_id = p.position_id
                LEFT JOIN branches b ON e.branch_id = b.branch_id
                LEFT JOIN modalities m ON e.modality_id = m.modality_id
                LEFT JOIN employee_departments ed ON e.employee_id = ed.employee_id 
                LEFT JOIN departments d ON ed.department_id = d.department_id
                LEFT JOIN employee_status es ON e.status_id = es.status_id  -- Relación con employee_status
                GROUP BY e.employee_id, e.firstname, e.lastname, p.position, b.branch, m.modality, e.hiredate, e.update_date, es.status;
                """
            )
            data = cur.fetchall()
            #print("Datos obtenidos:", data) 
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener los empleados: {e}")
            raise
        finally:
            conn.close()

    def get_employee_by_id(self, employee_id: int):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT e.employee_id, e.firstname, e.lastname, e.hiredate, 
                    p.position_id, p.position,  
                    b.branch_id, b.branch,  
                    m.modality_id, m.modality,
                    ed.department_id, d.department,
                    e.status_id, es.status  -- Incluir status_id y status
                FROM employees e
                LEFT JOIN positions p ON e.position_id = p.position_id
                LEFT JOIN branches b ON e.branch_id = b.branch_id
                LEFT JOIN modalities m ON e.modality_id = m.modality_id
                LEFT JOIN employee_departments ed ON e.employee_id = ed.employee_id
                LEFT JOIN departments d ON ed.department_id = d.department_id
                LEFT JOIN employee_status es ON e.status_id = es.status_id  -- Relación con employee_status
                WHERE e.employee_id = ?;
                """,
                (employee_id,),
            )
            data = cur.fetchone()
            if data:
                return {
                    "employee_id": data[0],
                    "firstname": data[1],
                    "lastname": data[2],
                    "hiredate": data[3],
                    "position_id": data[4],
                    "position": data[5],
                    "branch_id": data[6],
                    "branch": data[7],
                    "modality_id": data[8],
                    "modality": data[9],
                    "department_id": data[10],
                    "department": data[11],
                    "status_id": data[12],  # Incluir el status_id
                    "status": data[13],  # Incluir el nombre del status
                }
            return None
        except sqlite3.Error as e:
            print(f"Error al obtener el empleado: {e}")
            raise
        finally:
            conn.close()

    def update_employee(self, employee_id, firstname, lastname, position_id, branch_id, modality_id, hiredate, department_id, status_id):
        conn = self._connect()
        cursor = conn.cursor()
        try:
            print(f"Updating employee with ID {employee_id}")
            print(f"Received status_id: {status_id}")

            # Validar si el status_id es válido (por ejemplo, entre 1 y 2 si son los únicos valores)
            if status_id not in [1, 2]:
                raise ValueError(f"Invalid status_id value: {status_id}")

            # Actualizar los datos del empleado
            cursor.execute("""
                UPDATE employees
                SET firstname = ?, lastname = ?, position_id = ?, branch_id = ?, modality_id = ?, hiredate = ?, status_id = ?
                WHERE employee_id = ?
            """, (firstname, lastname, position_id, branch_id, modality_id, hiredate, status_id, employee_id))
            conn.commit()

            # Verificar si ya existe la relación exacta employee_id - department_id
            cursor.execute("""
                SELECT 1 FROM employee_departments WHERE employee_id = ? AND department_id = ?
            """, (employee_id, department_id))
            existing_relation = cursor.fetchone()

            if not existing_relation:
                # Primero eliminamos cualquier relación previa para evitar duplicados
                cursor.execute("""
                    DELETE FROM employee_departments WHERE employee_id = ?
                """, (employee_id,))
                conn.commit()

                # Ahora insertamos la nueva relación
                cursor.execute("""
                    INSERT INTO employee_departments (employee_id, department_id)
                    VALUES (?, ?)
                """, (employee_id, department_id))
                conn.commit()

        except sqlite3.Error as e:
            raise Exception(f"Error al actualizar el empleado: {e}")
        finally:
            conn.close()

    def get_employees_by_department(self, employee_id: int):
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                query = """
                SELECT 
                    e.employee_id, 
                    e.firstname || ' ' || e.lastname AS name
                FROM employees e
                JOIN employee_departments ed ON e.employee_id = ed.employee_id
                WHERE ed.department_id IN (
                    SELECT ds.department_id
                    FROM department_supervisor ds
                    JOIN supervisors s ON ds.supervisor_id = s.supervisor_id
                    JOIN users u ON s.employee_id = u.employee_id
                    WHERE u.employee_id = ?
                )
                AND e.employee_id != ?
                GROUP BY e.employee_id, e.firstname, e.lastname;
                """
                # Si employee_id es el supervisor, pasas el mismo employee_id para ambos parámetros
                cur.execute(query, (employee_id, employee_id))
                rows = cur.fetchall()
                employees_by_department = [{"employee_id": row[0], "name": row[1]} for row in rows]
                return employees_by_department
        except sqlite3.Error as e:
            print(f"Error al obtener los empleados ligados al supervisor: {e}")
            raise

    def get_employee_counts(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT 
                    COUNT(*) AS total,
                    SUM(CASE WHEN m.modality_id = 1 THEN 1 ELSE 0 END) AS site,
                    SUM(CASE WHEN m.modality_id = 2 THEN 1 ELSE 0 END) AS home_office,
                    SUM(CASE WHEN m.modality_id = 3 THEN 1 ELSE 0 END) AS hybrid
                FROM employees e
                LEFT JOIN modalities m ON e.modality_id = m.modality_id
                LEFT JOIN employee_status es ON e.status_id = es.status_id
                WHERE es.status_id = 1; -- Filtrar solo empleados activos (status_id = 1)
            """)
            data = cur.fetchone()
            return {
                "total": data[0],
                "site": data[1],
                "home_office": data[2],
                "hybrid": data[3]
            }
        except sqlite3.Error as e:
            print(f"Error al obtener el conteo de empleados: {e}")
            return None
        finally:
            conn.close()