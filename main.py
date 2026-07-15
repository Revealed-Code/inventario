from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
# ... (deja aquí tus otros imports como de supabase, os, etc.)

app = FastAPI()

# Configuramos CORS por seguridad (esto permite que se conecte sin bloqueos)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. ESTA RUTA DEBE SERVIR TU FRONTEND
@app.get("/")
def read_root():
    return FileResponse("index.html")

# ... (abajo de esto, conserva todas tus rutas de la API, como @app.post, @app.get, etc.)
