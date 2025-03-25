import sqlite3

#-----------------------------Data base connection------------------------------------------------------------------------------
class HandleDB():
    def __init__(self, db_path="./ocsrequest.db"):
        self.db_path = db_path
        
    def _connect(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

#----------------Todas las consultas a las tablas complementarias--------------------------------------------------------------------------------------------            
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
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT status_id, status FROM status")
                status = [{"status_id": row[0], "reason": row[1]} for row in cur.fetchall()]
                return status
        except sqlite3.Error as e:
            print(f"Error al obtener todos los status: {e}")
            raise

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

