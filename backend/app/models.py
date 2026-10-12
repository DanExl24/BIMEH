from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class KPIData(BaseModel):
    fecha: str
    total_personal: int
    disponibles: int
    novedades: int
    disponibilidad: float
    cambios_vs_ayer: int

class AlertaFatigaItem(BaseModel):
    id_personal: int
    cedula: int
    nombre: str
    dias_continuos: int
    estado_actual: str
    nivel_alerta: str  # MODERADO, ALTO, CRITICO
    recomendacion: str

class AlertaSanidadItem(BaseModel):
    id_personal: int
    cedula: int
    nombre: str
    total_dias_sanidad: int
    episodios: int
    novedades: str
    ultima_fecha: str
    clasificacion: str  # JUNTA_MEDICA_SUGERIDA, SEGUIMIENTO_SANIDAD
    recomendacion: str

class ProyeccionHorizonte(BaseModel):
    estimados_disponibles: int
    porcentaje: float
    reincorporaciones: int
    salidas_programadas: int

class ProyeccionMovimiento(BaseModel):
    id_personal: int
    cedula: int
    nombre: str
    novedad: str
    fecha_fin: str
    dias_restantes: int
    descripcion: Optional[str] = None

class ProyeccionFuerzaData(BaseModel):
    fecha_base: str
    efectivo_actual: Dict[str, Any]
    proyeccion_7_dias: ProyeccionHorizonte
    proyeccion_15_dias: ProyeccionHorizonte
    proyeccion_30_dias: ProyeccionHorizonte
    detalle_movimientos: List[ProyeccionMovimiento]

class ParteDiarioData(BaseModel):
    fecha: str
    total_personal: int
    disponibles: int
    novedades: int
    porcentaje_disponibilidad: float
    disposicion: Dict[str, int]
    desglose_categorias: Dict[str, int]
    desglose_subnovedades: List[Dict[str, Any]]
    alertas_resumen: Dict[str, Any]
    radiograma_texto: str
