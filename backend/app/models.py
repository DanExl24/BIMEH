from pydantic import BaseModel

class KPIData(BaseModel):
    fecha: str
    total_personal: int
    disponibles: int
    novedades: int
    disponibilidad: float
    cambios_vs_ayer: int
