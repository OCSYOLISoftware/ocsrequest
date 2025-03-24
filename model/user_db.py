import sqlite3
from model.handle_db import HandleDB

class UserDB(HandleDB):
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