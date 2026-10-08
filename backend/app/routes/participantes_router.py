from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import Participante, Tutor, Grupo, Asistencia
from app.schemas import ParticipanteCreate, ParticipanteResponse, TutorCreate, TutorResponse
from app.auth import get_current_user

router = APIRouter(prefix="/participantes", tags=["Participantes"])

# ============================================
# ENDPOINT: CREAR PARTICIPANTE
# ============================================

@router.post("/", response_model=dict, summary="Crear nuevo participante")
def crear_participante(
    datos: ParticipanteCreate,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Crear Participante**
    
    Crea un nuevo participante en el sistema.
    
    **Requiere:** Rol de Coordinador o Educador
    
    **Ejemplo:**
    ```json
    {
        "nombre": "Carlos",
        "apellido": "García",
        "dni": "12345678",
        "fecha_nacimiento": "2010-05-15T00:00:00",
        "domicilio": "Calle 123",
        "telefono": "1234567890",
        "tutor_id": 1
    }
    ```
    """
    
    # Verificar permisos
    rol = usuario_actual.get("rol")
    if rol not in ["Coordinador", "Educador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores y Educadores pueden crear participantes"
        )
    
    # Verificar DNI único
    participante_existente = db.query(Participante).filter(Participante.dni == datos.dni).first()
    if participante_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un participante con DNI {datos.dni}"
        )
    
    # Si se proporciona tutor_id, verificar que existe
    if datos.tutor_id:
        tutor = db.query(Tutor).filter(Tutor.id == datos.tutor_id).first()
        if not tutor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tutor con ID {datos.tutor_id} no existe"
            )
    
    # Crear participante
    nuevo_participante = Participante(
        nombre=datos.nombre,
        apellido=datos.apellido,
        dni=datos.dni,
        fecha_nacimiento=datos.fecha_nacimiento,
        domicilio=datos.domicilio,
        telefono=datos.telefono,
        tutor_id=datos.tutor_id,
        estado="Activo"
    )
    
    db.add(nuevo_participante)
    db.commit()
    db.refresh(nuevo_participante)
    
    return {
        "id": nuevo_participante.id,
        "nombre": nuevo_participante.nombre,
        "apellido": nuevo_participante.apellido,
        "dni": nuevo_participante.dni,
        "mensaje": "Participante creado exitosamente"
    }

# ============================================
# ENDPOINT: LISTAR PARTICIPANTES
# ============================================

@router.get("/", response_model=list, summary="Listar participantes con filtros")
def listar_participantes(
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Cantidad de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad de registros a traer"),
    nombre: str = Query(None, description="Filtrar por nombre o apellido"),
    dni: str = Query(None, description="Filtrar por DNI"),
    estado: str = Query(None, description="Filtrar por estado (Activo, Seguimiento, Inactivo)"),
    grupo_id: int = Query(None, description="Filtrar por grupo")
):
    """
    **Listar Participantes**
    
    Obtiene lista de participantes con opciones de filtrado.
    
    **Parámetros de consulta:**
    - `skip`: Saltar primeros N registros (para paginación)
    - `limit`: Máximo de registros a devolver
    - `nombre`: Buscar por nombre o apellido
    - `dni`: Buscar por DNI exacto
    - `estado`: Activo, Seguimiento o Inactivo
    - `grupo_id`: Filtrar por grupo
    
    **Ejemplo:**
    ```
    GET /participantes/?nombre=Carlos&estado=Activo&limit=20
    ```
    """
    
    query = db.query(Participante)
    
    # Aplicar filtros
    if nombre:
        query = query.filter(
            (Participante.nombre.ilike(f"%{nombre}%")) |
            (Participante.apellido.ilike(f"%{nombre}%"))
        )
    
    if dni:
        query = query.filter(Participante.dni == dni)
    
    if estado:
        query = query.filter(Participante.estado == estado)
    
    if grupo_id:
        query = query.join(Participante.grupos).filter(Grupo.id == grupo_id)
    
    # Paginación
    total = query.count()
    participantes = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "datos": [
            {
                "id": p.id,
                "nombre": p.nombre,
                "apellido": p.apellido,
                "dni": p.dni,
                "estado": p.estado,
                "tutor": {
                    "id": p.tutor.id,
                    "nombre": p.tutor.nombre,
                    "apellido": p.tutor.apellido
                } if p.tutor else None,
                "grupos": [{"id": g.id, "nombre": g.nombre} for g in p.grupos]
            }
            for p in participantes
        ]
    }

# ============================================
# ENDPOINT: OBTENER UN PARTICIPANTE
# ============================================

@router.get("/{participante_id}", response_model=dict, summary="Obtener datos de un participante")
def obtener_participante(
    participante_id: int,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Obtener Participante**
    
    Devuelve los datos completos de un participante incluyendo:
    - Datos personales
    - Información del tutor
    - Grupos a los que pertenece
    - Historial de asistencia
    """
    
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participante no encontrado"
        )
    
    # Calcular estadísticas de asistencia
    asistencias = db.query(Asistencia).filter(Asistencia.participante_id == participante_id).all()
    presentes = len([a for a in asistencias if a.estado == "Presente"])
    ausentes = len([a for a in asistencias if a.estado == "Ausente"])
    porcentaje = (presentes / len(asistencias) * 100) if asistencias else 0
    
    return {
        "id": participante.id,
        "nombre": participante.nombre,
        "apellido": participante.apellido,
        "dni": participante.dni,
        "fecha_nacimiento": participante.fecha_nacimiento,
        "domicilio": participante.domicilio,
        "telefono": participante.telefono,
        "estado": participante.estado,
        "tutor": {
            "id": participante.tutor.id,
            "nombre": participante.tutor.nombre,
            "apellido": participante.tutor.apellido,
            "email": participante.tutor.email,
            "telefono": participante.tutor.telefono,
            "domicilio": participante.tutor.domicilio
        } if participante.tutor else None,
        "grupos": [
            {
                "id": g.id,
                "nombre": g.nombre,
                "dia": g.dia_semana,
                "horario": g.horario
            }
            for g in participante.grupos
        ],
        "estadisticas": {
            "total_asistencias": len(asistencias),
            "presentes": presentes,
            "ausentes": ausentes,
            "porcentaje_asistencia": round(porcentaje, 2)
        }
    }

