from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Producto
from schemas import ProductoSchema

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.post("/")
def crear_producto(producto: ProductoSchema, db: Session = Depends(get_db)):
    nuevo = Producto(nombre=producto.nombre, stock=producto.stock)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo