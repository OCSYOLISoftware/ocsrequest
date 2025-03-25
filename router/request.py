from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from model.handle_db import HandleDB
from model.user_db import UserDB
from model.request_db import RequestDB
from model.warnings_db import WarningDB
from model.supervisors_db import SupervisorDB
from model.employees_db import EmployeesDB
from model.department_db import DepartmentDB
from router.dashboard import get_current_user

router = APIRouter()
template = Jinja2Templates(directory=('./view'))
db = HandleDB()
udb = UserDB()
rdb = RequestDB()
wdb = WarningDB()
sdb = SupervisorDB()
edb = EmployeesDB()
ddb = DepartmentDB()

@router.get('/request', response_class=HTMLResponse)
def show_request_form(req: Request, username: str = Depends(get_current_user)):
    # Obtener el employee_id del usuario que inició sesión
    user_data = udb.get_only(username)
    if not user_data:
        return HTTPException(status_code=404, detail="Usuario no encontrado")

    employee_id = user_data[1] 
    
    #Obtener supervisor
    supervisor = sdb.get_supervisor_for_current_user(username)
    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor ni encontrado")
    
    #aqui se define el supervisor
    supervisor_id = supervisor["employee_id"]

    # Joins
    employees = edb.get_employees_by_department(employee_id)
    get_departments_by_employee = ddb.get_departments_by_employee(employee_id)
    supervisor = sdb.get_supervisor_for_current_user(username)
    # Obtener los datos de las tablas relacionadas
    requests = rdb.get_all_requests(supervisor_id)
    users = udb.get_all()
    warnings = wdb.get_all_warnings()
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

@router.post("/request", response_class=HTMLResponse)
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
        rdb.insert_request(
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

@router.get("/editRequest/{request_id}", response_class=HTMLResponse)
def edit_request(req: Request, request_id: int, username: str = Depends(get_current_user)):
    request_data = rdb.get_request_by_id(request_id)
    user_data = udb.get_only(username)
    if not user_data:
        return HTTPException(status_code=404, detail="Usuario no encontrado")

    employee_id = user_data[1] 
    supervisor = sdb.get_supervisor_for_current_user(username)
    supervisor_id = supervisor["employee_id"]

    # Obtener el 'department_id' de la solicitud
    department_id = request_data.get("department_id") 

    # Usar el 'department_id' para obtener los empleados de ese departamento
    employees = edb.get_employees_by_department(department_id) 

    # Obtener otras consultas relacionadas
    get_departments_by_employee = ddb.get_departments_by_employee(employee_id)
    supervisor = sdb.get_supervisor_for_current_user(username)
    requests = rdb.get_all_requests(supervisor_id)
    users = udb.get_all()
    warnings = wdb.get_all_warnings()
    status = db.get_all_status()
    reasons = db.get_all_reasons()

    if not request_data:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    # Pasar los datos a la plantilla
    return template.TemplateResponse(
        'editRequest.html',
        {
            'request': req,
            'requests': requests,
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
    
@router.post("/updateRequest/{request_id}", response_class=HTMLResponse)
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
        rdb.update_request(
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