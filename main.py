import uvicorn
from fastapi import FastAPI

from api.v1.student import student_router
from api.v1.auth import auth_router

app = FastAPI()
app.include_router(student_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

@app.get("/")
async def root():
  return {
    "message": "Hello world!"
  }

if __name__ == "__main__":
  uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8000,
    reload=True
  )
