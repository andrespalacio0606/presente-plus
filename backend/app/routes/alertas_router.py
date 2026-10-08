from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import Alerta, Participante, Grupo
from app.auth import get_current_user

router = APIRouter(prefix="/alertas", tags=["Alertas"])

# ============================================
# ENDPOINT: OBTENER ALERTAS
# ============================================

@router.get("/", response_model=dict, summary="Obtener alertas con filtros")
def obtener_alertas(
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    estado: str = Query(None, description="Filtrar por estado (Activa, Resuelta)"),
    tipo: str = Query(None, description="Filtrar por tipo (Atención, Crítica)"),
    participante_id: int = Query(None, description="Filtrar por participante"),
    grupo_id: int = Query(None, description="Filtrar por grupo"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    **Obtener Alertas**
    
    Obtiene lista de alertas con opciones de filtrado.
    
    **Parámetros:**
    - `estado`: Activa o Resuelta
    - `tipo`: Atención o Crítica
    - `participante_id`: Filtrar por participante
    - `grupo_id`: Filtrar por grupo
    - `skip`: Cantidad de registros a saltar
    - `limit`: Máximo de registros a devolver
    
    **Nota:** Los Educadores solo ven alertas de sus grupos asignados
    
    **Ejemplo:**
    ```
    GET /alertas/?tipo=Crítica&estado=Activa&limit=20
    ```
    """
    
    query = db.query(Alerta)
    
    # Aplicar filtros
    if estado:
        query = query.filter(Alerta.estado == estado)
    
    if tipo:
        query = query.filter(Alerta.tipo == tipo)
    
    if participante_id:
        query = query.filter(Alerta.participante_id == participante_id)
    
    if grupo_id:
        query = query.filter(Alerta.grupo_id == grupo_id)
    
    # Si es Educador, solo mostrar alertas de sus grupos
    if usuario_actual.get("rol") == "Educador":
        from app.models import Usuario
        email = usuario_actual.get("sub")
        educador = db.query(Usuario).filter(Usuario.email == email).first()
        grupos_educador = [g.id for g in educador.grupos]
        query = query.filter(Alerta.grupo_id.in_(grupos_educador))
    
    total = query.count()
    alertas = query.order_by(Alerta.fecha_creacion.desc()).offset(skip).limit(limit).all()
    
    # Mapear severidad por colores
    severidad_map = {
        "Crítica": {"color": "rojo", "nivel": 3},
        "Atención": {"color": "amarillo", "nivel": 2}
    }
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "datos": [
            {
                "id": a.id,
                "participante": {
                    "id": a.participante.id,
                    "nombre": a.participante.nombre,
                    "apellido": a.participante.apellido
                },
                "grupo": {
                    "id": a.grupo.id,
                    "nombre": a.grupo.nombre
                },
                "tipo": a.tipo,
                "severidad": severidad_map.get(a.tipo, {"color": "gris", "nivel": 1}),
                "descripcion": a.descripcion,
                "estado": a.estado,
                "fecha_creacion": a.fecha_creacion,
                "fecha_resolucion": a.fecha_resolucion,
                "observaciones_resolucion": a.observaciones_resolucion
            }
            for a in alertas
        ]
    }

# ============================================
# ENDPOINT: OBTENER ALERTAS ACTIVAS
# ============================================

@router.get("/activas", response_model=dict, summary="Obtener solo alertas activas")
def obtener_alertas_activas(
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tipo: str = Query(None)
):
    """
    **Obtener Alertas Activas**
    
    Devuelve solo las alertas que aún no han sido resueltas.
    
    **Parámetro opcional:**
    - `tipo`: Filtrar por tipo (Atención, Crítica)
    """
    
    query = db.query(Alerta).filter(Alerta.estado == "Activa")
    
    if tipo:
        query = query.filter(Alerta.tipo == tipo)
    
    # Si es Educador, solo mostrar alertas de sus grupos
    if usuario_actual.get("rol") == "Educador":
        from app.models import Usuario
        email = usuario_actual.get("sub")
        educador = db.query(Usuario).filter(Usuario.email == email).first()
        grupos_educador = [g.id for g in educador.grupos]
        query = query.filter(Alerta.grupo_id.in_(grupos_educador))
    
    alertas = query.order_by(Alerta.fecha_creacion.desc()).all()
    
    # Contar por tipo
    criticas = len([a for a in alertas if a.tipo == "Crítica"])
    atencion = len([a for a in alertas if a.tipo == "Atención"])
    
    return {
        "total": len(alertas),
        "resumen": {
            "criticas": criticas,
            "atencion": atencion
        },
        "datos": [
            {
                "id": a.id,
                "participante": {
                    "id": a.participante.id,
                    "nombre": a.participante.nombre,
                    "apellido": a.participante.apellido
                },
                "grupo": a.grupo.nombre,
                "tipo": a.tipo,
                "descripcion": a.descripcion,
                "fecha_creacion": a.fecha_creacion
            }
            for a in alertas
        ]
    }

# ============================================
# ENDPOINT: OBTENER UNA ALERTA ESPECÍFICA
# ============================================

@router.get("/{alerta_id}", response_model=dict, summary="Obtener detalles de una alerta")
def obtener_alerta(
    alerta_id: int,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Obtener Alerta Específica**
    
    Devuelve los detalles completos de una alerta incluyendo historial.
    """
    
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    
    # Obtener historial de inasistencias del participante
    from app.models import Asistencia
    ultimas_asistencias = db.query(Asistencia).filter(
        Asistencia.participante_id == alerta.participante_id,
        Asistencia.grupo_id == alerta.grupo_id
    ).order_by(Asistencia.fecha.desc()).limit(10).all()
    
    return {
        "id": alerta.id,
        "participante": {
            "id": alerta.participante.id,
            "nombre": alerta.participante.nombre,
            "apellido": alerta.participante.apellido,
            "dni": alerta.participante.dni
        },
        "tutor": {
            "nombre": alerta.participante.tutor.nombre if alerta.participante.tutor else None,
            "apellido": alerta.participante.tutor.apellido if alerta.participante.tutor else None,
            "telefono": alerta.participante.tutor.telefono if alerta.participante.tutor else None
        } if alerta.participante.tutor else None,
        "grupo": {
            "id": alerta.grupo.id,
            "nombre": alerta.grupo.nombre
        },
        "tipo": alerta.tipo,
        "descripcion": alerta.descripcion,
        "estado": alerta.estado,
        "fecha_creacion": alerta.fecha_creacion,
        "fecha_resolucion": alerta.fecha_resolucion,
        "observaciones_resolucion": alerta.observaciones_resolucion,
        "historial_asistencias": [
            {
                "fecha": a.fecha,
                "estado": a.estado,
                "observaciones": a.observaciones
            }
            for a in ultimas_asistencias
        ]
    }

# ============================================
# ENDPOINT: RESOLVER ALERTA
# ============================================

@router.patch("/{alerta_id}/resolver", response_model=dict, summary="Marcar alerta como resuelta")
def resolver_alerta(
    alerta_id: int,
    observaciones: str = Query(..., description="Observaciones de seguimiento"),
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Resolver Alerta**
    
    Marca una alerta como resuelta e incluye las observaciones de seguimiento.
    
    **Requiere:** Rol de Coordinador
    
    **Ejemplo:**
    ```
    PATCH /alertas/1/resolver?observaciones=Se contactó a la familia y se comprometieron a mejorar la asistencia
    ```
    """
    
    if usuario_actual.get("rol") != "Coordinador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores pueden resolver alertas"
        )
    
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    
    if alerta.estado == "Resuelta":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta alerta ya fue resuelta"
        )
    
    # Marcar como resuelta
    alerta.estado = "Resuelta"
    alerta.fecha_resolucion = datetime.utcnow()
    alerta.observaciones_resolucion = observaciones
    
    db.commit()
    db.refresh(alerta)
    
    return {
        "id": alerta.id,
        "estado": alerta.estado,
        "fecha_resolucion": alerta.fecha_resolucion,
        "mensaje": "Alerta resuelta exitosamente"
    }

# ============================================
# ENDPOINT: OBTENER ALERTAS POR PARTICIPANTE
# ============================================

@router.get("/participante/{participante_id}", response_model=dict, summary="Obtener todas las alertas de un participante")
def obtener_alertas_participante(
    participante_id: int,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Obtener Alertas por Participante**
    
    Devuelve todas las alertas (activas y resueltas) de un participante específico.
    """
    
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participante no encontrado"
        )
    
    alertas = db.query(Alerta).filter(Alerta.participante_id == participante_id).all()
    
    alertas_activas = [a for a in alertas if a.estado == "Activa"]
    alertas_resueltas = [a for a in alertas if a.estado == "Resuelta"]
    
    return {
        "participante": {
            "id": participante.id,
            "nombre": participante.nombre,
            "apellido": participante.apellido
        },
        "resumen": {
            "total_alertas": len(alertas),
            "alertas_activas": len(alertas_activas),
            "alertas_resueltas": len(alertas_resueltas)
        },
        "alertas_activas": [
            {
                "id": a.id,
                "tipo": a.tipo,
                "descripcion": a.descripcion,
                "grupo": a.grupo.nombre,
                "fecha_creacion": a.fecha_creacion
            }
            for a in alertas_activas
        ],
        "alertas_resueltas": [
            {
                "id": a.id,
                "tipo": a.tipo,
                "descripcion": a.descripcion,
                "grupo": a.grupo.nombre,
                "fecha_creacion": a.fecha_creacion,
                "fecha_resolucion": a.fecha_resolucion,
                "observaciones": a.observaciones_resolucion
            }
            for a in alertas_resueltas
        ]
    }

# ============================================
# ENDPOINT: OBTENER ESTADÍSTICAS DE ALERTAS
# ============================================

@router.get("/estadisticas/general", response_model=dict, summary="Obtener estadísticas generales de alertas")
def obtener_estadisticas_alertas(
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Estadísticas de Alertas**
    
    Devuelve un resumen estadístico de todas las alertas del sistema.
    
    **Requiere:** Rol de Coordinador
    """
    
    if usuario_actual.get("rol") != "Coordinador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores pueden ver estadísticas generales"
        )
    
    todas_alertas = db.query(Alerta).all()
    alertas_activas = [a for a in todas_alertas if a.estado == "Activa"]
    alertas_criticas = [a for a in alertas_activas if a.tipo == "Crítica"]
    alertas_atencion = [a for a in alertas_activas if a.tipo == "Atención"]
    
    # Participantes con alertas activas
    participantes_con_alertas = len(set([a.participante_id for a in alertas_activas]))
    
    return {
        "resumen_general": {
            "total_alertas": len(todas_alertas),
            "alertas_activas": len(alertas_activas),
            "participantes_con_alertas": participantes_con_alertas
        },
        "por_tipo": {
            "criticas": len(alertas_criticas),
            "atencion": len(alertas_atencion)
        },
        "tendencia": {
            "resueltas_hoy": len([a for a in todas_alertas if a.estado == "Resuelta" and (datetime.utcnow() - a.fecha_resolucion).days == 0]) if todas_alertas else 0,
            "creadas_hoy": len([a for a in todas_alertas if (datetime.utcnow() - a.fecha_creacion).days == 0]) if todas_alertas else 0
        }
    }
