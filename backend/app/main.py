from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import traceback

from app.routers import dashboard, personal, stats, alertas, exportar, sincronizar, auth

app = FastAPI(title="BIMEJ12 - Sistema de Reportes de Personal", version="1.0.0")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "BIMEH API Online", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    method = request.method
    path = request.url.path
    print(f"--> [REQ] {method} {path}")
    try:
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds() * 1000
        print(f"<-- [RES] {method} {path} status={response.status_code} ({process_time:.2f}ms)")
        return response
    except Exception as e:
        process_time = (datetime.now() - start_time).total_seconds() * 1000
        print(f"❌ [ERR] {method} {path} ({process_time:.2f}ms): {e}")
        traceback.print_exc()
        raise e

# Include Routers
app.include_router(dashboard.router)
app.include_router(personal.router)
app.include_router(stats.router)
app.include_router(alertas.router)
app.include_router(exportar.router)
app.include_router(sincronizar.router)
app.include_router(auth.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=3000, reload=True)
