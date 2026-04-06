from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ── 1. Base de datos ──────────────────────────────────────────────
engine = create_engine("postgresql://postgres.thcdadlejpdhaaekyost:Kardex2026App@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ── 2. Modelos ────────────────────────────────────────────────────
class Producto(Base):
    __tablename__ = "productos"
    id             = Column(Integer, primary_key=True)
    sku            = Column(String, unique=True)
    nombre         = Column(String)
    categoria      = Column(String)
    proveedor      = Column(String)
    precio         = Column(Float)
    stock          = Column(Float)
    foto_url       = Column(String, nullable=True)
    marca          = Column(String, nullable=True)
    genero         = Column(String, nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

class Almacen(Base):
    __tablename__ = "almacenes"
    id             = Column(Integer, primary_key=True)
    nombre         = Column(String, nullable=False)
    direccion      = Column(String, nullable=True)
    ciudad         = Column(String, nullable=True)
    responsable    = Column(String, nullable=True)
    estado         = Column(String, default="activo")
    fecha_registro = Column(DateTime, default=datetime.utcnow)

class InventarioAlmacen(Base):
    __tablename__ = "inventario_almacen"
    id          = Column(Integer, primary_key=True)
    almacen_id  = Column(Integer)
    producto_id = Column(Integer)
    stock       = Column(Float, default=0)

class ProductoTalla(Base):
    __tablename__ = "producto_tallas"
    id          = Column(Integer, primary_key=True)
    producto_id = Column(Integer)
    genero      = Column(String)
    talla       = Column(String)
    unidades    = Column(Integer, default=0)

class Transferencia(Base):
    __tablename__ = "transferencias"
    id          = Column(Integer, primary_key=True)
    producto_id = Column(Integer)
    almacen_id  = Column(Integer)
    cantidad    = Column(Float)
    fecha       = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ── 3. Schemas ────────────────────────────────────────────────────
class ProductoSchema(BaseModel):
    sku:       str
    nombre:    str
    categoria: str
    proveedor: str
    precio:    float
    stock:     float
    foto_url:  Optional[str] = None
    marca:     Optional[str] = None
    genero:    Optional[str] = None

class AlmacenSchema(BaseModel):
    nombre:      str
    direccion:   Optional[str] = None
    ciudad:      Optional[str] = None
    responsable: Optional[str] = None
    estado:      Optional[str] = "activo"

class TransferenciaSchema(BaseModel):
    producto_id: int
    almacen_id:  int
    cantidad:    float
    cantidad:    float
    talla:       str
    genero:      str

class ProductoTallaSchema(BaseModel):
    producto_id: int
    genero:      str
    talla:       str
    unidades:    int

class InventarioAlmacenTalla(Base):
    __tablename__ = "inventario_almacen_tallas"
    id          = Column(Integer, primary_key=True)
    almacen_id  = Column(Integer)
    producto_id = Column(Integer)
    talla       = Column(String)
    genero      = Column(String)
    unidades    = Column(Integer, default=0)



# ── 4. Sesión ─────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── 5. App ────────────────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Productos ─────────────────────────────────────────────────────
@app.get("/productos")
def listar(db: Session = Depends(get_db)):
    return db.query(Producto).all()

@app.post("/productos")
def crear(producto: ProductoSchema, db: Session = Depends(get_db)):
    nuevo = Producto(
        sku=producto.sku, nombre=producto.nombre,
        categoria=producto.categoria, proveedor=producto.proveedor,
        precio=producto.precio, stock=producto.stock,
        marca=producto.marca, foto_url=producto.foto_url,
        genero=producto.genero
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# ── Almacenes ─────────────────────────────────────────────────────
@app.get("/almacenes")
def listar_almacenes(db: Session = Depends(get_db)):
    return db.query(Almacen).all()

@app.post("/almacenes")
def crear_almacen(almacen: AlmacenSchema, db: Session = Depends(get_db)):
    nuevo = Almacen(
        nombre=almacen.nombre, direccion=almacen.direccion,
        ciudad=almacen.ciudad, responsable=almacen.responsable,
        estado=almacen.estado
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# ── Transferencias ────────────────────────────────────────────────


@app.post("/transferencias")
def crear_transferencia(t: TransferenciaSchema, db: Session = Depends(get_db)):
    # Verificar producto
    producto = db.query(Producto).filter(Producto.id == t.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Verificar stock en talla específica
    talla_prod = db.query(ProductoTalla).filter(
        ProductoTalla.producto_id == t.producto_id,
        ProductoTalla.talla == t.talla
    ).first()
    if not talla_prod or talla_prod.unidades < t.cantidad:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente en talla {t.talla}")

    # Restar de producto_tallas (bodega)
    talla_prod.unidades -= int(t.cantidad)
    producto.stock -= t.cantidad

    # Actualizar inventario_almacen (total)
    inventario = db.query(InventarioAlmacen).filter(
        InventarioAlmacen.almacen_id == t.almacen_id,
        InventarioAlmacen.producto_id == t.producto_id
    ).first()
    if inventario:
        inventario.stock += t.cantidad
    else:
        inventario = InventarioAlmacen(
            almacen_id=t.almacen_id,
            producto_id=t.producto_id,
            stock=t.cantidad
        )
        db.add(inventario)

    # Actualizar inventario_almacen_tallas
    inv_talla = db.query(InventarioAlmacenTalla).filter(
        InventarioAlmacenTalla.almacen_id == t.almacen_id,
        InventarioAlmacenTalla.producto_id == t.producto_id,
        InventarioAlmacenTalla.talla == t.talla
    ).first()
    if inv_talla:
        inv_talla.unidades += int(t.cantidad)
    else:
        inv_talla = InventarioAlmacenTalla(
            almacen_id=t.almacen_id,
            producto_id=t.producto_id,
            talla=t.talla,
            genero=t.genero,
            unidades=int(t.cantidad)
        )
        db.add(inv_talla)

    # Guardar transferencia
    nueva = Transferencia(
        producto_id=t.producto_id,
        almacen_id=t.almacen_id,
        cantidad=t.cantidad
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

# ── Inventario por almacén ────────────────────────────────────────
@app.get("/almacenes/{almacen_id}/inventario")
def inventario_almacen(almacen_id: int, db: Session = Depends(get_db)):
    inventarios = db.query(InventarioAlmacenTalla).filter(
        InventarioAlmacenTalla.almacen_id == almacen_id,
        InventarioAlmacenTalla.unidades > 0
    ).all()
    resultado = []
    for inv in inventarios:
        producto = db.query(Producto).filter(Producto.id == inv.producto_id).first()
        if producto:
            resultado.append({
                "id": producto.id,
                "sku": producto.sku,
                "nombre": producto.nombre,
                "categoria": producto.categoria,
                "proveedor": producto.proveedor,
                "marca": producto.marca,
                "precio": producto.precio,
                "foto_url": producto.foto_url,
                "stock": inv.unidades,
                "talla": inv.talla,
                "genero": inv.genero
            })
    return resultado
# un end point para obtener las tallas ----


@app.get("/productos/{producto_id}/tallas")
def obtener_tallas(producto_id: int, db: Session = Depends(get_db)):
    tallas = db.query(ProductoTalla).filter(
        ProductoTalla.producto_id == producto_id
    ).all()
    return tallas

# ── Tallas ────────────────────────────────────────────────────────

@app.post("/producto-tallas")
def crear_tallas(tallas: list[ProductoTallaSchema], db: Session = Depends(get_db)):
    for t in tallas:
        nueva = ProductoTalla(
            producto_id=t.producto_id,
            genero=t.genero,
            talla=t.talla,
            unidades=t.unidades
        )
        db.add(nueva)
    db.commit()
    return {"mensaje": "Tallas guardadas"}


# ── Ventas ────────────────────────────────────────────────────────
class Venta(Base):
    __tablename__ = "ventas"
    id          = Column(Integer, primary_key=True)
    almacen_id  = Column(Integer)
    metodo_pago = Column(String)
    total       = Column(Float)
    fecha       = Column(DateTime, default=datetime.utcnow)

class DetalleVenta(Base):
    __tablename__ = "detalle_ventas"
    id              = Column(Integer, primary_key=True)
    venta_id        = Column(Integer)
    producto_id     = Column(Integer)
    talla           = Column(String)
    cantidad        = Column(Integer)
    precio_unitario = Column(Float)

class DetalleVentaSchema(BaseModel):
    producto_id:     int
    talla:           str
    cantidad:        int
    precio_unitario: float

class VentaSchema(BaseModel):
    almacen_id:  int
    metodo_pago: str
    total:       float
    detalle:     list[DetalleVentaSchema]

@app.post("/ventas")
def crear_venta(venta: VentaSchema, db: Session = Depends(get_db)):
    # Verificar stock en inventario_almacen para cada item
    for item in venta.detalle:
        inv = db.query(InventarioAlmacen).filter(
            InventarioAlmacen.almacen_id == venta.almacen_id,
            InventarioAlmacen.producto_id == item.producto_id
        ).first()
        if not inv or inv.stock < item.cantidad:
            producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {producto.nombre} talla {item.talla}"
            )

    # Crear venta
    nueva_venta = Venta(
        almacen_id=venta.almacen_id,
        metodo_pago=venta.metodo_pago,
        total=venta.total
    )
    db.add(nueva_venta)
    db.flush()

    # Crear detalle y descontar stock
    for item in venta.detalle:
        detalle = DetalleVenta(
            venta_id=nueva_venta.id,
            producto_id=item.producto_id,
            talla=item.talla,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario
        )
        db.add(detalle)

        # Descontar del inventario_almacen
        inv = db.query(InventarioAlmacen).filter(
            InventarioAlmacen.almacen_id == venta.almacen_id,
            InventarioAlmacen.producto_id == item.producto_id
        ).first()
        inv.stock -= item.cantidad

    db.commit()
    db.refresh(nueva_venta)
    return nueva_venta

@app.get("/ventas")
def listar_ventas(db: Session = Depends(get_db)):
    return db.query(Venta).order_by(Venta.fecha.desc()).all()

