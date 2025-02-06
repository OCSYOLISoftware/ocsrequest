from model.handle_db import HandleDB
from werkzeug.security import check_password_hash

def check_user(username, passw):
    user = HandleDB()
    filter_user = user.get_only(username)
    if filter_user:
        same_passw = check_password_hash(filter_user[3], passw)
        if same_passw:
            return filter_user
        return None
    
    
    ''' Codigo prueba Deepseek
def check_user(username, passw):
    user = HandleDB()
    filter_user = user.get_only(username)
    
    if filter_user:
        print(f"Datos del usuario obtenidos: {filter_user}")  # Depuración
        same_passw = check_password_hash(filter_user[3], passw)
        if same_passw:
            return filter_user
        else:
            print("La contraseña no coincide")  # Depuración
            return None
    else:
        print(f"Usuario '{username}' no encontrado")  # Depuración
        return None
        '''