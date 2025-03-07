import sqlite3

#-----------------------------Data base connection------------------------------------------------------------------------------
class HandleDB():
    def __init__(self, db_path="./ocsrequest.db"):
        self.db_path = db_path
        
    def _connect(self):
        #Crear una nueva conexion para cada solicitud
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
#-----------------------------Users Table-----------------------------------------------------------------------------------------
    def get_all(self):
        #Obtener todos los usuarios desde la base de datos
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        data = cur.fetchall()
        conn.close() #Cerrar la conexion despues de la consulta
        return data
    
    def get_only(self, data_user):
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
        user_id: int,  # Esto se dejará como None si no se quiere asignar
        requestdate: str,  # Formato: 'YYYY-MM-DD'
    ):
        """
        Inserta una nueva solicitud en la tabla requests.
        """
        conn = self._connect()
        cur = conn.cursor()
        try:
            # Si user_id es None, se insertará NULL en la base de datos
            if user_id is None:
                user_id = None  # Asegúrate de que el valor sea None en lugar de un número predeterminado

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
                    rs.reason AS reason,
                    r.notes,
                    st.status AS status,
                    r.requestdate,
                    u.firstname || ' ' || u.lastname AS assigned_employee_name, -- Nombre completo de la persona que se hará cargo
                    r.updatedate
                FROM requests r
                LEFT JOIN employees e ON r.employee_id = e.employee_id       -- Obtener empleado
                LEFT JOIN employees s ON r.supervisor_id = s.employee_id     -- Obtener supervisor
                LEFT JOIN departments d ON r.department_id = d.department_id
                LEFT JOIN warnings w ON r.warning_id = w.warning_id
                LEFT JOIN status st ON r.status_id = st.status_id
                LEFT JOIN reasons rs ON r.reason_id = rs.reason_id
                LEFT JOIN users us ON r.user_id = us.user_id                 -- Obtener el usuario que se hará cargo
                LEFT JOIN employees u ON us.employee_id = u.employee_id;     -- Obtener el nombre completo del encargado de la solicitud



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
                    CASE 
                        WHEN e.active = 1 THEN 'Active'
                        WHEN e.active = 2 THEN 'Inactive'
                        ELSE 'Unknown'
                    END AS active_status
                FROM employees e
                LEFT JOIN positions p ON e.position_id = p.position_id
                LEFT JOIN branches b ON e.branch_id = b.branch_id
                LEFT JOIN modalities m ON e.modality_id = m.modality_id
                LEFT JOIN employee_departments ed ON e.employee_id = ed.employee_id 
                LEFT JOIN departments d ON ed.department_id = d.department_id
                GROUP BY e.employee_id, e.firstname, e.lastname, p.position, b.branch, m.modality, e.hiredate, e.update_date, e.active;
  
                """
            )
            data = cur.fetchall()
            print("Datos obtenidos:", data)  # Depuración
            return data
        except sqlite3.Error as e:
            print(f"Error al obtener las solicitudes: {e}")
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
                    ed.department_id, d.department
                FROM employees e
                LEFT JOIN positions p ON e.position_id = p.position_id
                LEFT JOIN branches b ON e.branch_id = b.branch_id
                LEFT JOIN modalities m ON e.modality_id = m.modality_id
                LEFT JOIN employee_departments ed ON e.employee_id = ed.employee_id
                LEFT JOIN departments d ON ed.department_id = d.department_id
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
                }
            return None
        except sqlite3.Error as e:
            print(f"Error al obtener el empleado: {e}")
            raise
        finally:
            conn.close()
            
    def update_employee(self, employee_id, firstname, lastname, position_id, branch_id, modality_id,  department_id, active):
        conn = sqlite3.connect("./ocsrequest.db")
        cursor = conn.cursor()
        try:
            # Agregar impresión para depuración
            print(f"Updating employee with ID {employee_id}")
            print(f"Received active status: {active}")

            cursor.execute("""
                UPDATE employees
                SET firstname = ?, lastname = ?, position_id = ?, branch_id = ?, modality_id = ?, active = ?
                WHERE employee_id = ?
            """, (firstname, lastname, position_id, branch_id, modality_id,  int(active), employee_id))

            conn.commit()

            # Actualizar la relación con department
            cursor.execute("""
                UPDATE employee_departments
                SET department_id = ?
                WHERE employee_id = ?
            """, (department_id, employee_id))

            conn.commit()

        except sqlite3.Error as e:
            raise Exception(f"Error al actualizar el empleado: {e}")
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

#--------------------------------------------supervisor----------------------------------------------------------------------------------------------------       
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


    def get_all_warnings(self):
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT warning_id, warning FROM warnings")
                warnings = [{"warning_id": row[0], "warning": row[1]} for row in cur.fetchall()]
                return warnings
        except sqlite3.Error as e:
            print(f"Error al obtener todas los warnings: {e}")

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
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT reason_id, reason FROM reasons")
                reasons = [{"reason_id": row[0], "reason": row[1]} for row in cur.fetchall()]
                return reasons
        except sqlite3.Error as e:
            print(f"Error al obtener todas las rasones: {e}")
            raise

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
    

    #------------------------------------------------Organizar funciones
    def get_all_positions(self):
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT position_id, position FROM positions")
                positions = [{"position_id": row[0], "position": row[1]} for row in cur.fetchall()]
                return positions
        except sqlite3.Error as e:
            print(f"Error al obtener los departamentos: {e}")
            raise
        
    def get_all_branches(self):
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT branch_id, branch FROM branches")
                branches = [{"branch_id": row[0], "branch": row[1]} for row in cur.fetchall()]
                return branches
        except sqlite3.Error as e:
            print(f"Error al obtener las sucursales: {e}")
            raise
        
    def get_all_modalities(self):
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT modality_id, modality FROM modalities")
                modalities = [{"modality_id": row[0], "modality": row[1]} for row in cur.fetchall()]
                return modalities
        except sqlite3.Error as e:
            print(f"Error al obtener todas las modalidades: {e}")
            raise
        
    #---------------Re organizar  son consultas de pantalla Request
    

                

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
##-----------------------Pruebas-----------------------------
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
