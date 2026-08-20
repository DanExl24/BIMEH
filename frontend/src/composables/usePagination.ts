import { ref, computed, type Ref } from 'vue'

export function usePagination<T>(items: Ref<T[]>, pageSize: number = 10) {
  const currentPage = ref(1)

  const totalPages = computed(() => {
    return Math.ceil(items.value.length / pageSize) || 1
  })

  const paginatedItems = computed(() => {
    const start = (currentPage.value - 1) * pageSize
    return items.value.slice(start, start + pageSize)
  })

  const hasNextPage = computed(() => currentPage.value < totalPages.value)
  const hasPrevPage = computed(() => currentPage.value > 1)

  const nextPage = () => {
    if (hasNextPage.value) {
      currentPage.value++
    }
  }

  const prevPage = () => {
    if (hasPrevPage.value) {
      currentPage.value--
    }
  }

  const resetPage = () => {
    currentPage.value = 1
  }

  const totalCount = computed(() => items.value.length)
  const rangeStart = computed(() => (items.value.length === 0 ? 0 : (currentPage.value - 1) * pageSize + 1))
  const rangeEnd = computed(() => Math.min(currentPage.value * pageSize, items.value.length))

  return {
    currentPage,
    totalPages,
    paginatedItems,
    hasNextPage,
    hasPrevPage,
    nextPage,
    prevPage,
    resetPage,
    totalCount,
    rangeStart,
    rangeEnd
  }
}
