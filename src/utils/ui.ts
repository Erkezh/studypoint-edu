import { nextTick } from 'vue'

let practicePagePrefetch: Promise<unknown> | null = null

export const waitForNextPaint = async () => {
  await nextTick()
  await new Promise<void>((resolve) => {
    requestAnimationFrame(() => resolve())
  })
}

export const prefetchPracticePage = () => {
  if (!practicePagePrefetch) {
    practicePagePrefetch = import('@/pages/PracticeSession.vue')
  }
  return practicePagePrefetch
}
