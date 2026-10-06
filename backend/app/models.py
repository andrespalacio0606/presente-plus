from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

# ============================================
# ENUMS (tipos de datos con opciones fijas)
# ===========================================

class RolEnum(str, enum.Enum):
    COORDINADOR = "Coordinador"
    EDUCADOR = "Educador"
    PARTICIPANTE = "Participante"

class EstadoUsuarioEnum(str, enum.Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    BLOQUEADO = "Bloqueado"

class EstadoAsistenciaEnum(str, enum.Enum):
    PRESENTE = "Presente"
    AUSENTE = "Ausente"
    TARDE = "Tarde"
    JUSTIFICADO = "Justificado"

class TipoAlertaEnum(str, enum.Enum):
    ATENCION = "Atención"
    CRITICA = "Crítica"

# ============================================
# TABLAS
# ============================================

class Rol(Base):
    """Tabla de roles disponibles"""
    __tablename__ = "ROL"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(255))
    
    # Relación: un rol puede tener muchos usuarios
    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    """Tabla de usuarios del sistema"""
    __tablename__ = "USUARIO"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)  # Contraseña encriptada
    
    rol_id = Column(Integer, ForeignKey("ROL.id"), nullable=False)
    estado = Column(Enum(EstadoUsuarioEnum), default=EstadoUsuarioEnum.ACTIVO)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    rol = relationship("Rol", back_populates="usuarios")


class Tutor(Base):
    """Tabla de tutores de participantes"""
    __tablename__ = "TUTOR"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(120), nullable=True)
    telefono = Column(String(20), nullable=True)
    domicilio = Column(String(255), nullable=True)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relación: un tutor puede cuidar a muchos participantes
    participantes = relationship("Participante", back_populates="tutor")


class Participante(Base):
    """Tabla de participantes en talleres"""
    __tablename__ = "PARTICIPANTE"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    dni = Column(String(20), unique=True, nullable=False, index=True)
    fecha_nacimiento = Column(DateTime, nullable=True)
    domicilio = Column(String(255), nullable=True)
    telefono = Column(String(20), nullable=True)
    
    tutor_id = Column(Integer, ForeignKey("TUTOR.id"), nullable=True)
    estado = Column(String(50), default="Activo")  # Activo, Seguimiento, Inactivo
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    tutor = relationship("Tutor", back_populates="participantes")
    grupos = relationship("Grupo", secondary="PARTICIPANTE_GRUPO", back_populates="participantes")
    asistencias = relationship("Asistencia", back_populates="participante", cascade="all, delete-orphan")
    alertas = relationship("Alerta", back_populates="participante", cascade="all, delete-orphan")


class Grupo(Base):
    """Tabla de grupos/talleres"""
    __tablename__ = "GRUPO"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo_actividad = Column(String(100), nullable=True)
    rango_etario = Column(String(100), nullable=True)
    
    dia_semana = Column(String(20), nullable=True)  # Lunes, Martes, etc
    horario = Column(String(20), nullable=True)  # HH:MM-HH:MM
    cupo_maximo = Column(Integer, nullable=True)
    
    estado = Column(String(50), default="Activo")  # Activo, Pausado, Finalizado
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    participantes = relationship("Participante", secondary="PARTICIPANTE_GRUPO", back_populates="grupos")
    educadores = relationship("Usuario", secondary="EDUCADOR_GRUPO")
    asistencias = relationship("Asistencia", back_populates="grupo", cascade="all, delete-orphan")
    alertas = relationship("Alerta", back_populates="grupo", cascade="all, delete-orphan")
    materiales = relationship("Material", back_populates="grupo", cascade="all, delete-orphan")


class Asistencia(Base):
    """Tabla de registros de asistencia"""
    __tablename__ = "ASISTENCIA"
    
    id = Column(Integer, primary_key=True, index=True)
    participante_id = Column(Integer, ForeignKey("PARTICIPANTE.id"), nullable=False)
    grupo_id = Column(Integer, ForeignKey("GRUPO.id"), nullable=False)
    
    fecha = Column(DateTime, nullable=False)
    estado = Column(Enum(EstadoAsistenciaEnum), nullable=False)  # Presente, Ausente, Tarde, Justificado
    
    educador_id = Column(Integer, ForeignKey("USUARIO.id"), nullable=True)  # Quién registra
    observaciones = Column(Text, nullable=True)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    participante = relationship("Participante", back_populates="asistencias")
    grupo = relationship("Grupo", back_populates="asistencias")


class Alerta(Base):
    """Tabla de alertas por ausentismo"""
    __tablename__ = "ALERTA"
    
    id = Column(Integer, primary_key=True, index=True)
    participante_id = Column(Integer, ForeignKey("PARTICIPANTE.id"), nullable=False)
    grupo_id = Column(Integer, ForeignKey("GRUPO.id"), nullable=False)
    
    tipo = Column(Enum(TipoAlertaEnum), nullable=False)  # Atención, Crítica
    descripcion = Column(Text, nullable=True)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(50), default="Activa")  # Activa, Resuelta
    
    observaciones_resolucion = Column(Text, nullable=True)
    fecha_resolucion = Column(DateTime, nullable=True)
    
    # Relaciones
    participante = relationship("Participante", back_populates="alertas")
    grupo = relationship("Grupo", back_populates="alertas")


class Material(Base):
    """Tabla de materiales educativos"""
    __tablename__ = "MATERIAL"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria = Column(String(100), nullable=True)  # Guía didáctica, Ficha, etc
    
    ruta_archivo = Column(String(500), nullable=False)  # Ruta en servidor
    nombre_archivo = Column(String(255), nullable=False)
    
    grupo_id = Column(Integer, ForeignKey("GRUPO.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    grupo = relationship("Grupo", back_populates="materiales")


# ============================================
# TABLAS INTERMEDIAS (relaciones many-to-many)
# ============================================

from sqlalchemy import Table

# Relación: Un participante puede estar en muchos grupos, un grupo tiene muchos participantes
PARTICIPANTE_GRUPO = Table(
    'PARTICIPANTE_GRUPO',
    Base.metadata,
    Column('participante_id', Integer, ForeignKey('PARTICIPANTE.id'), primary_key=True),
    Column('grupo_id', Integer, ForeignKey('GRUPO.id'), primary_key=True),
    Column('fecha_asignacion', DateTime, default=datetime.utcnow)
)

# Relación: Un educador puede dictar muchos grupos, un grupo puede tener varios educadores
EDUCADOR_GRUPO = Table(
    'EDUCADOR_GRUPO',
    Base.metadata,
    Column('educador_id', Integer, ForeignKey('USUARIO.id'), primary_key=True),
    Column('grupo_id', Integer, ForeignKey('GRUPO.id'), primary_key=True),
    Column('fecha_asignacion', DateTime, default=datetime.utcnow)
)