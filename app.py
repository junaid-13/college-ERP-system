from fastapi import FastAPI
from routes.project import router

app = FastAPI()
app.include_router(router)