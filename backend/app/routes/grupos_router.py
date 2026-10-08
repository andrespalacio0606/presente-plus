from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import Grupo, Usuario, Participante
from app.schemas import GrupoCreate, GrupoResponse
from app.auth import get_current_user

router = APIRouter(prefix="/grupos", tags=["Grupos"])

# ============================================
# ENDPOINT: CREAR GRUPO
# ============================================

@router.post("/", response_model=dict, summary="Crear nuevo grupo/taller")
def crear_grupo(
    datos: GrupoCreate,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Crear Grupo/Taller**
    
    Crea un nuevo grupo o taller en el sistema.
    
    **Requiere:** Rol de Coordinador
    
    **Ejemplo:**
    ```json
    {
        "nombre": "Matemáticas Nivel 1",
        "descripcion": "Taller de matemáticas básicas",
        "tipo_actividad": "Taller",
        "rango_etario": "8-12 años",
        "dia_semana": "Lunes",
        "horario": "14:00-15:30",
        "cupo_maximo": 20
    }
    ```
    """
    
    # Verificar que es Coordinador
    if usuario_actual.get("rol") != "Coordinador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores pueden crear grupos"
        )
    
    # Crear grupo
    nuevo_grupo = Grupo(
        nombre=datos.nombre,
        descripcion=datos.descripcion,
        tipo_actividad=datos.tipo_actividad,
        rango_etario=datos.rango_etario,
        dia_semana=datos.dia_semana,
        horario=datos.horario,
        cupo_maximo=datos.cupo_maximo,
        estado="Activo"
    )
    
    db.add(nuevo_grupo)
    db.commit()
    db.refresh(nuevo_grupo)
    
    return {
        "id": nuevo_grupo.id,
        "nombre": nuevo_grupo.nombre,
        "estado": nuevo_grupo.estado,
        "mensaje": "Grupo creado exitosamente"
    }

# ============================================
# ENDPOINT: LISTAR GRUPOS
# ============================================

@router.get("/", response_model=dict, summary="Listar grupos con filtros")
def listar_grupos(
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    nombre: str = Query(None),
    estado: str = Query(None),
    tipo_actividad: str = Query(None)
):
    """
    **Listar Grupos**
    
    Obtiene lista de grupos con opciones de filtrado.
    
    **Parámetros:**
    - `skip`: Cantidad de registros a saltar
    - `limit`: Máximo de registros a devolver
    - `nombre`: Filtrar por nombre del grupo
    - `estado`: Filtrar por estado (Activo, Pausado, Finalizado)
    - `tipo_actividad`: Filtrar por tipo
    
    **Nota:** Los Educadores solo ven sus grupos asignados
    """
    
    query = db.query(Grupo)
    
    # Si es Educador, solo mostrar sus grupos
    if usuario_actual.get("rol") == "Educador":
        email = usuario_actual.get("sub")
        educador = db.query(Usuario).filter(Usuario.email == email).first()
        query = query.filter(Grupo.educadores.contains(educador))
    
    # Aplicar filtros
    if nombre:
        query = query.filter(Grupo.nombre.ilike(f"%{nombre}%"))
    
    if estado:
        query = query.filter(Grupo.estado == estado)
    
    if tipo_actividad:
        query = query.filter(Grupo.tipo_actividad == tipo_actividad)
    
    total = query.count()
    grupos = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "datos": [
            {
                "id": g.id,
                "nombre": g.nombre,
                "descripcion": g.descripcion,
                "tipo_actividad": g.tipo_actividad,
                "rango_etario": g.rango_etario,
                "dia_semana": g.dia_semana,
                "horario": g.horario,
                "cupo_maximo": g.cupo_maximo,
                "cantidad_participantes": len(g.participantes),
                "estado": g.estado,
                "educadores": [
                    {"id": e.id, "nombre": e.nombre, "apellido": e.apellido}
                    for e in g.educadores
                ]
            }
            for g in grupos
        ]
    }

# ============================================
# ENDPOINT: OBTENER UN GRUPO
# ============================================

@router.get("/{grupo_id}", response_model=dict, summary="Obtener detalles de un grupo")
def obtener_grupo(
    grupo_id: int,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Obtener Grupo**
    
    Devuelve los detalles completos de un grupo incluyendo:
    - Información general
    - Lista de participantes
    - Educadores asignados
    - Estadísticas
    """
    
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado"
        )
    
    return {
        "id": grupo.id,
        "nombre": grupo.nombre,
        "descripcion": grupo.descripcion,
        "tipo_actividad": grupo.tipo_actividad,
        "rango_etario": grupo.rango_etario,
        "dia_semana": grupo.dia_semana,
        "horario": grupo.horario,
        "cupo_maximo": grupo.cupo_maximo,
        "estado": grupo.estado,
        "educadores": [
            {
                "id": e.id,
                "nombre": e.nombre,
                "apellido": e.apellido,
                "email": e.email
            }
            for e in grupo.educadores
        ],
        "participantes": [
            {
                "id": p.id,
                "nombre": p.nombre,
                "apellido": p.apellido,
                "dni": p.dni,
                "estado": p.estado
            }
            for p in grupo.participantes
        ],
        "estadisticas": {
            "total_participantes": len(grupo.participantes),
            "lugares_disponibles": grupo.cupo_maximo - len(grupo.participantes) if grupo.cupo_maximo else None,
            "porcentaje_ocupacion": (len(grupo.participantes) / grupo.cupo_maximo * 100) if grupo.cupo_maximo else 0
        }
    }

