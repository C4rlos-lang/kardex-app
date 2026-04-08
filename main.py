from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator

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

class InventarioAlmacenTalla(Base):
    __tablename__ = "inventario_almacen_tallas"
    id          = Column(Integer, primary_key=True)
    almacen_id  = Column(Integer)
    producto_id = Column(Integer)
    talla       = Column(String)
    genero      = Column(String)
    unidades    = Column(Integer, default=0)

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

class Venta(Base):
    __tablename__ = "ventas"
    id          = Column(Integer, primary_key=True)
    almacen_id  = Column(Integer)
    metodo_pago = Column(String)
    total       = Column(Float)
    cliente_id  = Column(Integer, nullable=True)  # ← agrega esta línea
    fecha       = Column(DateTime, default=datetime.utcnow)

class DetalleVenta(Base):
    __tablename__ = "detalle_ventas"
    id              = Column(Integer, primary_key=True)
    venta_id        = Column(Integer)
    producto_id     = Column(Integer)
    talla           = Column(String)
    cantidad        = Column(Integer)
    precio_unitario = Column(Float)

Base.metadata.create_all(bind=engine)

class Cliente(Base):
    __tablename__ = "clientes"
    id             = Column(Integer, primary_key=True)
    nombre         = Column(String, nullable=True)
    telefono       = Column(String, nullable=True)
    correo         = Column(String, nullable=True)
    genero         = Column(String, nullable=True)
    documento      = Column(String, nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

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
    talla:       str
    genero:      str

class ProductoTallaSchema(BaseModel):
    producto_id: int
    genero:      str
    talla:       str
    unidades:    int

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
    cliente:     Optional[ClienteSchema] = None  # ← ¿está esta línea?

class ClienteSchema(BaseModel):
    nombre:    Optional[str] = None
    telefono:  Optional[str] = None
    correo:    Optional[str] = None
    genero:    Optional[str] = None
    documento: Optional[str] = None

    @field_validator('correo')
    @classmethod
    def validar_correo(cls, v):
        if v and '@' not in v:
            raise ValueError('El correo no es válido')
        return v



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

@app.get("/productos/{producto_id}/tallas")
def obtener_tallas(producto_id: int, db: Session = Depends(get_db)):
    return db.query(ProductoTalla).filter(
        ProductoTalla.producto_id == producto_id
    ).all()

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

@app.get("/almacenes/{almacen_id}/productos/{producto_id}/tallas")
def tallas_almacen(almacen_id: int, producto_id: int, db: Session = Depends(get_db)):
    return db.query(InventarioAlmacenTalla).filter(
        InventarioAlmacenTalla.almacen_id == almacen_id,
        InventarioAlmacenTalla.producto_id == producto_id,
        InventarioAlmacenTalla.unidades > 0
    ).all()

# ── Transferencias ────────────────────────────────────────────────
@app.post("/transferencias")
def crear_transferencia(t: TransferenciaSchema, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == t.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    talla_prod = db.query(ProductoTalla).filter(
        ProductoTalla.producto_id == t.producto_id,
        ProductoTalla.talla == t.talla
    ).first()
    if not talla_prod or talla_prod.unidades < t.cantidad:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente en talla {t.talla}")

    talla_prod.unidades -= int(t.cantidad)
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

    nueva = Transferencia(
        producto_id=t.producto_id,
        almacen_id=t.almacen_id,
        cantidad=t.cantidad
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

# ── Ventas ────────────────────────────────────────────────────────
@app.post("/ventas")
def crear_venta(venta: VentaSchema, db: Session = Depends(get_db)):
    # Guardar cliente si viene info
    cliente_id = None
    if venta.cliente and venta.cliente.nombre:
        nuevo_cliente = Cliente(
            nombre=venta.cliente.nombre,
            telefono=venta.cliente.telefono,
            correo=venta.cliente.correo,
            genero=venta.cliente.genero,
            documento=venta.cliente.documento
        )
        db.add(nuevo_cliente)
        db.flush()
        cliente_id = nuevo_cliente.id

    # Verificar stock
    for item in venta.detalle:
        inv_talla = db.query(InventarioAlmacenTalla).filter(
            InventarioAlmacenTalla.almacen_id == venta.almacen_id,
            InventarioAlmacenTalla.producto_id == item.producto_id,
            InventarioAlmacenTalla.talla == item.talla
        ).first()
        if not inv_talla or inv_talla.unidades < item.cantidad:
            producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {producto.nombre} talla {item.talla}"
            )

    # Crear venta
    nueva_venta = Venta(
        almacen_id=venta.almacen_id,
        metodo_pago=venta.metodo_pago,
        total=venta.total,
        cliente_id=cliente_id
    )
    db.add(nueva_venta)
    db.flush()

    # Detalle y descuento
    for item in venta.detalle:
        db.add(DetalleVenta(
            venta_id=nueva_venta.id,
            producto_id=item.producto_id,
            talla=item.talla,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario
        ))
        inv_talla = db.query(InventarioAlmacenTalla).filter(
            InventarioAlmacenTalla.almacen_id == venta.almacen_id,
            InventarioAlmacenTalla.producto_id == item.producto_id,
            InventarioAlmacenTalla.talla == item.talla
        ).first()
        inv_talla.unidades -= item.cantidad

        inv = db.query(InventarioAlmacen).filter(
            InventarioAlmacen.almacen_id == venta.almacen_id,
            InventarioAlmacen.producto_id == item.producto_id
        ).first()
        if inv:
            inv.stock -= item.cantidad

    db.commit()
    db.refresh(nueva_venta)
    return nueva_venta

@app.get("/ventas")
def listar_ventas(db: Session = Depends(get_db)):
    return db.query(Venta).order_by(Venta.fecha.desc()).all()

# ── Dashboard ─────────────────────────────────────────────────────
from sqlalchemy import func, extract

@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    from datetime import date
    hoy = datetime.utcnow()
    mes_actual = hoy.month
    anio_actual = hoy.year

    # ── TENDENCIAS ────────────────────────────────────────────────
    # Producto más vendido
    producto_top = db.query(
        DetalleVenta.producto_id,
        func.sum(DetalleVenta.cantidad).label("total")
    ).group_by(DetalleVenta.producto_id).order_by(func.sum(DetalleVenta.cantidad).desc()).first()

    nombre_producto_top = None
    if producto_top:
        p = db.query(Producto).filter(Producto.id == producto_top.producto_id).first()
        nombre_producto_top = p.nombre if p else None

    # Talla más vendida
    talla_top = db.query(
        DetalleVenta.talla,
        func.sum(DetalleVenta.cantidad).label("total")
    ).group_by(DetalleVenta.talla).order_by(func.sum(DetalleVenta.cantidad).desc()).first()

    # Ventas por mes
    ventas_por_mes = db.query(
        extract('month', Venta.fecha).label("mes"),
        func.sum(Venta.total).label("total")
    ).group_by(extract('month', Venta.fecha)).order_by(extract('month', Venta.fecha)).all()

    # Ventas por día de la semana
    ventas_por_dia = db.query(
        extract('dow', Venta.fecha).label("dia"),
        func.count(Venta.id).label("total")
    ).group_by(extract('dow', Venta.fecha)).order_by(extract('dow', Venta.fecha)).all()

    # Ventas por semana del año
    ventas_por_semana = db.query(
        extract('week', Venta.fecha).label("semana"),
        func.sum(Venta.total).label("total")
    ).group_by(extract('week', Venta.fecha)).order_by(extract('week', Venta.fecha)).all()

    # ── INVENTARIO ────────────────────────────────────────────────
    total_productos = db.query(func.count(Producto.id)).scalar()
    stock_bajo = db.query(func.count(Producto.id)).filter(Producto.stock < 5).scalar()

    # ── CLIENTES ──────────────────────────────────────────────────
    total_clientes = db.query(func.count(Cliente.id)).scalar()

    genero_top = db.query(
        Cliente.genero,
        func.count(Cliente.id).label("total")
    ).filter(Cliente.genero != None, Cliente.genero != '').group_by(Cliente.genero).order_by(func.count(Cliente.id).desc()).first()

    clientes_nuevos_mes = db.query(func.count(Cliente.id)).filter(
        extract('month', Cliente.fecha_registro) == mes_actual,
        extract('year', Cliente.fecha_registro) == anio_actual
    ).scalar()

    # Recurrencia — clientes con más de 1 compra
    recurrencia = db.query(
        Venta.cliente_id,
        func.count(Venta.id).label("compras")
    ).filter(Venta.cliente_id != None).group_by(Venta.cliente_id).order_by(func.count(Venta.id).desc()).all()

    clientes_recurrentes = len([r for r in recurrencia if r.compras > 1])
    promedio_compras = round(sum(r.compras for r in recurrencia) / len(recurrencia), 1) if recurrencia else 0

    # ── FINANCIERO ────────────────────────────────────────────────
    ventas_mes = db.query(func.sum(Venta.total)).filter(
        extract('month', Venta.fecha) == mes_actual,
        extract('year', Venta.fecha) == anio_actual
    ).scalar() or 0

    metodo_top = db.query(
        Venta.metodo_pago,
        func.count(Venta.id).label("total")
    ).group_by(Venta.metodo_pago).order_by(func.count(Venta.id).desc()).first()

    total_ventas = db.query(func.count(Venta.id)).scalar()
    total_ingresos = db.query(func.sum(Venta.total)).scalar() or 0
    ticket_promedio = round(total_ingresos / total_ventas, 0) if total_ventas else 0

    return {
        "tendencias": {
            "producto_top": nombre_producto_top,
            "talla_top": talla_top.talla if talla_top else None,
            "ventas_por_mes": [{"mes": int(v.mes), "total": float(v.total)} for v in ventas_por_mes],
            "ventas_por_dia": [{"dia": int(v.dia), "total": int(v.total)} for v in ventas_por_dia],
            "ventas_por_semana": [{"semana": int(v.semana), "total": float(v.total)} for v in ventas_por_semana],
        },
        "inventario": {
            "total_productos": total_productos,
            "stock_bajo": stock_bajo,
        },
        "clientes": {
            "total_clientes": total_clientes,
            "genero_top": genero_top.genero if genero_top else None,
            "clientes_nuevos_mes": clientes_nuevos_mes,
            "clientes_recurrentes": clientes_recurrentes,
            "promedio_compras": promedio_compras,
        },
        "financiero": {
            "ventas_mes": round(ventas_mes, 0),
            "metodo_top": metodo_top.metodo_pago if metodo_top else None,
            "ticket_promedio": ticket_promedio,
            "total_ventas": total_ventas,
        }
    }

