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
