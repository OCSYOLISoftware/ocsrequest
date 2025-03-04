import sqlite3

class HandleDB():
    def __init__(self, db_path="./ocsrequest.db"):
        self.db_path = db_path
        
    def _connect(self):
        #Crear una nueva conexion para cada solicitud
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def get_all(self):
        #Obtener todos los usuarios desde la base de datos
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        data = cur.fetchall()
        conn.close() #Cerrar la conexion despues de la consulta
        return data
    
    def get_only(self, data_user):
        #Obtener un ususario por employee_id
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (data_user,))
        data = cur.fetchone()
        conn.close()
        return data
    #obtiene el employee_id del usuario
    def get_employee_id_by_username(self, username: str):
        user_data = self.get_only(username)
        if user_data:
            return user_data[2]  # Suponiendo que employee_id es la tercera columna
        return None
    
    def insert(self, data_user):
        #Crear un nuevo usuario
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (employee_id, username, password_user) VALUES (?, ?, ?)",
                    (data_user['employee_id'], data_user['username'], data_user['password_user']))
        conn.commit()
        conn.close()
        
    def delete(self, username: str):
        #Eliminar un usuario por username
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
 #---------------------------------------------REQUEST---------------------------------------------------------------------------       
        #Insertar en request
    def insert_request(
        self,
        supervisor_id: int,
        employee_id: int,
        department_id: int,
        warning_id: int,
        reason_id: int,
        notes: str,
        user_id: int,
        requestdate: str,  # Formato: 'YYYY-MM-DD'
    ):
        """
        Inserta una nueva solicitud en la tabla requests.
        """
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO requests (
                    supervisor_id, employee_id, department_id, warning_id,
                    reason_id, notes, user_id, requestdate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    supervisor_id, employee_id, department_id, warning_id,
                    reason_id, notes, user_id, requestdate
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al insertar la solicitud: {e}")
            raise
        finally:
            conn.close()
            
        # Leer todas las solicitudes
    def get_all_requests(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT 
                     r.request_id,
                     s.firstname || ' ' || s.lastname AS supervisor_name, -- Nombre completo del supervisor
                    e.employee_id || ' - ' || e.firstname || ' ' || e.lastname AS employee_name,  -- Nombre completo del empleado
                    d.department AS department,
                    w.warning AS warning,
                    st.status AS status,
                    rs.reason AS reason,
                    r.notes,
                    r.requestdate,
                    r.updatedate
                FROM requests r
                LEFT JOIN employees e ON r.employee_id = e.employee_id       -- Obtener empleado
                LEFT JOIN employees s ON r.supervisor_id = s.employee_id     -- Obtener supervisor
                LEFT JOIN departments d ON r.department_id = d.department_id
                LEFT JOIN warnings w ON r.warning_id = w.warning_id
                LEFT JOIN status st ON r.status_id = st.status_id
                LEFT JOIN reasons rs ON r.reason_id = rs.reason_id;
                """
            )
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener las solicitudes: {e}")
            raise
        finally:
            conn.close()

    # Leer una solicitud por su request_id
    def get_request_by_id(self, request_id: int):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM requests WHERE request_id = ?", (request_id,))
            data = cur.fetchone()
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener la solicitud: {e}")
            raise
        finally:
            conn.close()

    # Actualizar una solicitud por su request_id
    def update_request(
        self,
        request_id: int,
        supervisor_id: int = None,
        employee_id: int = None,
        department_id: int = None,
        warning_id: int = None,
        status_id: int = None,
        reason_id: int = None,
        notes: str = None,
        user_id: int = None,
        requestdate: str = None,  # Formato: 'YYYY-MM-DD'
    ):
        conn = self._connect()
        cur = conn.cursor()
        try:
            # Construir la consulta dinámicamente
            query = "UPDATE requests SET "
            params = []
            if supervisor_id is not None:
                query += "supervisor_id = ?, "
                params.append(supervisor_id)
            if employee_id is not None:
                query += "employee_id = ?, "
                params.append(employee_id)
            if department_id is not None:
                query += "department_id = ?, "
                params.append(department_id)
            if warning_id is not None:
                query += "warning_id = ?, "
                params.append(warning_id)
            if status_id is not None:
                query += "status_id = ?, "
                params.append(status_id)
            if reason_id is not None:
                query += "reason_id = ?, "
                params.append(reason_id)
            if notes is not None:
                query += "notes = ?, "
                params.append(notes)
            if user_id is not None:
                query += "user_id = ?, "
                params.append(user_id)
            if requestdate is not None:
                query += "requestdate = ?, "
                params.append(requestdate)

            # Eliminar la última coma y agregar la condición WHERE
            query = query.rstrip(", ") + " WHERE request_id = ?"
            params.append(request_id)

            # Ejecutar la consulta
            cur.execute(query, tuple(params))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al actualizar la solicitud: {e}")
            raise
        finally:
            conn.close()

    # Eliminar una solicitud por su request_id
    def delete_request(self, request_id: int):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM requests WHERE request_id = ?", (request_id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al eliminar la solicitud: {e}")
            raise
        finally:
            conn.close()
            
#------------------------------Employee---------------------------------------------------------------------------------------------------------------------
        #Insertar en Employee
    def insert_employee(
        self,
        employee_id: int,
        firstname: str,
        lastname: str,
        position_id: int,
        hiredate: str,
        branch_id: int,
        modality_id: int
    ):
        """
        Inserta una nueva solicitud en la tabla employee.
        """
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO employees (
                    employee_id, firstname, lastname, position_id,
                    hiredate, branch_id, modality_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    employee_id, firstname, lastname, position_id, hiredate, branch_id, modality_id
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al insertar la solicitud: {e}")
            raise
        finally:
            conn.close()
            
        # Leer todas los empleados
    def get_all_employees(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM employees")
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener las solicitudes: {e}")
            raise
        finally:
            conn.close()
     #------------------------Employee_departments------------------------------------------------------------       
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
     #------------------------supervisor------------------------------------------------------------       
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

#----------------Todas las consultas a las tablas complementarias--------------------------------------------------------------------------------------------

    def get_all_employees(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT employee_id, firstname, lastname FROM employees")
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener los empleados: {e}")
            raise
        finally:
            conn.close()

    def get_all_departments(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT department_id, department FROM departments")
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener los departamentos: {e}")
            raise
        finally:
            conn.close()

    def get_all_warnings(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT warning_id, warning FROM warnings")
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener las advertencias: {e}")
            raise
        finally:
            conn.close()

    def get_all_status(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT status_id, status FROM status")
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener los estados: {e}")
            raise
        finally:
            conn.close()

    def get_all_reasons(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT reason_id, reason FROM reasons")
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener las razones: {e}")
            raise
        finally:
            conn.close()
            
    def get_all_positions(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT position_id, position FROM positions")
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener las razones: {e}")
            raise
        finally:
            conn.close()

    def get_all_branches(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT branch_id, branch FROM branches")
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener las razones: {e}")
            raise
        finally:
            conn.close()
            
    def get_all_modalities(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT modality_id, modality FROM modalities")
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener las razones: {e}")
            raise
        finally:
            conn.close()
# -------Prueba---------------------
    def get_employees_by_department(self, employee_id: int):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT e.*
                FROM employees e
                JOIN employee_departments ed ON e.employee_id = ed.employee_id
                WHERE ed.department_id IN (
                    SELECT ds.department_id
                    FROM department_supervisor ds
                    JOIN supervisors s ON ds.supervisor_id = s.supervisor_id
                    JOIN users u ON s.employee_id = u.employee_id
                    WHERE u.employee_id = ?
                )
                """,
                (employee_id,)
            )
            data = cur.fetchall()
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener los empleados: {e}")
            raise
        finally:
            conn.close()
 #----------------------------------------------------------------------------------       
    def __del__(self):
        #Cerrar ;a conexion al final 
        pass
    
    