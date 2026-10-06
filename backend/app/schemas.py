from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

# ============================================
# SCHEMAS PARA USUARIOS Y AUTENTICACIÓN
# ============================================

class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str
    apellido: str

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6, description="Contraseña de al menos 6 caracteres")

class UsuarioResponse(UsuarioBase):
    id: int
    estado: str
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

# ============================================
# SCHEMAS PARA PARTICIPANTES
# ============================================

class TutorBase(BaseModel):
    nombre: str
    apellido: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    domicilio: Optional[str] = None

class TutorCreate(TutorBase):
    pass

class TutorResponse(TutorBase):
    id: int
    
    class Config:
        from_attributes = True

class ParticipanteBase(BaseModel):
    nombre: str
    apellido: str
    dni: str
    fecha_nacimiento: Optional[datetime] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None

class ParticipanteCreate(ParticipanteBase):
    tutor_id: Optional[int] = None

class ParticipanteResponse(ParticipanteBase):
    id: int
    estado: str
    tutor: Optional[TutorResponse] = None
    
    class Config:
        from_attributes = True

# ============================================
# SCHEMAS PARA GRUPOS
# ============================================

class GrupoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    tipo_actividad: Optional[str] = None
    rango_etario: Optional[str] = None
    dia_semana: Optional[str] = None
    horario: Optional[str] = None
    cupo_maximo: Optional[int] = None

class GrupoCreate(GrupoBase):
    pass

class GrupoResponse(GrupoBase):
    id: int
    estado: str
    
    class Config:
        from_attributes = True

# ============================================
# SCHEMAS PARA ASISTENCIA
# ============================================

class AsistenciaBase(BaseModel):
    participante_id: int
    grupo_id: int
    fecha: datetime
    estado: str  # Presente, Ausente, Tarde, Justificado
    observaciones: Optional[str] = None

class AsistenciaCreate(AsistenciaBase):
    educador_id: Optional[int] = None

class AsistenciaResponse(AsistenciaBase):
    id: int
    
    class Config:
        from_attributes = True

# ============================================
# SCHEMAS PARA ALERTAS
# ============================================

class AlertaBase(BaseModel):
    participante_id: int
    grupo_id: int
    tipo: str  # Atención, Crítica
    descripcion: Optional[str] = None

class AlertaCreate(AlertaBase):
    pass

class AlertaResponse(AlertaBase):
    id: int
    estado: str
    
    class Config:
        from_attributes = True