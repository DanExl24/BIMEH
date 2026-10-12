export interface AlertaFatigaItem {
  id_personal: number
  cedula: number
  nombre: string
  dias_continuos: number
  estado_actual: string
  nivel_alerta: 'MODERADO' | 'ALTO' | 'CRITICO'
  recomendacion: string
}

export interface AlertaSanidadItem {
  id_personal: number
  cedula: number
  nombre: string
  total_dias_sanidad: number
  episodios: number
  novedades: string
  ultima_fecha: string
  clasificacion: 'JUNTA_MEDICA_SUGERIDA' | 'SEGUIMIENTO_SANIDAD'
  recomendacion: string
}

export interface ProyeccionHorizonte {
  estimados_disponibles: number
  porcentaje: number
  reincorporaciones: number
  salidas_programadas: number
}

export interface ProyeccionMovimiento {
  id_personal: number
  cedula: number
  nombre: string
  novedad: string
  fecha_fin: string
  dias_restantes: number
  descripcion?: string
}

export interface ProyeccionFuerzaData {
  fecha_base: string
  efectivo_actual: {
    total: number
    disponibles: number
    novedades: number
    porcentaje: number
  }
  proyeccion_7_dias: ProyeccionHorizonte
  proyeccion_15_dias: ProyeccionHorizonte
  proyeccion_30_dias: ProyeccionHorizonte
  detalle_movimientos: ProyeccionMovimiento[]
}

export interface SubnovedadResumen {
  nombre: string
  cantidad: number
}

export interface AlertasResumen {
  total_fatiga_critica: number
  total_sanidad_critica: number
  top_casos_fatiga: Array<{
    nombre: string
    dias: number
    alerta: string
  }>
  top_casos_sanidad: Array<{
    nombre: string
    dias: number
    novedad: string
  }>
}

export interface ParteDiarioData {
  fecha: string
  total_personal: number
  disponibles: number
  novedades: number
  porcentaje_disponibilidad: number
  disposicion: {
    area_operaciones: number
    cdo_unidad: number
  }
  desglose_categorias: {
    sanidad: number
    descanso: number
    servicio: number
    administrativas: number
  }
  desglose_subnovedades: SubnovedadResumen[]
  alertas_resumen: AlertasResumen
  radiograma_texto: string
}
