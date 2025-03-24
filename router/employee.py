from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from model.handle_db import HandleDB

router = APIRouter()
template = Jinja2Templates(directory=('./view'))
db = HandleDB()

@router.get("/addEmployee", response_class=HTMLResponse)
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

@router.post('/addEmployee', response_class=RedirectResponse)
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

@router.get("/editEmployee/{employee_id}", response_class=HTMLResponse)
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
    
@router.post("/updateEmployee/{employee_id}", response_class=HTMLResponse)
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