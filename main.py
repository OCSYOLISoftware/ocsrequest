from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from controller.user import User
from lib.check_passw import check_user
from model.handle_db import HandleDB

app = FastAPI()
template = Jinja2Templates(directory='./view')
db = HandleDB()

#Root
@app.get('/', response_class=HTMLResponse)
def root(req: Request):
    return template.TemplateResponse('index.html', {'request': req})

#Signup
@app.get('/signup', response_class=HTMLResponse)
def signup(req: Request):
    return template.TemplateResponse('signup.html', {'request': req})

#dashboard
@app.post('/dashboard', response_class=HTMLResponse)
def login_user(req: Request, username: str = Form(), password_user: str = Form()):
    verify = check_user(username, password_user)
    if verify:
        users = db.get_all()
        return template.TemplateResponse('dashboard.html', {'request': req, "data_user": verify, 'users': users})
    return RedirectResponse('/', status_code=303) 

@app.get('/dashboard', response_class=HTMLResponse)
def get_user(req: Request):
    if not req.cookies.get('user_logged_in'):
        return RedirectResponse('/')
    users = db.get_all()
    return template.TemplateResponse('/dashboard.html', {'request': req, 'users': users})

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