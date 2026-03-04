from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.routers import users
from app.errors import AppError
from app.database import create_pool, close_pool, get_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create connection pool
    print("Starting up: Creating connection pool...")
    create_pool()
    yield
    # Shutdown: Close connection pool
    print("Shutting down: Closing connection pool...")
    close_pool()

app = FastAPI(
    title="Training API",
    version="1.0.0",
    description="API interkoneksi data",
    lifespan=lifespan
)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
            },
            "meta": {
                "path": str(request.url.path),
                "request_id": request.headers.get("X-Request-ID", "")
            },
        },
    )
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    detail = []
    for err in exc.errors():
        loc = ",".join([str(x) for x in err.get("loc", []) if x != "body"])
        detail.append({
            "field": loc,
            "issue": err.get("msg", "Validation failed")
        })
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input tidak valid",
                "detail": detail,
            },
            "meta": {"path": str(request.url.path)},
        },
    )

app.include_router(
    users.router,
    prefix="/v1",
    tags=["users"]
)

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/health/db")
def db_health_check(conn = Depends(get_db)):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        cursor.close()
        return {"status": "healthy", "database": "connected", "result": result[0]}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}