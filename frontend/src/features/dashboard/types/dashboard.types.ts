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
