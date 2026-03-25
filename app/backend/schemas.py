from pydantic import BaseModel, Field
from typing import List

class Apartado(BaseModel):
    titulo: str = Field(...,  description="Título del capítulo, por ejemplo: '1. Objeto del Contrato'")
    descripcion: str = Field(..., description="Detalle de los puntos técnicos que debe cubrir este apartado")

class PliegoAnalisis(BaseModel):
    titulo: str = Field(..., description="Título general del pliego de prescripciones técnicas")
    resumen_proyecto: str = Field(..., description="Resumen ejecutivo del proyecto de licitación")
    apartados: List[Apartado] = Field(..., min_items=1, max_items=4, description="Lista de los apartados técnicos estructurados")