from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from controller.user import User
from model.handle_db import HandleDB

router = APIRouter()
template = Jinja2Templates(directory=('./view'))
db = HandleDB()


@router.get('/signup', response_class=HTMLResponse)
def signup(req: Request):
    return template.TemplateResponse('signup.html', {'request': req})

#Ruta Data-Processing
@router.post('/data-processing', response_class=HTMLResponse)
def data_processing(employee_id: str = Form(), username: str = Form(), password_user: str = Form()):
    data_user = {
        'employee_id': employee_id,
        'username': username,
        'password_user': password_user
    }
    db = User(data_user)
    db.create_user()
    return RedirectResponse('/', status_code=303)