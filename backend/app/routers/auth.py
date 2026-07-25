from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import bcrypt
import jwt
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = "bimej12_super_secret_jwt_key_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str

class UserResponse(BaseModel):
    nombre: str
    correo: str
    roles: list[str]

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UserResponse

def get_user_roles(cursor, user_id: int) -> list[str]:
    cursor.execute("""
        SELECT r.nombre 
        FROM ROL r 
        JOIN USUARIO_ROL ur ON r.id_rol = ur.id_rol 
        WHERE ur.id_usuario = %s;
    """, (user_id,))
    return [row[0] for row in cursor.fetchall()]

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db = Depends(get_db)):
    cursor = db.cursor()
    
    # Fetch user details
    cursor.execute("""
        SELECT id_usuario, nombre, correo, password_hash, activo 
        FROM USUARIO 
        WHERE correo = %s;
    """, (request.correo.lower(),))
    
    user_row = cursor.fetchone()
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )
        
    user_id, nombre, correo, password_hash, activo = user_row
    
    if not activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El usuario se encuentra inactivo"
        )
        
    # Verify password hash
    password_correct = False
    try:
        password_correct = bcrypt.checkpw(
            request.password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    except Exception as e:
        print(f"Error checking password: {e}")
        
    if not password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )
        
    # Intentar verificar credenciales de Google Drive (no bloquea el login si falla o falta token)
    try:
        from config.auth import obtener_servicio_drive
        obtener_servicio_drive()
    except Exception as e:
        print(f"[AUTH WARNING] Google Drive no autenticado aún en el servidor ({e}). El usuario podrá iniciar sesión normalmente.")
        
    # Update last login time
    now = datetime.now()
    cursor.execute("""
        UPDATE USUARIO 
        SET ultimo_login = %s 
        WHERE id_usuario = %s;
    """, (now, user_id))
    db.commit()
    
    # Get user roles
    roles = get_user_roles(cursor, user_id)
    
    # Generate JWT access token
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "nombre": nombre,
        "correo": correo,
        "roles": roles,
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "nombre": nombre,
            "correo": correo,
            "roles": roles
        }
    }

@router.post("/logout")
def logout():
    """Endpoint para cerrar sesión."""
    return {"message": "Sesión cerrada correctamente"}


# We will define a helper that decodes the token
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de sesión ha expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de sesión inválido"
        )

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.get("/drive-status")
def drive_status():
    """Verifica si el token de Google Drive está autorizado y activo en el servidor."""
    import os
    from config.auth import TOKEN_PATH
    from google.oauth2.credentials import Credentials
    from config.auth import SCOPES
    from google.auth.transport.requests import Request

    if not os.path.exists(TOKEN_PATH):
        return {"connected": False, "reason": "no_token"}

    try:
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if creds and creds.valid:
            return {"connected": True}
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                return {"connected": True}
            except Exception:
                return {"connected": False, "reason": "token_expired"}
        return {"connected": False, "reason": "token_invalid"}
    except Exception as e:
        return {"connected": False, "reason": str(e)}

