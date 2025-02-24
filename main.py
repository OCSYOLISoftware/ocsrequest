from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
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
def get_dashboard(req: Request):
    # Verificar si el usuario ha iniciado sesión
    if not req.cookies.get('username'):
        return RedirectResponse(url='/', status_code=303)

    # Obtener todos los requests desde la base de datos
    db = HandleDB()
    requests = db.get_all_requests()

    # Pasar los requests a la plantilla
    return template.TemplateResponse(
        'dashboard.html',
        {'request': req, 'requests': requests}
    )
    
#Request muestra el formulario de solicitud solo si el usuario ha iniciado sesión.
"""@app.get("/request", response_class=HTMLResponse)
def create_request(req: Request, username: str = Depends(get_current_user)):
    users = db.get_all()
    return template.TemplateResponse("request.html", {"request": req, "users": users, "username": username}) """
    
@app.get('/request', response_class=HTMLResponse)
def show_request_form(req: Request, username: str = Depends(get_current_user)):
    # Obtener el employee_id del usuario que inició sesión
    db = HandleDB()
    user_data = db.get_only(username)
    if not user_data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    employee_id = user_data[1]  # Suponiendo que employee_id es la cuarta columna

    # Obtener los empleados del mismo departamento
    employees = db.get_employees_by_department(employee_id)
    
    # Obtener los datos de las tablas relacionadas
    users = db.get_all()
    departments = db.get_all_departments()
    warnings = db.get_all_warnings()
    status = db.get_all_status()
    reasons = db.get_all_reasons()
    
    #Pasar los datos a la platilla
    return template.TemplateResponse('request.html', {'request': req, 'users': users, 'employees': employees, 'departments': departments, 'warnings': warnings, 'status': status, 'reasons': reasons })

#Request procesa los datos del formulario y los guarda en la base de datos
# Ruta para procesar el formulario de solicitud
@app.post("/request", response_class=HTMLResponse)
def submit_request(
    req: Request,
    supervisor_id: int = Form(...),  # ID del supervisor
    employee_id: int = Form(...),    # ID del empleado
    department_id: int = Form(...),  # ID del departamento
    warning_id: int = Form(...),     # ID de la advertencia
    reason_id: int = Form(...),     # ID de la razón
    notes: str = Form(...),         # Notas adicionales
    requestdate: str = Form(...),   # Fecha de la solicitud (formato 'YYYY-MM-DD')
    username: str = Depends(get_current_user),  # Verifica que el usuario haya iniciado sesión
):
    try:
        # Insertar los datos en la tabla requests
        db.insert_request(
            supervisor_id=supervisor_id,
            employee_id=employee_id,
            department_id=department_id,
            warning_id=warning_id,
            reason_id=reason_id,
            notes=notes,
            user_id=1,  # Reemplaza con el ID del usuario autenticado
            requestdate=requestdate,
        )
        return template.TemplateResponse(
            "request.html",
            {"request": req, "message": "Solicitud enviada exitosamente", "username": username}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar la solicitud: {e}",
        )
        
        
        
#logout elimina la cookie username y redirige al usuario a la página de inicio.
@app.get('/logout')
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="username")  # Eliminar la cookie de sesión
    return response