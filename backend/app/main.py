from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación FastAPI
app = FastAPI(
    title="Presente+ API",
    description="API para gestión de participantes, asistencia y alertas",
    version="1.0.0"
)

# ============================================
# CORS (Comunicación entre backend y frontend)
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # URLs del frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los headers
)

# ============================================
# CREAR TABLAS EN LA BASE DE DATOS
# ============================================
Base.metadata.create_all(bind=engine)

# ============================================
# ENDPOINT DE PRUEBA
# ============================================

@app.get("/", tags=["Health Check"])
def root():
    """Endpoint de prueba para verificar que el servidor está funcionando"""
    return {
        "mensaje": "¡Bienvenido a Presente+ API!",
        "version": "1.0.0",
        "docs": "/docs"  # Ir aquí para ver la documentación interactiva
    }

@app.get("/health", tags=["Health Check"])
def health_check():
    """Verifica que el servidor está corriendo correctamente"""
    return {"status": "OK", "mensaje": "Servidor funcionando correctamente"}

# ============================================
# ENDPOINTS PARA USUARIOS (PRÓXIMAMENTE)
# ============================================

# @app.post("/auth/login")
# def login(credenciales: LoginSchema):
#     pass

# @app.post("/auth/register")
# def register(usuario: UsuarioCreate):
#     pass

# ============================================
# ENDPOINTS PARA PARTICIPANTES (PRÓXIMAMENTE)
# ============================================

# @app.get("/participantes")
# def listar_participantes():
#     pass

# @app.post("/participantes")
# def crear_participante(participante: ParticipanteCreate):
#     pass

# ============================================
# ENDPOINTS PARA GRUPOS (PRÓXIMAMENTE)
# ============================================

# @app.get("/grupos")
# def listar_grupos():
#     pass

# @app.post("/grupos")
# def crear_grupo(grupo: GrupoCreate):
#     pass

# ============================================
# ENDPOINTS PARA ASISTENCIA (PRÓXIMAMENTE)
# ============================================

# @app.post("/asistencias")
# def registrar_asistencia(asistencia: AsistenciaCreate):
#     pass

# ============================================
# ENDPOINTS PARA ALERTAS (PRÓXIMAMENTE)
# ============================================

# @app.get("/alertas")
# def listar_alertas():
#     pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)