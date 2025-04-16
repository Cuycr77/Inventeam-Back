from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional
from datetime import datetime

# ------------------------
# PRODUCTO
# ------------------------

class ProductoBase(BaseModel):
    codigo: int
    nombre: str
    precio: int
    cantidad: int
    descripcion: Optional[str] = None
    imagen: Optional[str] = None

    class Config:
        orm_mode = True

class ProductoCreate(BaseModel):
    nombre: str
    precio: int
    cantidad: int
    descripcion: Optional[str] = None
    imagen: Optional[str] = None

    class Config:
        orm_mode = True

class Producto(ProductoBase):
    pass

# ------------------------
# CLIENTE
# ------------------------

class ClienteBase(BaseModel):
    documento: int
    nombre: str
    apellido: str
    correo: Optional[EmailStr] = None
    celular: Optional[int] = None
    nombre_tienda: Optional[str] = None

    class Config:
        orm_mode = True

class ClienteCreate(ClienteBase):
    pass

class Cliente(ClienteBase):
    pass

# ------------------------
# USUARIO
# ------------------------

class UsuarioBase(BaseModel):
    documento: int
    nombre_usuario: str

    class Config:
        orm_mode = True

class UsuarioCreate(UsuarioBase):
    password: str
    confirmar_password: str

    @validator('confirmar_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

class Usuario(UsuarioBase):
    pass

class Login(BaseModel):
    nombre_usuario: str
    password: str

# ------------------------
# COMPRA Y DETALLE COMPRA
# ------------------------

# Detalle de la compra base
class DetalleCompraBase(BaseModel):
    producto_codigo: int
    cantidad: int
    precio_unitario: float
    subtotal: float

# Modelo base común para Compra (sin detalles)
class CompraBase(BaseModel):
    id: Optional[int] = None
    fecha_compra: Optional[datetime] = None
    cliente_documento: int
    total: float

# Para registrar una compra (por ejemplo, en el carrito)
class CompraCreate(CompraBase):
    detalles: List[DetalleCompraBase]

# Para registrar una compra sin detalles (por ejemplo, en registroCompras)
class CompraSinDetalles(CompraBase):
    pass