# ============================================
# ENDPOINT: ACTUALIZAR PARTICIPANTE
# ============================================

@router.put("/{participante_id}", response_model=dict, summary="Actualizar datos de participante")
def actualizar_participante(
    participante_id: int,
    datos: ParticipanteCreate,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Actualizar Participante**
    
    Actualiza los datos de un participante existente.
    
    **Requiere:** Rol de Coordinador o Educador
    """
    
    rol = usuario_actual.get("rol")
    if rol not in ["Coordinador", "Educador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores y Educadores pueden actualizar participantes"
        )
    
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participante no encontrado"
        )
    
    # Verificar DNI si cambió
    if datos.dni != participante.dni:
        existente = db.query(Participante).filter(Participante.dni == datos.dni).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe otro participante con DNI {datos.dni}"
            )
    
    # Actualizar campos
    participante.nombre = datos.nombre
    participante.apellido = datos.apellido
    participante.dni = datos.dni
    participante.fecha_nacimiento = datos.fecha_nacimiento
    participante.domicilio = datos.domicilio
    participante.telefono = datos.telefono
    participante.tutor_id = datos.tutor_id
    participante.fecha_actualizacion = datetime.utcnow()
    
    db.commit()
    db.refresh(participante)
    
    return {
        "id": participante.id,
        "nombre": participante.nombre,
        "apellido": participante.apellido,
        "dni": participante.dni,
        "mensaje": "Participante actualizado exitosamente"
    }

# ============================================
# ENDPOINT: CREAR TUTOR
# ============================================

@router.post("/tutores/", response_model=dict, summary="Crear nuevo tutor")
def crear_tutor(
    datos: TutorCreate,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Crear Tutor**
    
    Crea un nuevo tutor que puede estar vinculado a participantes.
    """
    
    rol = usuario_actual.get("rol")
    if rol not in ["Coordinador", "Educador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores y Educadores pueden crear tutores"
        )
    
    nuevo_tutor = Tutor(
        nombre=datos.nombre,
        apellido=datos.apellido,
        email=datos.email,
        telefono=datos.telefono,
        domicilio=datos.domicilio
    )
    
    db.add(nuevo_tutor)
    db.commit()
    db.refresh(nuevo_tutor)
    
    return {
        "id": nuevo_tutor.id,
        "nombre": nuevo_tutor.nombre,
        "apellido": nuevo_tutor.apellido,
        "mensaje": "Tutor creado exitosamente"
    }

# ============================================
# ENDPOINT: ASIGNAR PARTICIPANTE A GRUPO
# ============================================

@router.post("/{participante_id}/asignar-grupo/{grupo_id}", summary="Asignar participante a grupo")
def asignar_participante_grupo(
    participante_id: int,
    grupo_id: int,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Asignar Participante a Grupo**
    
    Vincula un participante con un grupo/taller.
    """
    
    rol = usuario_actual.get("rol")
    if rol not in ["Coordinador", "Educador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores y Educadores pueden asignar grupos"
        )
    
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    if not participante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participante no encontrado")
    
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado")
    
    # Verificar si ya está asignado
    if grupo in participante.grupos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participante ya está en este grupo"
        )
    
    participante.grupos.append(grupo)
    db.commit()
    
    return {"mensaje": f"Participante {participante.nombre} asignado al grupo {grupo.nombre}"}

# ============================================
# ENDPOINT: DESASIGNAR PARTICIPANTE DE GRUPO
# ============================================

@router.delete("/{participante_id}/quitar-grupo/{grupo_id}", summary="Desasignar participante de grupo")
def desasignar_participante_grupo(
    participante_id: int,
    grupo_id: int,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Desasignar Participante de Grupo**
    
    Desvincula un participante de un grupo.
    """
    
    rol = usuario_actual.get("rol")
    if rol not in ["Coordinador", "Educador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores y Educadores pueden desasignar grupos"
        )
    
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    if not participante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participante no encontrado")
    
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado")
    
    if grupo not in participante.grupos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participante no está en este grupo"
        )
    
    participante.grupos.remove(grupo)
    db.commit()
    
    return {"mensaje": f"Participante removido del grupo {grupo.nombre}"}
