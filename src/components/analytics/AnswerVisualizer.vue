<template>
  <div class="answer-visualizer">
    <!-- Ten Frames (круги в рамках 2x5) -->
    <template v-if="data?.type === 'tenframes'">
      <div class="flex flex-wrap gap-4">
        <div
          v-for="(grid, gIdx) in grids"
          :key="'tf-' + gIdx"
          class="ten-frame inline-grid gap-1 p-3 bg-blue-50 rounded-xl border-2 border-blue-200"
          style="grid-template-columns: repeat(5, 1fr)"
        >
          <div
            v-for="cellIdx in 10"
            :key="'tfc-' + cellIdx"
            :class="[
              'w-8 h-8 rounded-full border-2 transition-all',
              isCellFilled(grid, cellIdx - 1)
                ? 'bg-pink-400 border-pink-500 shadow-sm'
                : 'bg-white border-gray-300'
            ]"
          />
        </div>
      </div>
    </template>

    <!-- Квадратная сетка (площадь) -->
    <template v-else-if="data?.type === 'grid'">
      <div class="flex flex-wrap gap-4">
        <div
          v-for="(grid, gIdx) in grids"
          :key="'grid-' + gIdx"
          class="inline-grid gap-0.5 p-2 bg-gray-100 rounded-lg border border-gray-300"
          :style="{ gridTemplateColumns: `repeat(${grid.cols || 10}, 1fr)` }"
        >
          <div
            v-for="cellIdx in ((grid.rows || 10) * (grid.cols || 10))"
            :key="'gc-' + cellIdx"
            :class="[
              'w-5 h-5 border transition-all',
              isCellFilled(grid, cellIdx - 1)
                ? variant === 'correct' ? 'bg-green-400 border-green-500' : 'bg-blue-400 border-blue-500'
                : 'bg-white border-gray-300'
            ]"
          />
        </div>
      </div>
    </template>

    <!-- Числовая прямая -->
    <template v-else-if="data?.type === 'numberline'">
      <div class="number-line-container p-4 bg-white rounded-lg border">
        <div class="relative h-16 mx-4">
          <!-- Линия -->
          <div class="absolute top-1/2 left-0 right-0 h-1 bg-gray-400 -translate-y-1/2"></div>
          <!-- Метки делений -->
          <div
            v-for="mark in numberLineMarks"
            :key="'nlm-' + mark.index"
            class="absolute top-1/2 -translate-y-1/2 flex flex-col items-center"
            :style="{ left: `${mark.position}%` }"
          >
            <div class="w-0.5 h-4 bg-gray-600"></div>
            <span v-if="mark.showLabel" class="text-xs text-gray-600 mt-1">{{ mark.label }}</span>
          </div>
          <!-- Отмеченная точка (вопрос) -->
          <div
            v-if="markedPoint"
            class="absolute top-1/2 -translate-y-1/2 flex flex-col items-center"
            :style="{ left: `${markedPoint.position}%` }"
          >
            <div
              class="w-5 h-5 rounded-full -mt-1 flex items-center justify-center text-white text-xs font-bold"
              :class="variant === 'question' ? 'bg-purple-500' : variant === 'correct' ? 'bg-green-500' : 'bg-blue-500'"
            >
              ?
            </div>
          </div>
          <!-- Выбранные точки (ответы) -->
          <div
            v-for="point in selectedPoints"
            :key="'nlp-' + point.value"
            class="absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full -ml-2"
            :class="variant === 'correct' ? 'bg-green-500' : 'bg-blue-500'"
            :style="{ left: `${point.position}%` }"
          />
        </div>
        <!-- Описание -->
        <p v-if="data.description" class="text-sm text-gray-600 mt-2 text-center">{{ data.description }}</p>
      </div>
    </template>

    <!-- Дробная полоска -->
    <template v-else-if="data?.type === 'fractionbar'">
      <div class="fraction-bar-container p-4 bg-white rounded-lg border">
        <div class="flex gap-0.5">
          <div
            v-for="i in fractionBarTotal"
            :key="'fb-' + i"
            :class="[
              'h-10 flex-1 border-2 transition-all',
              i <= fractionBarFilled
                ? variant === 'correct' ? 'bg-green-400 border-green-500' : variant === 'question' ? 'bg-purple-400 border-purple-500' : 'bg-blue-400 border-blue-500'
                : 'bg-white border-gray-300'
            ]"
          />
        </div>
        <p v-if="fractionBarLabel" class="text-center mt-2 text-lg font-semibold">{{ fractionBarLabel }}</p>
        <p v-if="data.description" class="text-sm text-gray-600 mt-1 text-center">{{ data.description }}</p>
      </div>
    </template>

    <!-- График функции -->
    <template v-else-if="data?.type === 'graph'">
      <div class="graph-container p-2 bg-white rounded-lg border">
        <svg :viewBox="`0 0 ${graphSize} ${graphSize}`" class="w-48 h-48">
          <!-- Сетка -->
          <g class="grid-lines">
            <line
              v-for="i in 11"
              :key="'gx-' + i"
              :x1="(i-1) * graphSize/10" :y1="0"
              :x2="(i-1) * graphSize/10" :y2="graphSize"
              stroke="#e5e7eb" stroke-width="1"
            />
            <line
              v-for="i in 11"
              :key="'gy-' + i"
              :x1="0" :y1="(i-1) * graphSize/10"
              :x2="graphSize" :y2="(i-1) * graphSize/10"
              stroke="#e5e7eb" stroke-width="1"
            />
          </g>
          <!-- Оси -->
          <line :x1="graphSize/2" y1="0" :x2="graphSize/2" :y2="graphSize" stroke="#374151" stroke-width="2"/>
          <line x1="0" :y1="graphSize/2" :x2="graphSize" :y2="graphSize/2" stroke="#374151" stroke-width="2"/>
          <!-- Линия графика -->
          <polyline
            v-if="graphPoints.length > 1"
            :points="graphPointsString"
            fill="none"
            :stroke="variant === 'correct' ? '#22c55e' : '#3b82f6'"
            stroke-width="3"
          />
          <!-- Точки -->
          <circle
            v-for="(point, pIdx) in graphPoints"
            :key="'gp-' + pIdx"
            :cx="point.svgX" :cy="point.svgY" r="5"
            :fill="variant === 'correct' ? '#22c55e' : '#3b82f6'"
          />
        </svg>
      </div>
    </template>

    <!-- Drag-drop элементы -->
    <template v-else-if="data?.type === 'dragdrop'">
      <div class="flex flex-wrap gap-2">
        <div
          v-for="(item, idx) in dragDropItems"
          :key="'dd-' + idx"
          :class="[
            'px-4 py-2 rounded-lg font-semibold text-lg border-2',
            item.type === 'number' ? 'bg-blue-100 border-blue-300 text-blue-700' :
            item.type === 'operator' ? 'bg-purple-100 border-purple-300 text-purple-700' :
            'bg-gray-100 border-gray-300 text-gray-700'
          ]"
        >
          {{ item.label }}
        </div>
      </div>
    </template>

    <!-- Фигуры (shapes) - для вопросов типа "сколько звёзд?" -->
    <template v-else-if="data?.type === 'shapes'">
      <div class="shapes-container p-4 bg-white rounded-lg border">
        <div class="flex flex-wrap gap-2 justify-center">
          <div
            v-for="(shape, idx) in shapesItems"
            :key="'shape-' + idx"
            class="w-8 h-8 flex items-center justify-center"
          >
            <!-- Круг -->
            <svg v-if="shape.type?.includes('шеңбер') || shape.type?.includes('circle')" viewBox="0 0 30 30" class="w-7 h-7">
              <circle cx="15" cy="15" r="12" :fill="shape.color" stroke="#374151" stroke-width="1"/>
            </svg>
            <!-- Квадрат -->
            <svg v-else-if="shape.type?.includes('шаршы') || shape.type?.includes('square')" viewBox="0 0 30 30" class="w-7 h-7">
              <rect x="3" y="3" width="24" height="24" :fill="shape.color" stroke="#374151" stroke-width="1"/>
            </svg>
            <!-- Треугольник -->
            <svg v-else-if="shape.type?.includes('үшбұрыш') || shape.type?.includes('triangle')" viewBox="0 0 30 30" class="w-7 h-7">
              <polygon points="15,3 27,27 3,27" :fill="shape.color" stroke="#374151" stroke-width="1"/>
            </svg>
            <!-- Звезда -->
            <svg v-else-if="shape.type?.includes('жұлдыз') || shape.type?.includes('star')" viewBox="0 0 30 30" class="w-7 h-7">
              <polygon points="15,2 18,11 28,11 20,17 23,27 15,21 7,27 10,17 2,11 12,11" :fill="shape.color" stroke="#374151" stroke-width="1"/>
            </svg>
            <!-- Шестиугольник -->
            <svg v-else-if="shape.type?.includes('алтыбұрыш') || shape.type?.includes('hexagon')" viewBox="0 0 30 30" class="w-7 h-7">
              <polygon points="15,2 26,9 26,21 15,28 4,21 4,9" :fill="shape.color" stroke="#374151" stroke-width="1"/>
            </svg>
            <!-- По умолчанию - круг -->
            <svg v-else viewBox="0 0 30 30" class="w-7 h-7">
              <circle cx="15" cy="15" r="12" :fill="shape.color || '#3b82f6'" stroke="#374151" stroke-width="1"/>
            </svg>
          </div>
        </div>
        <p v-if="shapesTarget" class="text-center mt-3 text-sm text-gray-600">
          {{ shapesTarget }}: <span class="font-semibold">{{ shapesTargetCount }}/{{ shapesTotalCount }}</span>
        </p>
        <p v-if="data.description" class="text-sm text-gray-600 mt-2 text-center">{{ data.description }}</p>
      </div>
    </template>

    <!-- Fallback: просто текст -->
    <template v-else>
      <p class="text-gray-700">{{ text || '-' }}</p>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Grid {
  rows: number
  cols: number
  filled: string[]
}

