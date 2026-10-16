"""
Registro y despachador centralizado de habilidades (Skill Registry).
"""

import logging
from typing import List, Optional
from app.ia.skills.base import BaseSkill, QueryContext, SkillResult

logger = logging.getLogger(__name__)

class SkillRegistry:
    """Gestiona el conjunto de skills registrados y despacha las intenciones del usuario."""

    def __init__(self):
        self._skills: List[BaseSkill] = []

    def register(self, skill: BaseSkill) -> None:
        """Registra un nuevo skill en el despachador."""
        self._skills.append(skill)
        logger.debug(f"[SkillRegistry] Registrado skill: '{skill.name}'")

    def dispatch(self, ctx: QueryContext) -> Optional[SkillResult]:
        """
        Evalúa secuencialmente los skills registrados hasta encontrar uno que pueda
        atender la consulta (fast-path). Retorna None si ningún skill coincide.
        """
        for skill in self._skills:
            try:
                if skill.can_handle(ctx):
                    logger.info(f"[SkillRegistry] Coincidencia encontrada con skill '{skill.name}'")
                    result = skill.execute(ctx)
                    if result:
                        return result
            except Exception as e:
                logger.error(f"[SkillRegistry] Error ejecutando skill '{skill.name}': {e}", exc_info=True)
        return None

    def get_all_skills(self) -> List[BaseSkill]:
        return list(self._skills)
