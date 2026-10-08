from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import Usuario, Rol
from app.schemas import UsuarioCreate, UsuarioResponse
from app.auth import (
    LoginRequest, TokenResponse, RegisterRequest,
    hash_password, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# ============================================
# ENDPOINT: LOGIN
# ============================================

@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión")
def login(credenciales: LoginRequest, db: Session = Depends(get_db)):
    """
    **Endpoint de Login**
    
    Valida email y contraseña, y devuelve un token JWT para usar en otros endpoints.
    
    **Ejemplo de uso:**
    ```json
    {
        "email": "coordinador@presente.com",
        "password": "123456"
    }
    ```
    """
    
    # Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == credenciales.email).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Verificar contraseña
    if not verify_password(credenciales.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Verificar que el usuario está activo
    if usuario.estado != "Activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo o bloqueado"
        )
    
    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.email, "rol": usuario.rol.nombre},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido
        },
        "rol": usuario.rol.nombre
    }

# ============================================
# ENDPOINT: REGISTRAR USUARIO
# ============================================

@router.post("/register", response_model=UsuarioResponse, summary="Registrar nuevo usuario")
def register(datos: RegisterRequest, db: Session = Depends(get_db)):
    """
    **Endpoint de Registro**
    
    Crea un nuevo usuario en el sistema.
    
    **Ejemplo de uso:**
    ```json
    {
        "email": "nuevo@usuario.com",
        "nombre": "Juan",
        "apellido": "Pérez",
        "password": "123456",
        "rol": "Participante"
    }
    ```
    
    **Roles disponibles:** Coordinador, Educador, Participante
    """
    
    # Verificar si el email ya existe
    usuario_existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Buscar el rol
    rol = db.query(Rol).filter(Rol.nombre == datos.rol).first()
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol '{datos.rol}' no existe. Disponibles: Coordinador, Educador, Participante"
        )
    
    # Crear nuevo usuario
    nuevo_usuario = Usuario(
        email=datos.email,
        nombre=datos.nombre,
        apellido=datos.apellido,
        password_hash=hash_password(datos.password),
        rol_id=rol.id,
        estado="Activo"
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario

# ============================================
# ENDPOINT: OBTENER USUARIO ACTUAL
# ============================================

@router.get("/me", response_model=dict, summary="Obtener datos del usuario actual")
def obtener_usuario_actual(usuario_actual: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    **Obtener Usuario Actual**
    
    Devuelve los datos del usuario autenticado.
    
    **Requiere:** Token JWT en header Authorization
    
    **Ejemplo de header:**
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    """
    
    email = usuario_actual.get("sub")
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return {
        "id": usuario.id,
        "email": usuario.email,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "rol": usuario.rol.nombre,
        "estado": usuario.estado
    }

# ============================================
# ENDPOINT: CAMBIAR CONTRASEÑA
# ============================================

@router.post("/cambiar-password", summary="Cambiar contraseña del usuario")
def cambiar_password(
    password_vieja: str,
    password_nueva: str,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Cambiar Contraseña**
    
    Permite al usuario autenticado cambiar su contraseña.
    """
    
    email = usuario_actual.get("sub")
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    # Verificar contraseña actual
    if not verify_password(password_vieja, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña actual incorrecta"
        )
    
    # Actualizar contraseña
    usuario.password_hash = hash_password(password_nueva)
    db.commit()
    
    return {"mensaje": "Contraseña actualizada correctamente"}

# ============================================
# ENDPOINT: LISTAR USUARIOS (solo Coordinador)
# ============================================

@router.get("/usuarios", response_model=list, summary="Listar todos los usuarios (solo Coordinador)")
def listar_usuarios(
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Listar Usuarios**
    
    Solo los Coordinadores pueden ver la lista de todos los usuarios.
    """
    
    # Verificar que sea Coordinador
    if usuario_actual.get("rol") != "Coordinador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores pueden ver la lista de usuarios"
        )
    
    usuarios = db.query(Usuario).all()
    
    return [
        {
            "id": u.id,
            "email": u.email,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "rol": u.rol.nombre,
            "estado": u.estado
        }
        for u in usuarios
    ]

# ============================================
# ENDPOINT: DESACTIVAR USUARIO (solo Coordinador)
# ============================================

@router.patch("/usuarios/{usuario_id}/desactivar", summary="Desactivar usuario (solo Coordinador)")
def desactivar_usuario(
    usuario_id: int,
    usuario_actual: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **Desactivar Usuario**
    
    Permite al Coordinador desactivar un usuario (no se puede eliminar, solo inactivar).
    """
    
    # Verificar que sea Coordinador
    if usuario_actual.get("rol") != "Coordinador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Coordinadores pueden desactivar usuarios"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    usuario.estado = "Inactivo"
    db.commit()
    
    return {"mensaje": f"Usuario {usuario.email} desactivado"}