interface NumberlineData {
  min?: number
  max?: number
  divisions?: number
  markedPosition?: number
  label?: string
}

interface GridData {
  rows: number
  cols: number
  filled: string[]
  highlight?: string[]
}

interface FractionBarData {
  total: number
  filled: number
  label?: string
}

interface ShapesData {
  items: Array<{ type: string, color: string }>
  targetType: string
  targetCount: number
  totalCount: number
}

interface DisplayData {
  type: 'tenframes' | 'grid' | 'numberline' | 'graph' | 'dragdrop' | 'fractionbar' | 'shapes'
  grids?: GridData[]
  text?: string
  note?: string
  description?: string
  // Для числовой прямой (старый формат)
  min?: number
  max?: number
  markers?: number[]
  selected?: number[]
  // Для числовой прямой (новый формат questionData)
  numberline?: NumberlineData
  // Для сетки (новый формат questionData)
  grid?: GridData
  // Для дробной полоски
  fractionBar?: FractionBarData
  // Для графика
  points?: Array<{ x: number, y: number }>
  xRange?: [number, number]
  yRange?: [number, number]
  graph?: {
    points?: Array<{ x: number, y: number }>
    xRange?: [number, number]
    yRange?: [number, number]
    highlightPoint?: { x: number, y: number }
  }
  // Для drag-drop
  items?: Array<{ id: string, label: string, type?: string }>
  order?: string[]
  // Для фигур (shapes)
  shapes?: ShapesData
}

