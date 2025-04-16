import bcrypt
from typing import List
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from conexion import crear, get_bd
from modelo import Base, RegistrarProducto, RegistroCliente, RegistroUsuario, Compra, DetalleCompra
from shemas import ProductoBase as pro
from shemas import Cliente as cli
from shemas import Usuario as usu
from shemas import UsuarioCreate as usuC
from sqlalchemy import func
from shemas import Login
from shemas import CompraCreate 
from shemas import CompraSinDetalles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from auth import crear_token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/compras", response_model=List[CompraSinDetalles])
def listar_compras(db: Session = Depends(get_bd)):
    compras = db.query(Compra).all()
    return compras

Base.metadata.create_all(bind=crear)
UPLOAD_FOLDER = "img"

# Crear la carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Servir archivos estáticos desde la carpeta "img"
app.mount("/img", StaticFiles(directory=UPLOAD_FOLDER), name="img")

@app.post("/insertar")
async def registrar_producto(
    codigo: int = Form(...),
    nombre: str = Form(...),
    precio: int = Form(...),
    cantidad: int = Form(...),
    descripcion: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_bd)
):
    # Validar el tipo de archivo
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado")

    # Generar nombre único para la imagen (para evitar conflictos)
    filename = f"{codigo}_{file.filename}"
    file_location = os.path.join(UPLOAD_FOLDER, filename)

    # Guardar el archivo en disco
    try:
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {str(e)}")

    # Generar URL accesible públicamente
    imagen_url = f"http://127.0.0.1:8000/img/{filename}"

    # Registrar producto en base de datos
    try:
        producto_data = RegistrarProducto(
            codigo=codigo,
            nombre=nombre,
            precio=precio,
            cantidad=cantidad,
            descripcion=descripcion,
            imagen=imagen_url
        )
        db.add(producto_data)
        db.commit()
        db.refresh(producto_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar producto: {str(e)}")

    return {"message": "Producto registrado correctamente", "data": producto_data}

@app.get("/consultaproductos")
def consultar_productos(db: Session = Depends(get_bd)):
    productos = db.query(RegistrarProducto).all()
    return [
        {
            "codigo": p.codigo,
            "nombre": p.nombre,
            "precio": p.precio,
            "cantidad": p.cantidad,
            "descripcion": p.descripcion,
            "imagenUrl": p.imagen  # URL completa ya guardada
        }
        for p in productos
    ]

@app.get("/consultaproductos", response_model=List[pro])
async def consultar_productos(request: Request, db: Session = Depends(get_bd)):
    base_url = str(request.base_url)
    datos_producto = db.query(RegistrarProducto).all()

    for producto in datos_producto:
        if producto.imagen and not producto.imagen.startswith("http"):
            imagen_url = producto.imagen.replace('\\', '/')
            producto.imagen = f"{base_url}{imagen_url}"
    return datos_producto

@app.get("/consultaclientes", response_model=list[cli])
async def consultar_clientes(db: Session = Depends(get_bd)):
    datos_cliente = db.query(RegistroCliente).all()
    return datos_cliente

@app.get("/clientes/documento/", response_model=list[int])
async def documentosClientes(db: Session = Depends(get_bd)):
    documentos = db.query(RegistroCliente.documento).all()
    return [doc[0] for doc in documentos]

@app.post("/registrarCliente", response_model=cli)
async def registrar_cliente(clientemodel: cli, db: Session = Depends(get_bd)):
    datos = RegistroCliente(**clientemodel.dict())
    db.add(datos)
    db.commit()
    db.refresh(datos)
    return datos

@app.post("/registrousuario")
async def registrar_usuario(user: usuC, db: Session = Depends(get_bd)):
    # Verifica si el nombre de usuario ya existe
    nombre_user = db.query(RegistroUsuario).filter(RegistroUsuario.nombre_usuario == user.nombre_usuario).first()
    if nombre_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    
    # Verifica si las contraseñas coinciden
    if user.password != user.confirmar_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")
    
    # Encriptación de la contraseña
    encriptacion = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    nuevo_user = RegistroUsuario(
        documento=user.documento,
        nombre_usuario=user.nombre_usuario,
        password=encriptacion.decode('utf-8')
    )
    
    db.add(nuevo_user)
    db.commit()
    db.refresh(nuevo_user)
    
    return {"documento": nuevo_user.documento, "nombre": nuevo_user.nombre_usuario}

@app.post("/login")
async def login(user: Login, db: Session = Depends(get_bd)):
    db_user = db.query(RegistroUsuario).filter(RegistroUsuario.nombre_usuario == user.nombre_usuario).first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="Usuario no existe")
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    token_data = {"sub": db_user.nombre_usuario}
    access_token = crear_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "nombreUsuario": db_user.nombre_usuario,
        "clienteDocumento": db_user.documento  # ✅ Asegúrate de que el campo se llame así
    }

@app.post("/finalizarCompras")
async def crear_compra(compra: CompraCreate, request: Request, db: Session = Depends(get_bd)):
    body = await request.json()
    print("🟡 JSON recibido:", body)
    print("✅ Objeto validado:", compra)

    nueva_compra = Compra(
        fecha_compra=datetime.now(),
        cliente_documento=compra.cliente_documento,
        total=compra.total
    )
    db.add(nueva_compra)
    db.commit()
    db.refresh(nueva_compra)

    for detalle in compra.detalles:
        # Buscar producto en la base de datos
        producto = db.query(RegistrarProducto).filter(RegistrarProducto.codigo == detalle.producto_codigo).first()

        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto con código {detalle.producto_codigo} no encontrado")

        if producto.cantidad < detalle.cantidad:
            raise HTTPException(status_code=400, detail=f"No hay suficiente inventario para el producto {producto.codigo}")

        # Restar inventario
        producto.cantidad -= detalle.cantidad
        db.add(producto)  # 👈 Esto asegura que SQLAlchemy actualice el producto

        # Crear detalle de compra
        nuevo_detalle = DetalleCompra(
            compra_id=nueva_compra.id,
            producto_codigo=detalle.producto_codigo,
            cantidad=detalle.cantidad,
            precio_unitario=detalle.precio_unitario,
            subtotal=detalle.subtotal
        )
        db.add(nuevo_detalle)

    db.commit()

    return {
        "mensaje": "Compra registrada correctamente",
        "id_compra": nueva_compra.id
    }

@app.delete("/eliminarProducto/{producto_codigo}", response_model=pro)
async def eliminar_producto(producto_codigo: int, db: Session = Depends(get_bd)):
    producto = db.query(RegistrarProducto).filter(RegistrarProducto.codigo == producto_codigo).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(producto)
    db.commit()
    return producto

@app.put("/actualizarProducto/{producto_codigo}", response_model=pro)
async def actualizar_producto(producto_codigo: int, productomodel: pro, db: Session = Depends(get_bd)):
    producto = db.query(RegistrarProducto).filter(RegistrarProducto.codigo == producto_codigo).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    for key, value in productomodel.dict().items():
        setattr(producto, key, value)
    
    db.commit()
    db.refresh(producto)
    return producto

@app.get("/productos-mas-vendidos")
def productos_mas_vendidos(db: Session = Depends(get_bd)):
    resultados = (
        db.query(
            RegistrarProducto.nombre.label("nombre"),
            func.sum(DetalleCompra.cantidad).label("total_vendido")
        )
        .join(DetalleCompra, RegistrarProducto.codigo == DetalleCompra.producto_codigo)
        .group_by(RegistrarProducto.codigo, RegistrarProducto.nombre)
        .order_by(func.sum(DetalleCompra.cantidad).desc())
        .all()
    )

    return [
        {"nombre": r.nombre, "total_vendido": r.total_vendido}
        for r in resultados
    ]

@app.get("/")
def home():
    return {"mensaje": "Bienvenido a la API de productos"}