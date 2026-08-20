/**
 * Utilidades puras para el manejo de personal y novedades
 */

export const DISPONIBLE_STATUSES = [
  'CDO UNIDAD',
  'AREA OPERACIONES',
  'SIN NOVEDAD',
  'DISPONIBLE',
  'SERVICIO ACTIVO'
]

export function isAvailable(subnovedad?: string | null): boolean {
  if (!subnovedad) return true
  const s = subnovedad.trim().toUpperCase()
  if (s === '' || s === '-') return true
  return DISPONIBLE_STATUSES.includes(s)
}


export function getStatusBadgeClass(estado: string): string {
  const e = (estado || '').toUpperCase()
  if (e === 'ACTIVO') {
    return 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
  }
  return 'bg-red-500/10 border-red-500/20 text-red-400'
}

export function getHeatmapCellClass(code: string): string {
  switch (code) {
    case 'D':
      return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
    case 'N':
      return 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
    case 'R':
      return 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
    default:
      return 'bg-slate-800/40 text-slate-600 border border-darkBorder/40'
  }
}

export function getStatusLabel(code: string): string {
  switch (code) {
    case 'D':
      return 'DISPONIBLE'
    case 'N':
      return 'NOVEDAD'
    case 'R':
      return 'RETIRADO'
    default:
      return 'SIN REGISTRO'
  }
}
