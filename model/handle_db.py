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
        
    def __del__(self):
        #Cerrar ;a conexion al final 
        pass