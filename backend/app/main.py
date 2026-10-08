from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import app.models
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ============================================
# CREAR LA APLICACIÓN FASTAPI
# ============================================

app = FastAPI(
    title="Presente+ API",
    description="API para gestión de participantes, asistencia y alertas",
    version="1.0.0"
)

# ============================================
# CONFIGURAR CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# CREAR TABLAS EN LA BASE DE DATOS
# ============================================

Base.metadata.create_all(bind=engine)

# ============================================
# CREAR ROLES POR DEFECTO (SI NO EXISTEN)
# ============================================

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Rol

def crear_roles_por_defecto():
    """Crea los roles por defecto si no existen"""
    db = SessionLocal()
    try:
        # Verificar si ya existen
        roles_existentes = db.query(Rol).all()
        if len(roles_existentes) > 0:
            print("✅ Roles ya creados")
            return
        
        # Crear roles
        roles = [
            Rol(nombre="Coordinador", descripcion="Administrador del sistema"),
            Rol(nombre="Educador", descripcion="Educador/Docente"),
            Rol(nombre="Participante", descripcion="Participante/Estudiante")
        ]
        
        for rol in roles:
            db.add(rol)
        
        db.commit()
        print("✅ Roles creados exitosamente")
    
    except Exception as e:
        print(f"ℹ️ Roles ya existen o error: {e}")
    
    finally:
        db.close()

# Crear roles al iniciar
crear_roles_por_defecto()

# ============================================
# IMPORTAR ROUTERS (ENDPOINTS)
# ============================================

from app.routes import usuarios_router, participantes_router, grupos_router, asistencias_router, alertas_router

# ============================================
# REGISTRAR ROUTERS
# ============================================

app.include_router(usuarios_router.router)
app.include_router(participantes_router.router)
app.include_router(grupos_router.router)
app.include_router(asistencias_router.router)
app.include_router(alertas_router.router)

# ============================================
# ENDPOINTS DE PRUEBA
# ============================================

@app.get("/", tags=["Health Check"])
def root():
    """Endpoint raíz - Verificar que la API está funcionando"""
    return {
        "mensaje": "¡Bienvenido a Presente+ API!",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs",
        "redoc": "http://localhost:8000/redoc",
        "status": "✅ Servidor funcionando correctamente"
    }

@app.get("/health", tags=["Health Check"])
def health_check():
    """Endpoint de verificación de salud"""
    return {
        "status": "OK",
        "mensaje": "Servidor funcionando correctamente",
        "timestamp": __import__('datetime').datetime.utcnow()
    }

@app.get("/info", tags=["Info"])
def obtener_info():
    """Información del sistema"""
    return {
        "nombre": "Presente+ API",
        "version": "1.0.0",
        "endpoints_disponibles": {
            "autenticacion": "/auth/login, /auth/register, /auth/me",
            "participantes": "/participantes",
            "grupos": "/grupos",
            "asistencias": "/asistencias",
            "alertas": "/alertas"
        },
        "documentacion": "Abre /docs en tu navegador para ver Swagger UI"
    }

# ============================================
# INICIALIZAR SERVIDOR
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)