from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uvicorn

from triage_engine import process_chat

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Support Triage API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware to disable caching for static files in development
@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    result = process_chat(request.message, session_id=request.session_id)
    return result

# Serve static files (Frontend)
backend_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(os.path.dirname(backend_dir), "frontend")

if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    icon_path = os.path.join(static_path, "favicon.ico")
    if os.path.exists(icon_path):
        return FileResponse(icon_path)
    return Response(status_code=204)

@app.get("/")
async def root():
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "API is running. Please create static/index.html"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}...")
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
