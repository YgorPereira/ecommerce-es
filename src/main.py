from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)from fastapi import FastAPI
from fastapi.responses import JSONResponse
from h11 import Request
from src.modules.users.router import user_router
import uvicorn

from src.shared.exceptions import AppException

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)