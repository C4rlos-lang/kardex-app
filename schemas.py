from pydantic import BaseModel

class ProductoSchema(BaseModel):
    sku:        str
    nombre:     str
    categoria:  str
    proveedor:  str
    precio:     float
    stock:      float
    foto_url:   str = None