const props = defineProps<{
  data: DisplayData | null
  variant?: 'correct' | 'user' | 'question'
  text?: string
}>()

const graphSize = 200

// Grids для сеток
const grids = computed(() => props.data?.grids || [])

// Проверка заполненности ячейки
const isCellFilled = (grid: Grid, cellIdx: number): boolean => {
  const cols = grid.cols || 5
  const row = Math.floor(cellIdx / cols)
  const col = cellIdx % cols
  return grid.filled?.includes(`${row}-${col}`) || false
}

// Числовая прямая
const numberLineMarks = computed(() => {
  if (props.data?.type !== 'numberline') return []

  // Новый формат с numberline объектом
  if (props.data.numberline) {
    const nl = props.data.numberline
    const divisions = nl.divisions || 11
    const min = nl.min ?? 0
    const max = nl.max ?? 1

    const marks = []
    for (let i = 0; i < divisions; i++) {
      const value = min + (i / (divisions - 1)) * (max - min)
      marks.push({
        index: i,
        value,
        position: (i / (divisions - 1)) * 100,
        label: i === 0 ? String(min) : i === divisions - 1 ? String(max) : '',
        showLabel: i === 0 || i === divisions - 1
      })
    }
    return marks
  }

  // Старый формат с markers
  const min = props.data.min ?? 0
  const max = props.data.max ?? 10
  const markers = props.data.markers || []
  return markers.map((v, i) => ({
    index: i,
    value: v,
    position: ((v - min) / (max - min)) * 100,
    label: String(v),
    showLabel: true
  }))
})

