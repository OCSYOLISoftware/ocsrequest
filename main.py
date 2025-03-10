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

#-------------------------Signup---------------------------------------------------------------------------------------------------------------------------------------------------
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
# ------------------Dashboard-----------------------------------------------------------------------------------------------------------------------------------------------------
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
    username = req.cookies.get('username')
    if not username:
        return RedirectResponse(url='/', status_code=303)

    percentages = db.calculate_status_percentages()#test
    
    # Pasar los requests a la plantilla
    return template.TemplateResponse(
        'dashboard.html',
        {
            'request': req, 
            "username": username,
            "open_percentage": percentages["open_percentage"], #test
            "in_progress_percentage": percentages["in_progress_percentage"],#test
            "closed_percentage": percentages["closed_percentage"],#test
        }
    )
    
#logout elimina la cookie username y redirige al usuario a la página de inicio.
@app.get('/logout')
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="username")  # Eliminar la cookie de sesión
    return response
    

#-------------------Request-----------------------------------------------------------------------------------------------------------------------------------------------------------------------   
@app.get('/request', response_class=HTMLResponse)
def show_request_form(req: Request, username: str = Depends(get_current_user)):
    # Obtener el employee_id del usuario que inició sesión
    db = HandleDB()
    user_data = db.get_only(username)
    if not user_data:
        return HTTPException(status_code=404, detail="Usuario no encontrado")

    employee_id = user_data[1] 

    # Joins
    employees = db.get_employees_by_department(employee_id)
    get_departments_by_employee = db.get_departments_by_employee(employee_id)
    supervisor = db.get_supervisor_for_current_user(username)
    # Obtener los datos de las tablas relacionadas
    requests = db.get_all_requests()
    users = db.get_all()
    warnings = db.get_all_warnings()
    status = db.get_all_status()
    reasons = db.get_all_reasons()
    
    #Pasar los datos a la platilla
    return template.TemplateResponse(
        'request.html', 
        {
            'request': req, 
            'users': users, 
            'employees': employees, 
            'get_departments_by_employee': get_departments_by_employee,
            'supervisor_id': supervisor["employee_id"], 
            'supervisor_name': supervisor["name"], 
            'warnings': warnings, 
            'status': status, 
            'reasons': reasons,
            "username": username,
            "requests": requests 
        }
    )

#Request procesa los datos del formulario y los guarda en la base de datos
# Ruta para procesar el formulario de solicitud
@app.post("/request", response_class=HTMLResponse)
def submit_request(
    req: Request,
    supervisor_id: int = Form(...),  # ID del supervisor
    employee_id: int = Form(...),    # ID del empleado
    department_id: int = Form(...),  # ID del departamento
    warning_id: int = Form(...),     # ID de la advertencia
    reason_id: int = Form(...),      # ID de la razón
    notes: str = Form(...),          # Notas adicionales
    requestdate: str = Form(...),    # Fecha de la solicitud (formato 'YYYY-MM-DD')
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
            user_id=None,  # Asigna None para dejarlo en blanco en la base de datos
            requestdate=requestdate,
        )
        return RedirectResponse(url='/request', status_code=303)
         
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar la solicitud: {e}",
        )

@app.get("/editRequest/{request_id}", response_class=HTMLResponse)
def edit_request(req: Request, request_id: int, username: str = Depends(get_current_user)):
    db = HandleDB()  # Asegúrate de que HandleDB esté inicializado correctamente
    request_data = db.get_request_by_id(request_id)
    user_data = db.get_only(username)
    if not user_data:
        return HTTPException(status_code=404, detail="Usuario no encontrado")

    employee_id = user_data[1] 

    # Obtener el 'department_id' de la solicitud
    department_id = request_data.get("department_id") 

    # Usar el 'department_id' para obtener los empleados de ese departamento
    employees = db.get_employees_by_department(department_id) 

    # Obtener otras consultas relacionadas
    get_departments_by_employee = db.get_departments_by_employee(employee_id)
    supervisor = db.get_supervisor_for_current_user(username)
    requests = db.get_all_requests()
    users = db.get_all()
    warnings = db.get_all_warnings()
    status = db.get_all_status()
    reasons = db.get_all_reasons()

    if not request_data:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    # Pasar los datos a la plantilla
    return template.TemplateResponse(
        'editRequest.html',
        {
            'request': req,
            'request_data': request_data,
            'username': username,
            'users': users, 
            'employees': employees,  # Ahora pasas los empleados filtrados por departamento
            'get_departments_by_employee': get_departments_by_employee,
            'supervisor_id': supervisor["employee_id"] if supervisor else None,
            'supervisor_name': supervisor["name"] if supervisor else None,
            'warnings': warnings, 
            'status': status, 
            'reasons': reasons
        }
    )
    
