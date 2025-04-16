from sqlalchemy import String, Integer, Column, ForeignKey, DateTime
from conexion import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class RegistrarProducto(Base):
    __tablename__ = "productos"
    codigo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    precio = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    descripcion = Column(String(150), nullable=False)
    imagen = Column(String(length=255))

class RegistroCliente(Base):
    __tablename__ = "clientes"
    documento = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    correo = Column(String(50), nullable=True)
    celular = Column(Integer, nullable=True )
    nombre_tienda = Column(String(50), nullable=False)

class RegistroUsuario(Base):
    __tablename__ = "usuarios"
    documento = Column(Integer, ForeignKey('clientes.documento'), primary_key=True, index=True)
    cliente = relationship("RegistroCliente")
    nombre_usuario = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)

class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    fecha_compra = Column(DateTime, default=datetime.utcnow, nullable=False)
    cliente_documento = Column(Integer, ForeignKey('clientes.documento'))
    cliente = relationship("RegistroCliente", backref="compras")
    total = Column(Integer, nullable=False)

class DetalleCompra(Base):
    __tablename__ = "detalle_compras"
    id = Column(Integer, primary_key=True, index=True)
    compra_id = Column(Integer, ForeignKey('compras.id'))
    producto_codigo = Column(Integer, ForeignKey('productos.codigo'))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Integer, nullable=False)
    subtotal = Column(Integer, nullable=False)

    compra = relationship("Compra", backref="detalle_compras")
    producto = relationship("RegistrarProducto", backref="detalle_compras")
