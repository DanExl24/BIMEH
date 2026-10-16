"""
Clases base y contratos para las habilidades modulares (Skills) del Asistente IA.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from app.ia.nlp.normalizer import _norm
from app.ia.nlp.date_extractor import (
    _extract_month, _extract_year, _extract_day_range, _extract_month_name,
    _extract_month_range, _extract_date_range, _last_day_of_month
)
from app.ia.nlp.militar_matcher import _extract_novedad_type, _extract_cedula, _extract_subnovedad_oficial, _is_least_frequent

@dataclass
class QueryContext:
    """Contenedor de información contextual preprocesada para el despacho de skills."""
    user_message: str
    active_militar: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    current_year: int = 2026
    db: Optional[Any] = None
    history: Optional[List[Dict[str, Any]]] = None

    # Propiedades calculadas
    msg_norm: str = field(init=False)
    cedula_en_msg: Optional[str] = field(init=False)
    mes_num: Optional[int] = field(init=False)
    mes_nom: Optional[str] = field(init=False)
    month_range: Optional[Tuple[int, int]] = field(init=False)
    date_range: Optional[Tuple[str, str]] = field(init=False)
    is_range: bool = field(init=False)
    range_label: Optional[str] = field(init=False)
    anio: int = field(init=False)
    day_range: Optional[Tuple[int, int]] = field(init=False)
    novedad_type: Optional[str] = field(init=False)
    subnovedad_oficial: Optional[str] = field(init=False)
    is_least: bool = field(init=False)

    def __post_init__(self):
        self.msg_norm = _norm(self.user_message)
        self.cedula_en_msg = _extract_cedula(self.user_message)
        self.anio = _extract_year(self.msg_norm, self.current_year)
        self.month_range = _extract_month_range(self.msg_norm)
        self.date_range = _extract_date_range(self.msg_norm, self.user_message, self.anio)
        self.mes_num = _extract_month(self.msg_norm)
        self.mes_nom = _extract_month_name(self.msg_norm)
        
        # Etiqueta y flag de rango
        if self.month_range:
            m1, m2 = self.month_range
            nombres = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
            self.range_label = f"{nombres[m1-1]} - {nombres[m2-1]} {self.anio}"
            self.is_range = True
        elif self.date_range and self.date_range[0] != self.date_range[1]:
            self.range_label = f"{self.date_range[0]} AL {self.date_range[1]}"
            self.is_range = True
        else:
            self.range_label = None
            self.is_range = False

        # Si no se extrajo mes del mensaje pero viene en el contexto activo
        if self.mes_num is None and not self.is_range and self.context:
            ctx_period = self.context.get("active_period") or {}
            ctx_mes = ctx_period.get("mes")
            if ctx_mes:
                if isinstance(ctx_mes, int):
                    self.mes_num = ctx_mes
                elif str(ctx_mes).isdigit():
                    self.mes_num = int(ctx_mes)
                else:
                    self.mes_num = _extract_month(_norm(str(ctx_mes)))
                    
        if self.mes_nom is None and self.mes_num is not None:
            nombres = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
            if 1 <= self.mes_num <= 12:
                self.mes_nom = nombres[self.mes_num - 1]

        self.day_range = _extract_day_range(self.msg_norm)
        self.novedad_type = _extract_novedad_type(self.msg_norm)
        self.subnovedad_oficial = _extract_subnovedad_oficial(self.msg_norm)
        self.is_least = _is_least_frequent(self.msg_norm)

@dataclass
class SkillResult:
    """Resultado estructurado retornado por un Skill ejecutado con éxito."""
    type: str  # 'sql', 'report', 'conversation', 'error'
    sql: Optional[str] = None
    description: Optional[str] = None
    report_info: Optional[Dict[str, Any]] = None
    answer: Optional[str] = None
    active_militar: Optional[Dict[str, Any]] = None
    columns: List[str] = field(default_factory=list)
    rows: List[Dict[str, Any]] = field(default_factory=list)
    total_records: int = 0

class BaseSkill(ABC):
    """Clase base que define una habilidad del sistema BIMEH."""

    name: str = "base_skill"
    description: str = "Descripción de la habilidad"

    @abstractmethod
    def can_handle(self, ctx: QueryContext) -> bool:
        """Determina si este skill sabe cómo atender la consulta del usuario."""
        pass

    @abstractmethod
    def execute(self, ctx: QueryContext) -> Optional[SkillResult]:
        """Ejecuta la habilidad y retorna el resultado estructurado o SQL parametrizado."""
        pass