# ============================================
# ENDPOINT: ACTUALIZAR GRUPO
# ============================================

@router.put("/{grupo_id}", response_model=dict, summary="Actualizar datos de grupo")
def actualizar_grupo(
    grupo_id: int,
    datos: GrupoCreate,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Actualizar Grupo**
    
    Actualiza los datos de un grupo existente.
    
    **Requiere:** Rol de Coordinador
    """
    
    if usuario_actual.get("rol") != "Coordinador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores pueden actualizar grupos"
        )
    
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado"
        )
    
    grupo.nombre = datos.nombre
    grupo.descripcion = datos.descripcion
    grupo.tipo_actividad = datos.tipo_actividad
    grupo.rango_etario = datos.rango_etario
    grupo.dia_semana = datos.dia_semana
    grupo.horario = datos.horario
    grupo.cupo_maximo = datos.cupo_maximo
    
    db.commit()
    db.refresh(grupo)
    
    return {
        "id": grupo.id,
        "nombre": grupo.nombre,
        "mensaje": "Grupo actualizado exitosamente"
    }

# ============================================
# ENDPOINT: CAMBIAR ESTADO DEL GRUPO
# ============================================

@router.patch("/{grupo_id}/estado/{nuevo_estado}", summary="Cambiar estado del grupo")
def cambiar_estado_grupo(
    grupo_id: int,
    nuevo_estado: str,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Cambiar Estado del Grupo**
    
    Cambia el estado de un grupo (Activo, Pausado, Finalizado).
    
    **Requiere:** Rol de Coordinador
    
    **Estados válidos:** Activo, Pausado, Finalizado
    """
    
    if usuario_actual.get("rol") != "Coordinador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores pueden cambiar estados de grupos"
        )
    
    estados_validos = ["Activo", "Pausado", "Finalizado"]
    if nuevo_estado not in estados_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"
        )
    
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado"
        )
    
    grupo.estado = nuevo_estado
    db.commit()
    
    return {"mensaje": f"Estado del grupo cambiado a '{nuevo_estado}'"}

# ============================================
# ENDPOINT: ASIGNAR EDUCADOR A GRUPO
# ============================================

@router.post("/{grupo_id}/educadores/{educador_id}", summary="Asignar educador a grupo")
def asignar_educador(
    grupo_id: int,
    educador_id: int,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Asignar Educador a Grupo**
    
    Vincula un educador con un grupo como responsable.
    
    **Requiere:** Rol de Coordinador
    """
    
    if usuario_actual.get("rol") != "Coordinador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores pueden asignar educadores"
        )
    
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado"
        )
    
    educador = db.query(Usuario).filter(Usuario.id == educador_id).first()
    if not educador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educador no encontrado"
        )
    
    if educador.rol.nombre != "Educador":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene rol de Educador"
        )
    
    if educador in grupo.educadores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El educador ya está asignado a este grupo"
        )
    
    grupo.educadores.append(educador)
    db.commit()
    
    return {"mensaje": f"Educador {educador.nombre} asignado al grupo {grupo.nombre}"}

# ============================================
# ENDPOINT: DESASIGNAR EDUCADOR DE GRUPO
# ============================================

@router.delete("/{grupo_id}/educadores/{educador_id}", summary="Desasignar educador de grupo")
def desasignar_educador(
    grupo_id: int,
    educador_id: int,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Desasignar Educador de Grupo**
    
    Desvincula un educador de un grupo.
    
    **Requiere:** Rol de Coordinador
    """
    
    if usuario_actual.get("rol") != "Coordinador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores pueden desasignar educadores"
        )
    
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado"
        )
    
    educador = db.query(Usuario).filter(Usuario.id == educador_id).first()
    if not educador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educador no encontrado"
        )
    
    if educador not in grupo.educadores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El educador no está asignado a este grupo"
        )
    
    grupo.educadores.remove(educador)
    db.commit()
    
    return {"mensaje": f"Educador removido del grupo {grupo.nombre}"}