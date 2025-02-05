from model.handle_db import HandleDB
from werkzeug.security import generate_password_hash

class User():
    data_user = {}
    
    def __init__(self, data_user):
        self.db = HandleDB()
        self.data_user = data_user
        
    def create_user(self):
        #encriptar password
        self._passw_encrypt()
        #crear usuario
        self.db.insert(self.data_user)
        
    def _passw_encrypt(self):
        self.data_user['password_user'] = generate_password_hash(self.data_user['password_user'], 'pbkdf2:sha256:30', 30)