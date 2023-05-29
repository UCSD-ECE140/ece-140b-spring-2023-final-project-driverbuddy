from fastapi import FastAPI
import uvicorn
from routers import data_routes, auth_routes


app = FastAPI()
app.include_router(data_routes.router)
app.include_router(auth_routes.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
