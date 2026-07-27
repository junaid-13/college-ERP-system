from fastapi import FastAPI
from routes.project import router as project_router
from routes.generate import router as generate_router

app = FastAPI()
app.include_router(project_router)
app.include_router(generate_router)