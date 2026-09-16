export interface NovedadCatalogoItem {
  id: number
  nombre: string
  total_registros: number
  total_personal: number
}

export interface NovedadRegistroItem {
  id: number
  cedula: number
  nombre: string
  estado: 'ACTIVO' | 'RETIRADO'
  fecha_retiro: string | null
  id_sub_novedad: number
  sub_novedad: string
  fecha_reporte: string
  fecha_inicio: string
  fecha_final: string
  descripcion: string
}

export interface NovedadesKpis {
  total_registros: number
  personal_unico: number
  activos_unicos: number
  retirados_unicos: number
  primera_fecha: string | null
  ultima_fecha: string | null
}

export interface NovedadesConsultaFiltros {
  id_sub_novedad?: number | null
  mes?: string
  fecha_inicio?: string
  fecha_fin?: string
  q?: string
  estado?: 'TODOS' | 'ACTIVO' | 'RETIRADO'
  page?: number
  limit?: number
}

export interface NovedadesConsultaResponse {
  kpis: NovedadesKpis
  registros: NovedadRegistroItem[]
  total: number
  page: number
  limit: number
  total_pages: number
}
