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
            return user_data[2]  
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
    def get_all_requests(self, supervisor_id):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT 
                    r.request_id, 
                    s.firstname || ' ' || s.lastname AS supervisor_name, 
                    e.employee_id || ' - ' || e.firstname || ' ' || e.lastname AS employee_name,  
                    d.department AS department,
                    w.warning AS warning,
                    rs.reason AS reason,
                    r.notes,
                    st.status AS status,
                    r.requestdate,
                    u.firstname || ' ' || u.lastname AS assigned_employee_name, 
                    r.updatedate
                FROM requests r
                LEFT JOIN employees e ON r.employee_id = e.employee_id       
                LEFT JOIN employees s ON r.supervisor_id = s.employee_id     
                LEFT JOIN departments d ON r.department_id = d.department_id
                LEFT JOIN warnings w ON r.warning_id = w.warning_id
                LEFT JOIN status st ON r.status_id = st.status_id
                LEFT JOIN reasons rs ON r.reason_id = rs.reason_id
                LEFT JOIN users us ON r.user_id = us.user_id                 
                LEFT JOIN employees u ON us.employee_id = u.employee_id    
                WHERE r.supervisor_id = :supervisor_id;
                """,
                {"supervisor_id": supervisor_id}  # <--- Aquí pasamos el parámetro
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
            cur.execute(
                """
                SELECT 
                    r.request_id, 
                    r.supervisor_id,
                    r.employee_id,
                    r.department_id,
                    r.warning_id,
                    r.reason_id,
                    r.notes,
                    r.status_id,
                    r.requestdate,
                    r.user_id,
                    r.updatedate,
                    s.firstname || ' ' || s.lastname AS supervisor_name, -- Nombre completo del supervisor
                    e.firstname || ' ' || e.lastname AS employee_name,    -- Nombre completo del empleado
                    d.department AS department,
                    w.warning AS warning,
                    rs.reason AS reason,
                    st.status AS status,
                    u.firstname || ' ' || u.lastname AS assigned_employee_name -- Nombre completo del usuario asignado
                FROM requests r
                LEFT JOIN employees e ON r.employee_id = e.employee_id       -- Obtener empleado
                LEFT JOIN employees s ON r.supervisor_id = s.employee_id     -- Obtener supervisor
                LEFT JOIN departments d ON r.department_id = d.department_id
                LEFT JOIN warnings w ON r.warning_id = w.warning_id
                LEFT JOIN status st ON r.status_id = st.status_id
                LEFT JOIN reasons rs ON r.reason_id = rs.reason_id
                LEFT JOIN users us ON r.user_id = us.user_id                 -- Obtener el usuario asignado
                LEFT JOIN employees u ON us.employee_id = u.employee_id      -- Obtener el nombre completo del encargado de la solicitud
                WHERE r.request_id = ?;
                """, (request_id,)
            )
            data = cur.fetchone()
            if data:
                return {
                    "request_id": data[0],
                    "supervisor_id": data[1],
                    "employee_id": data[2],
                    "department_id": data[3],
                    "warning_id": data[4],
                    "reason_id": data[5],
                    "notes": data[6],
                    "status_id": data[7],
                    "requestdate": data[8],
                    "user_id": data[9],
                    "updatedate": data[10],
                    "supervisor_name": data[11],
                    "employee_name": data[12],
                    "department": data[13],
                    "warning": data[14],
                    "reason": data[15],
                    "status": data[16],
                    "assigned_employee_name": data[17]
                }
            return None
        except sqlite3.Error as e:
            print(f"Error al obtener la solicitud: {e}")
            raise
        finally:
            conn.close()


    def update_request(self, request_id: int, supervisor_id: int, employee_id: int, department_id: int,
                   warning_id: int, reason_id: int, notes: str, status_id: int, requestdate: str):
        conn = sqlite3.connect("./ocsrequest.db")
        cursor = conn.cursor()
        try:
            # Agregar impresión para depuración
            print(f"Updating request with ID {request_id}")
            print(f"Received status_id: {status_id}")

            # Actualizar los datos de la solicitud
            cursor.execute("""
                UPDATE requests
                SET supervisor_id = ?, employee_id = ?, department_id = ?, warning_id = ?, reason_id = ?,
                    notes = ?, status_id = ?, requestdate = ?
                WHERE request_id = ?
            """, (supervisor_id, employee_id, department_id, warning_id, reason_id, notes, status_id, requestdate, request_id))

            conn.commit()

        except sqlite3.Error as e:
            raise Exception(f"Error al actualizar la solicitud: {e}")
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
        conn = sqlite3.connect("./ocsrequest.db")
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
            
    def get_all_employee_status(self):
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT status_id, status FROM employee_status")
                employee_status = [{"status_id": row[0], "status": row[1]} for row in cur.fetchall()]
                return employee_status
        except sqlite3.Error as e:
            print(f"Error al obtener todos los status: {e}")

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
#--------------------Prueba de barras de colores--------------------------------------
    def get_request_status_counts(self):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT status_id, COUNT(*) 
                FROM requests 
                GROUP BY status_id;
            """)
            data = cur.fetchall()
            return {status_id: count for status_id, count in data}
        except sqlite3.Error as e:
            print(f"Error al obtener los estados de las solicitudes: {e}")
            raise
        finally:
            conn.close()

    def calculate_status_percentages(self):
        status_counts = self.get_request_status_counts()
        total_requests = sum(status_counts.values())  # Total de todas las solicitudes

        if total_requests == 0:
            return {
                "open_percentage": 0,
                "in_progress_percentage": 0,
                "closed_percentage": 0,
            }

        # Suponiendo que el status_id de Open es 1, In Progress es 2, y Closed es 3
        open_percentage = (status_counts.get(1, 0) / total_requests) * 100
        in_progress_percentage = (status_counts.get(2, 0) / total_requests) * 100
        closed_percentage = (status_counts.get(3, 0) / total_requests) * 100

        return {
            "open_percentage": open_percentage,
            "in_progress_percentage": in_progress_percentage,
            "closed_percentage": closed_percentage,
        }
#--------------------Prueba de conteo de empleados y modalidad--------------------------------------
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
