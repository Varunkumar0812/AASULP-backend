from fastapi import FastAPI
from app.routes import example
from app.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}


# Include routes
app.include_router(example.router, prefix="/example", tags=["Example"])

