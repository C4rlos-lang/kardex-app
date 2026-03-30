from pydantic import BaseModel

class ProductoSchema(BaseModel):
    nombre: str
    stock: float