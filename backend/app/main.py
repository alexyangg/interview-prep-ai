from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router

# from app.db.session import engine
# from app.db.base import Base

# # create database tables
# @app.on_event("startup")
# def on_startup():
#     Base.metadata.create_all(bind=engine)
#     print("Database tables created")

app = FastAPI(title="Interview Prep AI Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status" : "ok"}

app.include_router(api_router, prefix="/api/v1")
