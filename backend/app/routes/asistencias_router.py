from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List
from app.database import get_db
from app.models import Asistencia, Participante, Grupo, Usuario, Alerta
from app.schemas import AsistenciaCreate, AsistenciaResponse
from app.auth import get_current_user

router = APIRouter(prefix="/asistencias", tags=["Asistencias"])

# ============================================
# ENDPOINT: REGISTRAR ASISTENCIA
# ============================================

@router.post("/", response_model=dict, summary="Registrar asistencia de un participante")
def registrar_asistencia(
    datos: AsistenciaCreate,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Registrar Asistencia**
    
    Registra la asistencia de un participante en una jornada.
    
    **Requiere:** Rol de Coordinador o Educador
    
    **Ejemplo:**
    ```json
    {
        "participante_id": 1,
        "grupo_id": 1,
        "fecha": "2024-01-15T14:00:00",
        "estado": "Presente",
        "observaciones": "Llegó 5 minutos tarde"
    }
    ```
    
    **Estados válidos:** Presente, Ausente, Tarde, Justificado
    """
    
    rol = usuario_actual.get("rol")
    if rol not in ["Coordinador", "Educador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores y Educadores pueden registrar asistencias"
        )
    
    # Validar estados
    estados_validos = ["Presente", "Ausente", "Tarde", "Justificado"]
    if datos.estado not in estados_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"
        )
    
    # Verificar que participante y grupo existen
    participante = db.query(Participante).filter(Participante.id == datos.participante_id).first()
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participante no encontrado"
        )
    
    grupo = db.query(Grupo).filter(Grupo.id == datos.grupo_id).first()
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado"
        )
    
    # Obtener ID del educador actual
    email_usuario = usuario_actual.get("sub")
    educador = db.query(Usuario).filter(Usuario.email == email_usuario).first()
    
    # Crear registro de asistencia
    asistencia = Asistencia(
        participante_id=datos.participante_id,
        grupo_id=datos.grupo_id,
        fecha=datos.fecha,
        estado=datos.estado,
        educador_id=educador.id if educador else None,
        observaciones=datos.observaciones
    )
    
    db.add(asistencia)
    db.flush()  # Para obtener el ID antes de commit
    
    # ============================================
    # MOTOR DE ALERTAS: Generar alertas automáticas
    # ============================================
    
    if datos.estado == "Ausente":
        # Contar inasistencias consecutivas
        ultimas_asistencias = db.query(Asistencia).filter(
            Asistencia.participante_id == datos.participante_id,
            Asistencia.grupo_id == datos.grupo_id
        ).order_by(Asistencia.fecha.desc()).limit(3).all()
        
        ausentes_consecutivos = 0
        for ast in ultimas_asistencias:
            if ast.estado == "Ausente":
                ausentes_consecutivos += 1
            else:
                break
        
        # Alerta por 3 inasistencias consecutivas (CRÍTICA)
        if ausentes_consecutivos >= 3:
            alerta_existente = db.query(Alerta).filter(
                Alerta.participante_id == datos.participante_id,
                Alerta.grupo_id == datos.grupo_id,
                Alerta.estado == "Activa",
                Alerta.tipo == "Crítica"
            ).first()
            
            if not alerta_existente:
                alerta = Alerta(
                    participante_id=datos.participante_id,
                    grupo_id=datos.grupo_id,
                    tipo="Crítica",
                    descripcion=f"{ausentes_consecutivos} inasistencias consecutivas",
                    estado="Activa"
                )
                db.add(alerta)
        
        # Alerta por 2 inasistencias consecutivas (ATENCIÓN)
        elif ausentes_consecutivos == 2:
            alerta_existente = db.query(Alerta).filter(
                Alerta.participante_id == datos.participante_id,
                Alerta.grupo_id == datos.grupo_id,
                Alerta.estado == "Activa",
                Alerta.tipo == "Atención"
            ).first()
            
            if not alerta_existente:
                alerta = Alerta(
                    participante_id=datos.participante_id,
                    grupo_id=datos.grupo_id,
                    tipo="Atención",
                    descripcion=f"{ausentes_consecutivos} inasistencias consecutivas",
                    estado="Activa"
                )
                db.add(alerta)
        
        # Contar inasistencias en el mes actual
        mes_actual = datos.fecha.month
        ano_actual = datos.fecha.year
        
        ausencias_mes = db.query(Asistencia).filter(
            Asistencia.participante_id == datos.participante_id,
            Asistencia.grupo_id == datos.grupo_id,
            Asistencia.estado == "Ausente",
            Asistencia.fecha.extract('month') == mes_actual,
            Asistencia.fecha.extract('year') == ano_actual
        ).count()
        
        # Alerta por 3 ausencias en el mes
        if ausencias_mes >= 3:
            alerta_existente = db.query(Alerta).filter(
                Alerta.participante_id == datos.participante_id,
                Alerta.grupo_id == datos.grupo_id,
                Alerta.estado == "Activa",
                Alerta.descripcion.contains("3 inasistencias acumuladas en el mes")
            ).first()
            
            if not alerta_existente:
                alerta = Alerta(
                    participante_id=datos.participante_id,
                    grupo_id=datos.grupo_id,
                    tipo="Atención",
                    descripcion=f"3 inasistencias acumuladas en el mes",
                    estado="Activa"
                )
                db.add(alerta)
    
    db.commit()
    db.refresh(asistencia)
    
    return {
        "id": asistencia.id,
        "participante": participante.nombre,
        "grupo": grupo.nombre,
        "fecha": datos.fecha,
        "estado": datos.estado,
        "mensaje": "Asistencia registrada exitosamente"
    }

# ============================================
# ENDPOINT: REGISTRAR LOTE DE ASISTENCIAS
# ============================================

@router.post("/lote", response_model=dict, summary="Registrar asistencia de múltiples participantes")
def registrar_lote_asistencias(
    grupo_id: int,
    fecha: datetime,
    asistencias: List[dict],  # [{"participante_id": 1, "estado": "Presente"}, ...]
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Registrar Lote de Asistencias**
    
    Registra la asistencia de múltiples participantes en una sola jornada.
    
    **Requiere:** Rol de Coordinador o Educador
    
    **Ejemplo:**
    ```json
    {
        "grupo_id": 1,
        "fecha": "2024-01-15T14:00:00",
        "asistencias": [
            {"participante_id": 1, "estado": "Presente"},
            {"participante_id": 2, "estado": "Ausente"},
            {"participante_id": 3, "estado": "Tarde"}
        ]
    }
    ```
    """
    
    rol = usuario_actual.get("rol")
    if rol not in ["Coordinador", "Educador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores y Educadores pueden registrar asistencias"
        )
    
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado"
        )
    
    email_usuario = usuario_actual.get("sub")
    educador = db.query(Usuario).filter(Usuario.email == email_usuario).first()
    
    registros_creados = 0
    errores = []
    
    for asist in asistencias:
        try:
            participante_id = asist.get("participante_id")
            estado = asist.get("estado")
            
            participante = db.query(Participante).filter(Participante.id == participante_id).first()
            if not participante:
                errores.append(f"Participante {participante_id} no encontrado")
                continue
            
            nueva_asistencia = Asistencia(
                participante_id=participante_id,
                grupo_id=grupo_id,
                fecha=fecha,
                estado=estado,
                educador_id=educador.id if educador else None
            )
            
            db.add(nueva_asistencia)
            registros_creados += 1
            
        except Exception as e:
            errores.append(f"Error en participante {participante_id}: {str(e)}")
    
    db.commit()
    
    return {
        "registros_creados": registros_creados,
        "errores": errores,
        "mensaje": f"Se registraron {registros_creados} asistencias"
    }

