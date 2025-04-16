from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from auth import verificar_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    user_data = verificar_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    return user_data  # Devuelve payload (ej: {"sub": "nombre_usuario", "id": 1})
