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