# ============================================
# ENDPOINT: OBTENER HISTORIAL DE ASISTENCIAS
# ============================================

@router.get("/", response_model=dict, summary="Obtener historial de asistencias con filtros")
def obtener_asistencias(
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    participante_id: int = Query(None),
    grupo_id: int = Query(None),
    fecha_inicio: date = Query(None),
    fecha_fin: date = Query(None),
    estado: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    **Obtener Historial de Asistencias**
    
    Obtiene registro de asistencias con opciones de filtrado.
    
    **Parámetros:**
    - `participante_id`: Filtrar por participante
    - `grupo_id`: Filtrar por grupo
    - `fecha_inicio`: Filtrar desde fecha (YYYY-MM-DD)
    - `fecha_fin`: Filtrar hasta fecha (YYYY-MM-DD)
    - `estado`: Filtrar por estado (Presente, Ausente, Tarde, Justificado)
    - `skip`: Cantidad de registros a saltar
    - `limit`: Máximo de registros a devolver
    
    **Ejemplo:**
    ```
    GET /asistencias/?participante_id=1&fecha_inicio=2024-01-01&estado=Ausente
    ```
    """
    
    query = db.query(Asistencia)
    
    # Aplicar filtros
    if participante_id:
        query = query.filter(Asistencia.participante_id == participante_id)
    
    if grupo_id:
        query = query.filter(Asistencia.grupo_id == grupo_id)
    
    if fecha_inicio:
        query = query.filter(Asistencia.fecha >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(Asistencia.fecha <= fecha_fin)
    
    if estado:
        query = query.filter(Asistencia.estado == estado)
    
    # Si es Educador, solo mostrar asistencias de sus grupos
    if usuario_actual.get("rol") == "Educador":
        email = usuario_actual.get("sub")
        educador = db.query(Usuario).filter(Usuario.email == email).first()
        grupos_educador = [g.id for g in educador.grupos]
        query = query.filter(Asistencia.grupo_id.in_(grupos_educador))
    
    total = query.count()
    asistencias = query.order_by(Asistencia.fecha.desc()).offset(skip).limit(limit).all()
    
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
                "fecha": a.fecha,
                "estado": a.estado,
                "observaciones": a.observaciones,
                "educador": a.educador.nombre if a.educador else None
            }
            for a in asistencias
        ]
    }

# ============================================
# ENDPOINT: OBTENER ASISTENCIAS DE UN GRUPO EN UNA FECHA
# ============================================

@router.get("/grupo/{grupo_id}/fecha/{fecha_str}", response_model=dict, summary="Obtener asistencias de un grupo en una fecha específica")
def obtener_asistencias_grupo_fecha(
    grupo_id: int,
    fecha_str: str,  # Formato: YYYY-MM-DD
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Obtener Asistencias de Grupo en Fecha**
    
    Devuelve todos los registros de asistencia de un grupo para un día específico.
    
    **Parámetros:**
    - `grupo_id`: ID del grupo
    - `fecha_str`: Fecha en formato YYYY-MM-DD
    
    **Ejemplo:**
    ```
    GET /asistencias/grupo/1/fecha/2024-01-15
    ```
    """
    
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Usa YYYY-MM-DD"
        )
    
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado"
        )
    
    asistencias = db.query(Asistencia).filter(
        Asistencia.grupo_id == grupo_id,
        Asistencia.fecha.cast(date) == fecha
    ).all()
    
    # Contar estados
    presentes = len([a for a in asistencias if a.estado == "Presente"])
    ausentes = len([a for a in asistencias if a.estado == "Ausente"])
    tardios = len([a for a in asistencias if a.estado == "Tarde"])
    
    return {
        "grupo": grupo.nombre,
        "fecha": fecha,
        "total_registros": len(asistencias),
        "estadisticas": {
            "presentes": presentes,
            "ausentes": ausentes,
            "tardios": tardios
        },
        "datos": [
            {
                "id": a.id,
                "participante": {
                    "id": a.participante.id,
                    "nombre": a.participante.nombre,
                    "apellido": a.participante.apellido
                },
                "estado": a.estado,
                "observaciones": a.observaciones
            }
            for a in asistencias
        ]
    }

# ============================================
# ENDPOINT: OBTENER PARTICIPANTES LISTOS PARA TOMAR ASISTENCIA
# ============================================

@router.get("/grupo/{grupo_id}/listos", response_model=dict, summary="Obtener participantes listos para asistencia")
def obtener_participantes_asistencia(
    grupo_id: int,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Obtener Participantes para Asistencia**
    
    Devuelve la lista de participantes activos de un grupo, listos para registrar asistencia.
    
    Útil para la UI de toma de asistencia.
    """
    
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado"
        )
    
    return {
        "grupo": {
            "id": grupo.id,
            "nombre": grupo.nombre,
            "dia": grupo.dia_semana,
            "horario": grupo.horario
        },
        "participantes": [
            {
                "id": p.id,
                "nombre": p.nombre,
                "apellido": p.apellido,
                "dni": p.dni,
                "estado": p.estado
            }
            for p in grupo.participantes if p.estado == "Activo"
        ]
    }
