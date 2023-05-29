from fastapi import FastAPI

from routers import data_routes, auth_routes

app = FastAPI()
app.include_router(data_routes.router)
app.include_router(auth_routes.router)