// Отмеченная точка (для вопроса)
const markedPoint = computed(() => {
  if (props.data?.type !== 'numberline' || !props.data.numberline) return null

  const nl = props.data.numberline
  if (nl.markedPosition === undefined) return null

  const divisions = nl.divisions || 11
  return {
    position: (nl.markedPosition / (divisions - 1)) * 100
  }
})

const selectedPoints = computed(() => {
  if (props.data?.type !== 'numberline') return []
  const min = props.data.min ?? 0
  const max = props.data.max ?? 10
  const selected = props.data.selected || []
  return selected.map(v => ({
    value: v,
    position: ((v - min) / (max - min)) * 100
  }))
})

// Дробная полоска
const fractionBarTotal = computed(() => {
  if (props.data?.type !== 'fractionbar') return 0
  return props.data.fractionBar?.total || 0
})

const fractionBarFilled = computed(() => {
  if (props.data?.type !== 'fractionbar') return 0
  return props.data.fractionBar?.filled || 0
})

const fractionBarLabel = computed(() => {
  if (props.data?.type !== 'fractionbar') return ''
  return props.data.fractionBar?.label || ''
})

// График
const graphPoints = computed(() => {
  if (props.data?.type !== 'graph' || !props.data.points) return []
  const xRange = props.data.xRange || [-5, 5]
  const yRange = props.data.yRange || [-5, 5]

  return props.data.points.map(p => ({
    ...p,
    svgX: ((p.x - xRange[0]) / (xRange[1] - xRange[0])) * graphSize,
    svgY: graphSize - ((p.y - yRange[0]) / (yRange[1] - yRange[0])) * graphSize
  }))
})

const graphPointsString = computed(() => {
  return graphPoints.value.map(p => `${p.svgX},${p.svgY}`).join(' ')
})

// Drag-drop
const dragDropItems = computed(() => {
  if (props.data?.type !== 'dragdrop') return []
  const items = props.data.items || []
  const order = props.data.order || items.map(i => i.id)
  return order.map(id => items.find(i => i.id === id)).filter(Boolean)
})

// Shapes (фигуры)
const shapesItems = computed(() => {
  if (props.data?.type !== 'shapes') return []
  return props.data.shapes?.items || []
})

const shapesTarget = computed(() => {
  if (props.data?.type !== 'shapes') return ''
  return props.data.shapes?.targetType || ''
})

const shapesTargetCount = computed(() => {
  if (props.data?.type !== 'shapes') return 0
  return props.data.shapes?.targetCount || 0
})

const shapesTotalCount = computed(() => {
  if (props.data?.type !== 'shapes') return 0
  return props.data.shapes?.totalCount || 0
})
</script>

<style scoped>
.ten-frame {
  width: fit-content;
}
</style>
