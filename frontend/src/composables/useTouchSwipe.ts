import { ref, type Ref } from 'vue'

export interface TouchSwipeOptions<T extends string> {
  tabs: T[]
  currentTab: Ref<T>
  threshold?: number
}

export function useTouchSwipe<T extends string>(options: TouchSwipeOptions<T>) {
  const { tabs, currentTab, threshold = 40 } = options
  const touchStartX = ref(0)
  const touchEndX = ref(0)

  const handleTouchStart = (e: TouchEvent) => {
    if (e.changedTouches && e.changedTouches.length > 0) {
      touchStartX.value = e.changedTouches[0].screenX
    }
  }

  const handleTouchEnd = (e: TouchEvent) => {
    if (e.changedTouches && e.changedTouches.length > 0) {
      touchEndX.value = e.changedTouches[0].screenX
      handleSwipe()
    }
  }

  const handleSwipe = () => {
    const diff = touchStartX.value - touchEndX.value
    const currentIndex = tabs.indexOf(currentTab.value)

    if (diff > threshold) {
      // Swiped Left -> Siguiente pestaña
      if (currentIndex < tabs.length - 1) {
        currentTab.value = tabs[currentIndex + 1]
      }
    } else if (diff < -threshold) {
      // Swiped Right -> Pestaña anterior
      if (currentIndex > 0) {
        currentTab.value = tabs[currentIndex - 1]
      }
    }
  }

  return {
    handleTouchStart,
    handleTouchEnd
  }
}