@app.post("/updateRequest/{request_id}", response_class=HTMLResponse)
def update_request(
        req: Request,
        request_id: int,
        supervisor_id: int = Form(...),
        employee_id: int = Form(...),
        department_id: int = Form(...),
        warning_id: int = Form(...),
        reason_id: int = Form(...),
        notes: str = Form(...),
        status_id: int = Form(...),
        requestdate: str = Form(...)
):
    try:
        # Actualizar los datos de la solicitud en la base de datos
        db.update_request(
            request_id=request_id,
            supervisor_id=supervisor_id,
            employee_id=employee_id,
            department_id=department_id,
            warning_id=warning_id,
            reason_id=reason_id,
            notes=notes,
            status_id=status_id,
            requestdate=requestdate
        )
        # Redirigir a la página de solicitudes después de la actualización
        return RedirectResponse(url="/requests", status_code=303)
    
    except Exception as e:
        # Manejo de errores: muestra el error en caso de falla
        return HTMLResponse(content=f"Error al actualizar la solicitud: {e}", status_code=500)


#-----------------------------Employee -----------------------------------------------------------------------------------------------------------------------------------------------
@app.get("/addEmployee", response_class=HTMLResponse)
def show_employee_form(req: Request):
    # Verificar si el usuario ha iniciado sesión
    username = req.cookies.get('username')
    if not username:
        return RedirectResponse(url='/', status_code=303)
    
    # Obtener todos los empleados desde la base de datos
    employees = db.get_all_employees()
    departments = db.get_all_departments()
    positions = db.get_all_positions()
    branches = db.get_all_branches()
    modalities = db.get_all_modalities()
    employee_status = db.get_all_employee_status()
    
    return template.TemplateResponse(
        "addEmployee.html",
        {
            'request': req,
            'employees': employees,
            'departments': departments,
            'positions': positions,
            'branches': branches,
            'modalities': modalities,
            "username": username,
            "employee_status": employee_status
        }
    )

@app.post('/addEmployee', response_class=RedirectResponse)
def add_employee(
        req: Request,
        employee_id: int = Form(...),  # ID del empleado
        firstname: str = Form(...),    # Nombre del empleado
        lastname: str = Form(...),     # Apellido del empleado
        position_id: int = Form(...),  # ID de la posición
        branch_id: int = Form(...),    # ID del branch
        modality_id: int = Form(...),  # ID de modalidad
        hiredate: str = Form(...),     # Fecha de contratación (formato 'YYYY-MM-DD')
        department_id: int = Form(...),  # ID del departamento 
        status_id: int = Form(...)  # ID del departamento 
):
    try:
        # Insertar los datos en la tabla employees
        db.insert_employee(
            employee_id=employee_id,
            firstname=firstname,
            lastname=lastname,
            position_id=position_id,
            branch_id=branch_id,
            modality_id=modality_id,
            hiredate=hiredate,
            status_id=status_id
        )

        # Insertar los datos en la tabla employee_departments
        db.insert_employee_department(
            employee_id=employee_id,
            department_id=department_id
        )

        # 🔹 Redirigir a la misma página para refrescar la lista de empleados
        return RedirectResponse(url='/addEmployee', status_code=303)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar la solicitud: {e}",
        )
 #------------------------------------------------------------------------------------------------------------------------------------       

@app.get("/editEmployee/{employee_id}", response_class=HTMLResponse)
def edit_employee(req: Request, employee_id: int):
    # Verificar si el usuario ha iniciado sesión
    username = req.cookies.get('username')
    if not username:
        return RedirectResponse(url='/', status_code=303)

    # Obtener datos del empleado
    
    employee = db.get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # Obtener todas las listas necesarias
    employees = db.get_all_employees()
    departments = db.get_all_departments()
    positions = db.get_all_positions()
    branches = db.get_all_branches()
    modalities = db.get_all_modalities()
    employee_status = db.get_all_employee_status()

    return template.TemplateResponse(
        "editEmployee.html",
        {
            "request": req,
            "employee": employee,
            "employees": employees,
            "departments": departments,
            "positions": positions,
            "branches": branches,
            "modalities": modalities,
            "username": username,
            "employee_status": employee_status
        }
    )
    
@app.post("/updateEmployee/{employee_id}", response_class=HTMLResponse)
def update_employee(
        req: Request,
        employee_id: int,
        firstname: str = Form(...),
        lastname: str = Form(...),
        position_id: int = Form(...),
        branch_id: int = Form(...),
        modality_id: int = Form(...),
        hiredate: str = Form(...),
        department_id: int = Form(...),
        status_id: int = Form(...)
):
    try:
        # Actualizar los datos del empleado en la base de datos
        db.update_employee(
            employee_id=employee_id,
            firstname=firstname,
            lastname=lastname,
            position_id=position_id,
            branch_id=branch_id,
            modality_id=modality_id,
            hiredate=hiredate,
            department_id=department_id,
            status_id=status_id
        )

        # Actualizar el departamento del empleado
        db.update_employee_department(
            employee_id=employee_id,
            department_id=department_id
        )

        return RedirectResponse(url="/addEmployee", status_code=303)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el empleado: {e}")
#----------------------------------------------------------------------------------------------------------
