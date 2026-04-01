from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ── 1. Configurar la base de datos ────────────────────────────────
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

# ── Endpoints Productos ───────────────────────────────────────────
@app.get("/productos")
def listar(db: Session = Depends(get_db)):
    return db.query(Producto).all()

@app.post("/productos")
def crear(producto: ProductoSchema, db: Session = Depends(get_db)):
    nuevo = Producto(
        sku=producto.sku, nombre=producto.nombre,
        categoria=producto.categoria, proveedor=producto.proveedor,
        precio=producto.precio, stock=producto.stock,
        marca=producto.marca, foto_url=producto.foto_url
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# ── Endpoints Almacenes ───────────────────────────────────────────
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

# ── Endpoints Transferencias ──────────────────────────────────────
@app.post("/transferencias")
def crear_transferencia(t: TransferenciaSchema, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == t.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if producto.stock < t.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente en bodega")
    
    producto.stock -= t.cantidad

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
    inventarios = db.query(InventarioAlmacen).filter(
        InventarioAlmacen.almacen_id == almacen_id
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
                "stock": inv.stock
            })
    return resultado