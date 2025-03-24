from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from model.handle_db import HandleDB

router = APIRouter()
template = Jinja2Templates(directory=('./view'))
db = HandleDB()

@router.get('/', response_class=HTMLResponse)
def root(req: Request):
    return template.TemplateResponse('index.html', {'request': req})