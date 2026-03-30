from database import Base
from sqlalchemy import Column, Integer, String, Float

class Producto(Base):
    __tablename__ = "productos"
    id     = Column(Integer, primary_key=True)
    nombre = Column(String)
    stock  = Column(Float)