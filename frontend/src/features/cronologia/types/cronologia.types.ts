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
