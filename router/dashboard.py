from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from lib.check_passw import check_user
from model.handle_db import HandleDB
from model.employees_db import EmployeesDB
from model.request_db import RequestDB

router = APIRouter()
template = Jinja2Templates(directory=('./view'))
db = HandleDB()
edb = EmployeesDB()
rdb = RequestDB()

#Dependencia para verificar autenticación    IMPORTAR ESTA FUNCION DONDE HAGA FALTA
def get_current_user(req: Request):
    username = req.cookies.get("username") #Obtener el nombre del usuario de la cookie
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No has iniciado sesión"
        )
    return username

# ------------------Dashboard-----------------------------------------------------------------------------------------------------------------------------------------------------
#dashboard maneja el inicio de sesión y guarda el nombre de usuario en una cookie.
@router.post('/dashboard', response_class=HTMLResponse)
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
@router.get('/dashboard', response_class=HTMLResponse)
def get_dashboard(req: Request):
    # Verificar si el usuario ha iniciado sesión
    username = req.cookies.get('username')
    if not username:
        return RedirectResponse(url='/', status_code=303)

    percentages = rdb.calculate_status_percentages()#test
    employee_counts = edb.get_employee_counts()
    
    # Pasar los requests a la plantilla
    return template.TemplateResponse(
        'dashboard.html',
        {
            'request': req, 
            "username": username,
            "open_percentage": percentages["open_percentage"], #test
            "in_progress_percentage": percentages["in_progress_percentage"],#test
            "closed_percentage": percentages["closed_percentage"],#test
            "employee_counts": employee_counts
        }
    )
    
#logout elimina la cookie username y redirige al usuario a la página de inicio.
@router.get('/logout')
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="username")  # Eliminar la cookie de sesión
    return response
    
