/**
 * Utilidades centralizadas para manejo y formato de fechas y meses en BIMEH
 */

export const MONTHS_LIST = [
  'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
  'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'
] as const

export type MonthName = typeof MONTHS_LIST[number]

export const MONTH_TO_NUMBER: Record<string, string> = {
  'ENERO': '01', 'FEBRERO': '02', 'MARZO': '03', 'ABRIL': '04',
  'MAYO': '05', 'JUNIO': '06', 'JULIO': '07', 'AGOSTO': '08',
  'SEPTIEMBRE': '09', 'OCTUBRE': '10', 'NOVIEMBRE': '11', 'DICIEMBRE': '12'
}

export const NUMBER_TO_MONTH: Record<string, string> = {
  '01': 'ENERO', '02': 'FEBRERO', '03': 'MARZO', '04': 'ABRIL',
  '05': 'MAYO', '06': 'JUNIO', '07': 'JULIO', '08': 'AGOSTO',
  '09': 'SEPTIEMBRE', '10': 'OCTUBRE', '11': 'NOVIEMBRE', '12': 'DICIEMBRE',
  '1': 'ENERO', '2': 'FEBRERO', '3': 'MARZO', '4': 'ABRIL',
  '5': 'MAYO', '6': 'JUNIO', '7': 'JULIO', '8': 'AGOSTO',
  '9': 'SEPTIEMBRE'
}

export const MONTH_SPANISH_NAMES: Record<string, string> = {
  '01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril',
  '05': 'Mayo', '06': 'Junio', '07': 'Julio', '08': 'Agosto',
  '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
}

/**
 * Obtiene el número total de días para un mes y año específico
 */
export function getDaysInMonth(monthNameOrNumber: string, year: number = new Date().getFullYear()): number {
  const mNumStr = MONTH_TO_NUMBER[monthNameOrNumber.toUpperCase()] || monthNameOrNumber
  const mNum = parseInt(mNumStr, 10)
  if (isNaN(mNum) || mNum < 1 || mNum > 12) return 31
  return new Date(year, mNum, 0).getDate()
}

/**
 * Genera la lista de días formateados en 2 dígitos ['01', '02', ..., '31'] para un mes
 */
export function getMonthDaysArray(monthNameOrNumber?: string, year: number = new Date().getFullYear()): string[] {
  const totalDays = monthNameOrNumber ? getDaysInMonth(monthNameOrNumber, year) : 31
  return Array.from({ length: totalDays }, (_, i) => String(i + 1).padStart(2, '0'))
}

/**
 * Formatea una fecha ISO (YYYY-MM-DD) a formato legible
 */
export function formatISODate(dateStr: string | null | undefined): string {
  if (!dateStr) return '-'
  const parts = dateStr.split('-')
  if (parts.length !== 3) return dateStr
  const monthName = MONTH_SPANISH_NAMES[parts[1]] || parts[1]
  return `${parts[2]} de ${monthName}, ${parts[0]}`
}
