from fastapi import FastAPI
from router.dashboard import router as dashboard_router
from router.index import router as index_router
from router.signup import router as signup_router
from router.request import router as request_router
from router.employee import router as employee_router

app = FastAPI()

app.include_router(dashboard_router)
app.include_router(index_router)
app.include_router(signup_router)
app.include_router(request_router)
app.include_router(employee_router)
