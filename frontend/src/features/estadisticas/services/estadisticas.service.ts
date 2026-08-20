import { http } from '@services/http'
import type { RankingsData } from '@types'

export const estadisticasService = {
  getRankings: async (): Promise<RankingsData> => {
    return http.get<RankingsData>('/api/stats/ranking')
  }
}
