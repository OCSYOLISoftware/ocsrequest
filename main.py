from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from controller.user import User
from lib.check_passw import check_user
from model.handle_db import HandleDB

app = FastAPI()
template = Jinja2Templates(directory='./view')
db = HandleDB()

#Dependencia para verificar autenticación
def get_current_user(req: Request):
    username = req.cookies.get("username") #Obtener el nombre del usuario de la cookie
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No has iniciado sesión"
        )
    return username
    
#Root
@app.get('/', response_class=HTMLResponse)
def root(req: Request):
    return template.TemplateResponse('index.html', {'request': req})

#Signup
@app.get('/signup', response_class=HTMLResponse)
def signup(req: Request):
    return template.TemplateResponse('signup.html', {'request': req})

#Ruta Data-Processing
@app.post('/data-processing', response_class=HTMLResponse)
def data_processing(employee_id: str = Form(), username: str = Form(), password_user: str = Form()):
    data_user = {
        'employee_id': employee_id,
        'username': username,
        'password_user': password_user
    }
    db = User(data_user)
    db.create_user()
    return RedirectResponse('/', status_code=303)

#dashboard maneja el inicio de sesión y guarda el nombre de usuario en una cookie.
@app.post('/dashboard', response_class=HTMLResponse)
def login_user(req: Request, username: str = Form(), password_user: str = Form()):
    verify = check_user(username, password_user)
    if verify:
        print(f"Inicio de sesión exitoso para el usuario: {username}")
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="username", value=username) #Guarda el nombre de usuario en una cookie
        return response
    else:
        print(f"Error en la autenticación para el usuario: {username}")
        return RedirectResponse('/', status_code=303) 
    
#Dashboard muestra el dashboard solo si el usuario ha iniciado sesión.
@app.get('/dashboard', response_class=HTMLResponse)
def get_user(req: Request, username: str = Depends(get_current_user)):
    users = db.get_all()
    return template.TemplateResponse('dashboard.html', {"request": req, "users": users, 'username': username })
    
#Request muestra el formulario de solicitud solo si el usuario ha iniciado sesión.
@app.get("/request", response_class=HTMLResponse)
def create_request(req: Request, username: str = Depends(get_current_user)):
    users = db.get_all()
    return template.TemplateResponse("request.html", {"request": req, "users": users, "username": username})

#Request procesa los datos del formulario y los guarda en la base de datos
@app.post("/request", response_class=HTMLResponse)
def submit_request(req: Request, username: str = Depends(get_current_user)):
    try:
        #Aqui procesa los datos del formulario y los guarda en la base de datos
        db.insert_request() #Crear funciones para incertar en request dentro de Model
        return template.TemplateResponse("request.html", {"request": req, "message": "Solicitud enviada exitosamente", "username": username})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar solicitud: {e}",
        )
#logout elimina la cookie username y redirige al usuario a la página de inicio.
@app.get('/logout')
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="username")  # Eliminar la cookie de sesión
    return response