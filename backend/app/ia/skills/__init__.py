"""
Módulo de Habilidades (Skills) del Asistente IA de BIMEH.
"""

from app.ia.skills.base import BaseSkill, QueryContext, SkillResult
from app.ia.skills.registry import SkillRegistry
from app.ia.skills.reportes_export_skill import ReportesExportSkill
from app.ia.skills.report_delivery import ReportDeliveryEngine, ReportDeliveryRequest
from app.ia.skills.militar_skill import MilitarSkill
from app.ia.skills.novedades_skill import NovedadesSkill
from app.ia.skills.efectivos_skill import EfectivosSkill
from app.ia.skills.apreciacion_skill import ApreciacionSkill

def build_default_skill_registry() -> SkillRegistry:
    """Construye y registra el conjunto estándar de habilidades en orden de prioridad."""
    registry = SkillRegistry()
    registry.register(ReportesExportSkill())
    registry.register(MilitarSkill())
    registry.register(NovedadesSkill())
    registry.register(EfectivosSkill())
    registry.register(ApreciacionSkill())
    return registry

__all__ = [
    "BaseSkill",
    "QueryContext",
    "SkillResult",
    "SkillRegistry",
    "ReportesExportSkill",
    "ReportDeliveryEngine",
    "ReportDeliveryRequest",
    "MilitarSkill",
    "NovedadesSkill",
    "EfectivosSkill",
    "ApreciacionSkill",
    "build_default_skill_registry",
]
