from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware  # ← agrega esto
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# ── 1. Configurar la base de datos ────────────────────────────────
engine = create_engine("postgresql://postgres.thcdadlejpdhaaekyost:Kardex2026App@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ── 2. Definir la tabla ───────────────────────────────────────────
class Producto(Base):
    __tablename__ = "productos"
    id          = Column(Integer, primary_key=True)
    sku         = Column(String, unique=True)
    nombre      = Column(String)
    categoria   = Column(String)
    proveedor   = Column(String)
    precio      = Column(Float)
    stock       = Column(Float)
    foto_url    = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

# ── 3. Schema ─────────────────────────────────────────────────────
# ── 3. Schema ─────────────────────────────────────────────────────
class ProductoSchema(BaseModel):
    sku:       str
    nombre:    str
    categoria: str
    proveedor: str
    precio:    float
    stock:     float
    foto_url:  str = None

# ── 4. Sesión de base de datos ────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── 5. App y endpoints ────────────────────────────────────────────
app = FastAPI()

# ── CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/productos")
def listar(db: Session = Depends(get_db)):
    return db.query(Producto).all()
@app.post("/productos")
def crear(producto: ProductoSchema, db: Session = Depends(get_db)):
    nuevo = Producto(
        sku=producto.sku,
        nombre=producto.nombre,
        categoria=producto.categoria,
        proveedor=producto.proveedor,
        precio=producto.precio,
        stock=producto.stock,
        foto_url=producto.foto_url
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo