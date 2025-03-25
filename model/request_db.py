import sqlite3
from model.handle_db import HandleDB

class RequestDB(HandleDB):
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