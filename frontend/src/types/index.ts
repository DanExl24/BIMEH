export interface KPIData {
  fecha: string
  total_personal: number
  disponibles: number
  novedades: number
  disponibilidad: number
  cambios_vs_ayer: number
}

export interface CambioEstado {
  cedula: number
  nombre: string
  novedad_anterior: string
  novedad_nueva: string
  fecha: string
}

export interface CambiosResponse {
  entraron_novedades: CambioEstado[]
  volvieron_disponibles: CambioEstado[]
  otros_cambios: CambioEstado[]
}

export interface EvolucionItem {
  fecha: string
  total_personal: number
  disponibles: number
  novedades: number
  disponibilidad: number
}

export interface NovedadFrecuente {
  novedad: string
  cantidad: number
}

export interface DistribucionItem {
  subnovedad: string
  cantidad: number
  porcentaje: number
  categoria: 'DISPONIBLE' | 'NOVEDAD'
}

export interface PersonalSearchResult {
  cedula: number
  nombre: string
  estado: 'ACTIVO' | 'RETIRADO'
  fecha_retiro: string | null
}

export interface PersonalDetalle {
  cedula: number
  nombre: string
  estado: 'ACTIVO' | 'RETIRADO'
  fecha_retiro: string | null
  primer_registro_fecha: string | null
  ultimo_registro_fecha: string | null
  total_dias: number
  tiempo_disponible_pct: number
  tiempo_novedades_pct: number
  total_novedades: number
  promedio_duracion_novedades: number
  ultima_novedad: string | null
}

export interface HistorialRegistro {
  fecha: string
  subnovedad: string
  descripcion: string
  desde: string | null
  hasta: string | null
}

export interface AcumuladoNovedad {
  subnovedad: string
  dias: number
}

export interface CalendarioItem {
  fecha: string
  disponibilidad: number
  total_personal: number
  disponibles: number
  novedades: number
}

export interface PersonalDia {
  cedula: number
  nombre: string
  subnovedad: string
  descripcion: string | null
  desde: string | null
  hasta: string | null
}

export interface HeatmapRow {
  cedula: number
  nombre: string
  estados: string[]
}

export interface HeatmapResponse {
  fechas: string[]
  data: HeatmapRow[]
}

export interface RankingItem {
  subnovedad: string
  dias_acumulados: number
}

export interface PersonnelRankingItem {
  cedula: number
  nombre: string
  dias_novedad: number
}

export interface RankingsData {
  global_rank: RankingItem[]
  most_novelties_people: PersonnelRankingItem[]
}
