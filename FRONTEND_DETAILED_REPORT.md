# 📋 Подробный отчет о функциональности фронтенда проекта Math Edu

**Дата составления:** 23 января 2026  
**Версия:** 1.0  
**Проект:** Math Edu Beta 1

---

## 📑 Содержание

1. [Общая информация](#общая-информация)
2. [Архитектура проекта](#архитектура-проекта)
3. [Страницы с примерами кода](#страницы-с-примерами-кода)
4. [Компоненты](#компоненты)
5. [State Management (Pinia Stores)](#state-management-pinia-stores)
6. [API клиенты](#api-клиенты)
7. [Роутинг и защита](#роутинг-и-защита)
8. [Особенности реализации](#особенности-реализации)
9. [Новые функции (Плагины)](#новые-функции-плагины)
10. [Инструкции для скриншотов](#инструкции-для-скриншотов)

---

## Общая информация

### Технологический стек

- **Vue 3** (Composition API) - основной фреймворк
- **TypeScript** - типизация
- **Pinia** - управление состоянием
- **Vue Router** - маршрутизация
- **Axios** - HTTP клиент
- **Tailwind CSS** - стилизация
- **Vite** - сборщик

### Структура проекта

```
src/
├── pages/          # 13 страниц приложения
├── components/     # Переиспользуемые компоненты
├── stores/         # Pinia stores (5 штук)
├── api/            # API клиенты (6 штук)
├── router/         # Конфигурация роутинга
├── composables/    # Композиции (2 штуки)
└── types/          # TypeScript типы
```

---

## Архитектура проекта

### Принципы организации

1. **Composition API** - все компоненты используют `<script setup>`
2. **TypeScript** - строгая типизация
3. **Pinia** - централизованное управление состоянием
4. **Разделение ответственности** - страницы, компоненты, stores, API клиенты разделены

### Поток данных

```
Пользователь → Компонент → Store → API Client → Backend
                ↓
            LocalStorage (кэш)
```

---

## Страницы с примерами кода

### 1. Home.vue - Главная страница

**Путь:** `/`  
**Доступ:** Без авторизации  
**Файл:** `src/pages/Home.vue`

#### Функциональность

Отображает список доступных классов (grades) в виде карточек. При клике на карточку происходит переход к просмотру класса.

#### Пример кода

```vue
<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-6">Басты бет</h1>

      <!-- Индикатор загрузки -->
      <div v-if="catalogStore.loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">Жүктелуде...</p>
      </div>

      <!-- Ошибка -->
      <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {{ error }}
      </div>

      <!-- Список классов -->
      <div v-else>
        <h2 class="text-2xl font-semibold mb-4">Қолжетімді сыныптар</h2>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card
            v-for="grade in grades"
            :key="grade.id"
            clickable
            class="hover:shadow-xl transition-shadow"
            @click="navigateToClass(grade.number)"
          >
            <h3 class="text-xl font-semibold mb-2">{{ grade.title }}</h3>
            <p class="text-gray-600">{{ grade.number }} сынып</p>
          </Card>
        </div>
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const catalogStore = useCatalogStore()

const grades = ref(catalogStore.grades)
const error = ref<string | null>(null)

const navigateToClass = (gradeNumber: number) => {
  router.push({ name: 'class', params: { gradeId: gradeNumber } })
}

onMounted(async () => {
  try {
    const fetchedGrades = await catalogStore.getGrades()
    grades.value = fetchedGrades
  } catch (err: any) {
    error.value = err.message || 'Сыныптарды жүктеу мүмкін болмады'
    console.error('Failed to load grades:', err)
  }
})
</script>
```

#### Ключевые моменты

1. **Использование CatalogStore** - данные загружаются через store с кэшированием
2. **Обработка состояний** - loading, error, success
3. **Реактивность** - `ref()` для реактивных данных
4. **Lifecycle hook** - `onMounted()` для загрузки данных

#### 📸 Скриншот

**Что снимать:** Главная страница с сеткой карточек классов (1, 2, 3, 4, 5 класс и т.д.)

---

### 2. ClassView.vue - Просмотр класса

**Путь:** `/class/:gradeId`  
**Доступ:** Без авторизации  
**Файл:** `src/pages/ClassView.vue`

#### Функциональность

Отображает список навыков (skills) для выбранного класса. Показывает статистику SmartScore только для авторизованных пользователей. Имеет боковую панель с классами.

#### Пример кода (отображение навыков)

```vue
<div v-else-if="skills && skills.length > 0" class="space-y-1">
  <div
    v-for="skill in skills"
    :key="skill.id"
    @click="navigateToSkill(skill.id)"
    class="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200 hover:border-lime-400 hover:shadow-md transition-all cursor-pointer"
  >
    <div class="flex items-center gap-4 flex-1">
      <!-- Иконка статуса (галочка для пройденных) -->
      <div v-if="skillStats.has(skill.id) && skillStats.get(skill.id)!.best_smartscore >= 90" class="flex-shrink-0">
        <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
      </div>
      
      <!-- Название навыка -->
      <div class="flex-1">
        <h3 class="text-base font-medium text-gray-900 hover:text-lime-600">
          {{ skill.title }}
        </h3>
        <!-- SmartScore только для авторизованных -->
        <p v-if="skillStats.has(skill.id) && authStore.isAuthenticated" class="text-sm text-gray-500 mt-1">
          SmartScore:
          <span :class="{
            'text-green-600 font-semibold': skillStats.get(skill.id)!.best_smartscore >= 90,
            'text-blue-600': skillStats.get(skill.id)!.best_smartscore >= 70 && skillStats.get(skill.id)!.best_smartscore < 90,
            'text-yellow-600': skillStats.get(skill.id)!.best_smartscore < 70
          }">
            {{ skillStats.get(skill.id)!.best_smartscore || skillStats.get(skill.id)!.last_smartscore || 0 }}
          </span>
        </p>
      </div>
    </div>
  </div>
</div>
```

#### Ключевые моменты

1. **Условное отображение SmartScore** - `v-if="authStore.isAuthenticated"`
2. **Цветовая индикация** - зеленый (>=90), синий (70-89), желтый (<70)
3. **Иконка пройденных** - галочка для навыков с SmartScore >= 90
4. **Реактивная навигация** - клик по навыку ведет на страницу навыка

#### 📸 Скриншот

**Что снимать:** 
- Боковая панель с классами (полукруглые кнопки)
- Список навыков с цветовой индикацией SmartScore
- Иконки галочек для пройденных навыков

---

### 3. PracticeSession.vue - Сессия практики

**Путь:** `/practice/:sessionId`  
**Доступ:** Без авторизации (пробные вопросы)  
**Файл:** `src/pages/PracticeSession.vue`

#### Функциональность

Самая сложная страница. Отображает вопросы, обрабатывает ответы, показывает результаты, управляет сессией.

#### Пример кода (отображение SmartScore)

```vue
<!-- SmartScore отображается только для авторизованных -->
<div v-if="authStore.isAuthenticated" class="flex items-center gap-3">
  <h2 class="text-xl font-semibold">SmartScore: {{ practiceStore.smartscore }}</h2>
  <span v-if="previousBestScore !== null && previousBestScore > 0" class="text-sm text-gray-600">
    (Ең жақсы: {{ previousBestScore }})
  </span>
</div>

<!-- Зона (LEARNING/REFINING/CHALLENGE) -->
<span
  :class="[
    'px-3 py-1 rounded-full text-sm font-medium',
    {
      'bg-yellow-100 text-yellow-800': practiceStore.zone === 'LEARNING',
      'bg-blue-100 text-blue-800': practiceStore.zone === 'REFINING',
      'bg-purple-100 text-purple-800': practiceStore.zone === 'CHALLENGE',
    },
  ]"
>
  {{ getZoneText(practiceStore.zone) }}
</span>
```

#### Пример кода (обработка MCQ вопросов)

```vue
<!-- MCQ (Multiple Choice Question) -->
<div v-if="currentQuestion.type === 'MCQ'" class="space-y-2">
  <button
    v-for="(option, index) in (currentQuestion.data?.choices || currentQuestion.data?.options || [])"
    :key="index"
    @click="submitMCQAnswer(option, index)"
    :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
    class="w-full text-left p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
  >
    <span v-html="formatMCQOption(option)"></span>
  </button>
</div>
```

#### Пример кода (отображение результата)

```vue
<div v-if="showingResult && lastResult" class="bg-white rounded-lg shadow-md p-6 mb-6">
  <div
    :class="[
      'rounded-lg p-6 mb-6',
      lastResult.is_correct
        ? 'bg-green-100 border border-green-300 text-green-800'
        : 'bg-red-100 border border-red-300 text-red-800',
    ]"
  >
    <p class="font-semibold text-lg mb-4">
      {{ lastResult.is_correct ? '✓ Дұрыс!' : '✗ Қате' }}
    </p>
    
    <!-- Показываем ответ пользователя и правильный ответ при неправильном ответе -->
    <div v-if="!lastResult.is_correct" class="space-y-3 mt-4">
      <div>
        <p class="font-medium mb-1">Сіздің жауабыңыз:</p>
        <p class="text-sm bg-white px-3 py-2 rounded border border-red-400" v-html="formatUserAnswer(userAnswer, lastQuestion)"></p>
      </div>
      <div>
        <p class="font-medium mb-1">Дұрыс жауап:</p>
        <p class="text-sm bg-white px-3 py-2 rounded border border-green-400" v-html="formatCorrectAnswer(lastQuestion, lastResult)"></p>
      </div>
    </div>
    
    <p v-if="lastResult.explanation" class="text-sm mt-4 italic">{{ lastResult.explanation }}</p>
  </div>
</div>
```

#### Пример кода (обработка INTERACTIVE вопросов)

```vue
<!-- INTERACTIVE (интерактивные задания с кодом) -->
<div v-else-if="currentQuestion.type === 'INTERACTIVE'" class="space-y-4">
  <InteractiveQuestion
    v-if="currentQuestion.data?.component_code"
    :component-code="currentQuestion.data.component_code"
    :question-data="currentQuestion.data"
    :disabled="submitting || showingResult || (shouldCheckTrialQuestions && trialQuestions.isTrialQuestionsExhausted.value)"
    @answer="handleInteractiveAnswer"
  />
  <div v-else class="text-red-500 text-sm">
    ⚠ Интерактивное задание не загружено. Код компонента отсутствует.
  </div>
</div>
```

#### Ключевые моменты

1. **Условное отображение SmartScore** - только для авторизованных
2. **Типы вопросов** - MCQ, NUMERIC, TEXT, MULTI_SELECT, INTERACTIVE
3. **Idempotency Key** - для предотвращения дублирования ответов
4. **Heartbeat** - отслеживание активности каждые 30 секунд
5. **Пробные вопросы** - лимит 10 в день для неавторизованных

#### 📸 Скриншот

**Что снимать:**
- Вопрос с вариантами ответов
- Результат после ответа (правильно/неправильно)
- SmartScore и зона (для авторизованных)
- Таймер и счетчики

---

### 4. AdminPlugins.vue - Управление плагинами ⭐ НОВОЕ

**Путь:** `/admin/plugins`  
**Доступ:** Только ADMIN  
**Файл:** `src/pages/AdminPlugins.vue`

#### Функциональность

Страница для загрузки, управления и предпросмотра интерактивных плагинов.

#### Пример кода (загрузка плагина)

```vue
<form @submit.prevent="handleUpload" class="space-y-4">
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-2">
      ZIP файл плагина
    </label>
    <input
      ref="fileInput"
      type="file"
      accept=".zip"
      @change="handleFileSelect"
      class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
    />
    <p v-if="selectedFile" class="text-sm text-gray-600 mt-2">
      Выбран файл: {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
    </p>
  </div>

  <div class="flex gap-4">
    <Button type="submit" variant="primary" :loading="uploading">
      Загрузить плагин
    </Button>
  </div>
</form>
```

#### Пример кода (обработка загрузки)

```typescript
const handleUpload = async () => {
  if (!selectedFile.value) {
    error.value = 'Выберите файл для загрузки'
    return
  }

  uploading.value = true
  error.value = null
  successMessage.value = null

  try {
    const response = await adminApi.uploadPlugin(selectedFile.value)
    successMessage.value = `Плагин "${response.data.name}" успешно загружен!`
    resetUpload()
    await loadPlugins()
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err: any) {
    console.error('Upload error:', err)
    const errorDetail = err.response?.data?.error || err.response?.data
    let errorMsg = err.message
    
    // Обработка 409 Conflict
    if (err.response?.status === 409) {
      errorMsg = errorDetail?.message || 'Плагин с таким ID и версией уже существует. Если он опубликован, сначала скройте его.'
    }
    
    error.value = errorMsg || 'Ошибка при загрузке плагина'
  } finally {
    uploading.value = false
  }
}
```

#### Пример кода (Preview с postMessage)

```vue
<!-- Preview Modal -->
<div v-if="previewPluginData" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
  <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
    <!-- Лог postMessage событий -->
    <div class="mb-4 p-3 bg-gray-50 rounded border">
      <h4 class="font-semibold mb-2">PostMessage Events:</h4>
      <div class="space-y-1 max-h-32 overflow-y-auto">
        <div
          v-for="(event, idx) in messageLog"
          :key="idx"
          class="text-xs font-mono p-2 bg-white rounded border"
        >
          <span class="font-semibold">{{ event.type }}:</span>
          <pre class="mt-1 text-xs">{{ JSON.stringify(event.data, null, 2) }}</pre>
        </div>
      </div>
    </div>

    <!-- Iframe с плагином -->
    <iframe
      :src="pluginUrl"
      :style="{ width: '100%', height: `${previewPluginData.height}px`, border: '1px solid #e5e7eb' }"
      sandbox="allow-scripts allow-same-origin"
      class="rounded"
      @load="handleIframeLoad"
    ></iframe>
  </div>
</div>
```

#### Пример кода (обработка postMessage)

```typescript
const setupMessageHandler = () => {
  // Удаляем предыдущий обработчик, если есть
  if (messageHandler.value) {
    window.removeEventListener('message', messageHandler.value)
  }
  
  messageHandler.value = (event: MessageEvent) => {
    try {
      const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data
      
      if (data.type) {
        messageLog.value.push({
          type: data.type,
          data: data,
        })
        
        // Обрабатываем SUBMIT - отправляем на сервер
        if (data.type === 'SUBMIT') {
          handlePluginSubmit(data)
        }
        
        // Обрабатываем INIT - отправляем подтверждение
        if (data.type === 'INIT') {
          sendMessageToPlugin({
            type: 'INIT',
            status: 'ready',
          })
        }
      }
    } catch (e) {
      console.error('Error parsing message:', e)
    }
  }
  
  window.addEventListener('message', messageHandler.value)
}

const handlePluginSubmit = async (data: any) => {
  try {
    // Отправляем на сервер для проверки
    const response = await fetch(`${API_BASE_URL}/api/v1/plugins/evaluate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        plugin_id: previewPluginData.value?.plugin_id,
        task_id: data.taskId || 'preview',
        userAnswer: data.userAnswer,
      }),
    })
    
    const result = await response.json()
    
    // Отправляем результат обратно в плагин
    sendMessageToPlugin({
      type: 'SERVER_RESULT',
      correct: result.data?.correct || false,
      score: result.data?.score || 0,
      explanation: result.data?.explanation || '',
    })
  } catch (err) {
    console.error('Evaluate error:', err)
    sendMessageToPlugin({
      type: 'SERVER_RESULT',
      correct: false,
      score: 0,
      explanation: 'Ошибка при проверке ответа',
    })
  }
}

const sendMessageToPlugin = (data: any) => {
  // Находим iframe и отправляем сообщение
  const iframe = document.querySelector('iframe')
  if (iframe && iframe.contentWindow) {
    iframe.contentWindow.postMessage(data, '*') // В продакшене указать конкретный origin
  }
}
```

#### Ключевые моменты

1. **Загрузка ZIP** - валидация размера (макс. 10MB)
2. **PostMessage API** - двусторонняя коммуникация с плагином
3. **Iframe sandbox** - изоляция плагина
4. **Логирование событий** - все postMessage события логируются
5. **Интеграция с сервером** - проверка ответов через API

#### 📸 Скриншот

**Что снимать:**
- Форма загрузки плагина
- Список загруженных плагинов
- Preview модальное окно с iframe и логом событий
- Кнопки "Опубликовать", "Скрыть", "Удалить"

---

### 5. Analytics.vue - Аналитика

**Путь:** `/analytics`  
**Доступ:** Требуется авторизация  
**Файл:** `src/pages/Analytics.vue`

#### Функциональность

Отображает статистику пользователя: общее время, количество вопросов, точность, пройденные темы, статистику по навыкам.

#### Пример кода (общая статистика)

```vue
<!-- Общая статистика -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
  <Card>
    <div>
      <span class="text-sm text-gray-500 block mb-1">Жалпы уақыт</span>
      <p class="text-2xl font-bold">{{ formatTime(analyticsStore.totalTime) }}</p>
    </div>
  </Card>

  <Card>
    <div>
      <span class="text-sm text-gray-500 block mb-1">Барлық сұрақтар</span>
      <p class="text-2xl font-bold">{{ analyticsStore.totalQuestions }}</p>
    </div>
  </Card>

  <Card>
    <div>
      <span class="text-sm text-gray-500 block mb-1">Дәлдік</span>
      <p class="text-2xl font-bold text-green-600">{{ analyticsStore.accuracy }}%</p>
    </div>
  </Card>

  <Card>
    <div>
      <span class="text-sm text-gray-500 block mb-1">Өткізілген тақырыптар</span>
      <p class="text-2xl font-bold text-blue-600">{{ completedTopics.length }}</p>
    </div>
  </Card>
</div>
```

#### Пример кода (статистика по навыкам)

```vue
<!-- Статистика по навыкам -->
<table class="min-w-full divide-y divide-gray-200">
  <thead class="bg-gray-50">
    <tr>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дағды</th>
      <th v-if="authStore.isAuthenticated" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
        Ең жақсы SmartScore
      </th>
      <th v-if="authStore.isAuthenticated" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
        Соңғы SmartScore
      </th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Сұрақтар</th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дәлдік</th>
    </tr>
  </thead>
  <tbody class="bg-white divide-y divide-gray-200">
    <tr v-for="skill in analyticsStore.skills" :key="skill.skill_id">
      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
        {{ (skillNames.value && skillNames.value.get(skill.skill_id)) || `Дағды ${skill.skill_id}` }}
      </td>
      <td v-if="authStore.isAuthenticated" class="px-6 py-4 whitespace-nowrap text-sm font-semibold" :class="{
        'text-green-600': (skill.best_smartscore || 0) >= 90,
        'text-blue-600': (skill.best_smartscore || 0) >= 70 && (skill.best_smartscore || 0) < 90,
        'text-yellow-600': (skill.best_smartscore || 0) < 70
      }">
        {{ skill.best_smartscore || 0 }}
      </td>
      <td v-if="authStore.isAuthenticated" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {{ skill.last_smartscore || 0 }}
      </td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {{ skill.total_questions || 0 }}
      </td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {{ skill.accuracy_percent || 0 }}%
      </td>
    </tr>
  </tbody>
</table>
```

#### Ключевые моменты

1. **Условное отображение SmartScore** - только для авторизованных
2. **Цветовая индикация** - зеленый/синий/желтый в зависимости от SmartScore
3. **Кэширование** - данные кэшируются в localStorage

#### 📸 Скриншот

**Что снимать:**
- Общая статистика (время, вопросы, точность)
- Список навыков с SmartScore
- Пройденные темы

---

### 6. Profile.vue - Профиль пользователя

**Путь:** `/profile`  
**Доступ:** Требуется авторизация  
**Файл:** `src/pages/Profile.vue`

#### Функциональность

Отображает личную информацию пользователя: имя, email, роль, класс, статус подписки.

#### Пример кода

```vue
<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-6">Профиль</h1>

      <div v-if="authStore.user" class="bg-white rounded-lg shadow-md p-6">
        <div class="mb-6">
          <h2 class="text-xl font-semibold mb-4">Жеке ақпарат</h2>
          <div class="space-y-3">
            <div>
              <span class="text-sm text-gray-500">Аты-жөні:</span>
              <p class="text-lg font-medium">{{ authStore.user.full_name }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Email:</span>
              <p class="text-lg font-medium">{{ authStore.user.email }}</p>
            </div>
            <div>
              <span class="text-sm text-gray-500">Рөл:</span>
              <p class="text-lg font-medium">{{ getRoleText(authStore.user.role) }}</p>
            </div>
            <div v-if="authStore.user.profile">
              <span class="text-sm text-gray-500">Сынып:</span>
              <p class="text-lg font-medium">{{ authStore.user.profile.grade_level }}</p>
            </div>
            <div v-if="authStore.user.subscription">
              <span class="text-sm text-gray-500">Жазылым:</span>
              <p class="text-lg font-medium">
                {{ authStore.user.subscription.plan === 'PREMIUM' ? 'Премиум' : 'Тегін' }}
                <span :class="[
                  'ml-2 px-2 py-1 rounded text-xs',
                  authStore.user.subscription.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800',
                ]">
                  {{ authStore.user.subscription.is_active ? 'Белсенді' : 'Белсенді емес' }}
                </span>
              </p>
            </div>
          </div>
        </div>

        <div class="flex gap-4">
          <Button @click="handleLogout" variant="danger">Шығу</Button>
        </div>
      </div>
    </main>
    <Footer />
  </div>
</template>
```

#### 📸 Скриншот

**Что снимать:** Профиль пользователя с информацией и кнопкой выхода

---

### 7. PracticeResults.vue - Результаты сессии

**Путь:** `/practice/:sessionId/results`  
**Доступ:** Без авторизации  
**Файл:** `src/pages/PracticeResults.vue`

#### Функциональность

Отображает итоговые результаты сессии практики.

#### Пример кода

```vue
<div class="bg-white rounded-lg shadow-md p-6 mb-6">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <div v-if="authStore.isAuthenticated">
      <span class="text-sm text-gray-500 block mb-1">SmartScore</span>
      <p class="text-3xl font-bold text-blue-600">{{ session.smartscore }}</p>
    </div>
    <div>
      <span class="text-sm text-gray-500 block mb-1">Дұрыс</span>
      <p class="text-3xl font-bold text-green-600">{{ session.correct_count }}</p>
    </div>
    <div>
      <span class="text-sm text-gray-500 block mb-1">Қате</span>
      <p class="text-3xl font-bold text-red-600">{{ session.wrong_count }}</p>
    </div>
    <div>
      <span class="text-sm text-gray-500 block mb-1">Уақыт</span>
      <p class="text-3xl font-bold">{{ formatTime(session.time_elapsed_sec) }}</p>
    </div>
  </div>

  <div class="mb-6">
    <h2 class="text-xl font-semibold mb-2">Дәлдік</h2>
    <div class="w-full bg-gray-200 rounded-full h-4">
      <div
        class="bg-green-600 h-4 rounded-full transition-all"
        :style="{ width: `${accuracy}%` }"
      ></div>
    </div>
    <p class="mt-2 text-sm text-gray-600">{{ accuracy }}% дұрыс жауаптар</p>
  </div>
</div>
```

#### Ключевые моменты

1. **Условное отображение SmartScore** - только для авторизованных
2. **Визуализация точности** - progress bar
3. **Форматирование времени** - минуты:секунды

#### 📸 Скриншот

**Что снимать:** Результаты сессии с метриками и progress bar

---

### 8. SkillView.vue - Детали навыка

**Путь:** `/skill/:skillId`  
**Доступ:** Требуется авторизация  
**Файл:** `src/pages/SkillView.vue`

#### Функциональность

Отображает детальную информацию о навыке и статистику пользователя.

#### Пример кода

```vue
<div class="bg-white rounded-lg shadow-md p-6 mb-6">
  <h1 class="text-3xl font-bold mb-4">{{ skill.title }}</h1>
  <p class="text-gray-600 mb-4">{{ skill.description || 'Описание отсутствует' }}</p>

  <div class="flex flex-wrap gap-4 mb-4">
    <div>
      <span class="text-sm text-gray-500">Код:</span>
      <span class="ml-2 font-medium">{{ skill.code }}</span>
    </div>
    <div>
      <span class="text-sm text-gray-500">Сложность:</span>
      <span class="ml-2 font-medium">{{ skill.difficulty }}/5</span>
    </div>
  </div>

  <div v-if="skill.tags.length > 0" class="flex flex-wrap gap-2 mb-6">
    <span
      v-for="tag in skill.tags"
      :key="tag"
      class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
    >
      {{ tag }}
    </span>
  </div>

  <div class="flex gap-4">
    <Button
      @click="startPractice"
      :loading="startingPractice"
      variant="primary"
      class="text-lg px-6 py-3"
    >
      Начать практику
    </Button>
  </div>
</div>

<div v-if="stats" class="bg-white rounded-lg shadow-md p-6">
  <h2 class="text-xl font-semibold mb-4">Ваша статистика</h2>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div v-if="authStore.isAuthenticated">
      <span class="text-sm text-gray-500">SmartScore</span>
      <p class="text-2xl font-bold">{{ stats.smartscore || 0 }}</p>
    </div>
    <!-- ... -->
  </div>
</div>
```

#### Ключевые моменты

1. **Условное отображение SmartScore** - только для авторизованных
2. **Кнопка "Начать практику"** - создает сессию и переходит к практике

#### 📸 Скриншот

**Что снимать:** Страница навыка с описанием, тегами, кнопкой "Начать практику" и статистикой

---

### 9. Login.vue - Вход

**Путь:** `/auth/login`  
**Доступ:** Без авторизации  
**Файл:** `src/pages/auth/Login.vue`

#### Функциональность

Форма входа в систему.

#### Пример кода

```vue
<form class="mt-8 space-y-6" @submit.prevent="handleLogin">
  <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
    {{ error }}
  </div>

  <div class="rounded-md shadow-sm -space-y-px">
    <div>
      <label for="email" class="sr-only">Email</label>
      <input
        id="email"
        v-model="email"
        name="email"
        type="email"
        required
        class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        placeholder="Email"
      />
    </div>
    <div>
      <label for="password" class="sr-only">Құпия сөз</label>
      <input
        id="password"
        v-model="password"
        name="password"
        type="password"
        required
        class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        placeholder="Құпия сөз"
      />
    </div>
  </div>

  <div>
    <Button
      type="submit"
      :loading="authStore.loading"
      :disabled="!email || !password"
      variant="primary"
      class="w-full"
    >
      Кіру
    </Button>
  </div>
</form>
```

#### 📸 Скриншот

**Что снимать:** Форма входа с полями email и password

---

### 10. Register.vue - Регистрация

**Путь:** `/auth/register`  
**Доступ:** Без авторизации  
**Файл:** `src/pages/auth/Register.vue`

#### Функциональность

Форма регистрации нового пользователя.

#### Пример кода

```vue
<form class="mt-8 space-y-6" @submit.prevent="handleRegister">
  <div class="space-y-4">
    <div>
      <label for="full_name" class="block text-sm font-medium text-gray-700">
        Толық аты-жөні
      </label>
      <input
        id="full_name"
        v-model="fullName"
        name="full_name"
        type="text"
        required
        class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 rounded-md"
        placeholder="Аты-жөні"
      />
    </div>

    <div>
      <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
      <input
        id="email"
        v-model="email"
        name="email"
        type="email"
        required
        class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 rounded-md"
        placeholder="user@example.com"
      />
    </div>

    <div>
      <label for="password" class="block text-sm font-medium text-gray-700">Құпия сөз</label>
      <input
        id="password"
        v-model="password"
        name="password"
        type="password"
        required
        minlength="8"
        class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 rounded-md"
        placeholder="Кемінде 8 таңба"
      />
    </div>

    <div>
      <label for="role" class="block text-sm font-medium text-gray-700">Рөл</label>
      <select
        id="role"
        v-model="role"
        name="role"
        required
        class="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md"
      >
        <option value="STUDENT">Оқушы</option>
        <option value="TEACHER">Мұғалім</option>
        <option value="PARENT">Ата-ана</option>
      </select>
    </div>

    <div v-if="role === 'STUDENT'">
      <label for="grade_level" class="block text-sm font-medium text-gray-700">Сынып</label>
      <select
        id="grade_level"
        v-model.number="gradeLevel"
        name="grade_level"
        required
        class="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md"
      >
        <option v-for="n in 11" :key="n" :value="n">{{ n }}</option>
      </select>
    </div>
  </div>

  <div>
    <Button
      type="submit"
      :loading="authStore.loading"
      variant="primary"
      class="w-full"
    >
      Тіркелу
    </Button>
  </div>
</form>
```

#### 📸 Скриншот

**Что снимать:** Форма регистрации с полями и выбором роли

---

### 11. AdminQuestions.vue - Управление вопросами

**Путь:** `/admin/questions`  
**Доступ:** Только ADMIN  
**Файл:** `src/pages/AdminQuestions.vue`

#### Функциональность

Создание интерактивных заданий через вставку React кода.

#### Пример кода

```vue
<div class="bg-blue-50 border-l-4 border-blue-400 p-6 mb-6 rounded">
  <h2 class="text-xl font-semibold text-blue-800 mb-3">📋 Нұсқаулық</h2>
  <div class="space-y-3 text-gray-700">
    <div class="bg-white p-4 rounded border border-blue-200">
      <p class="font-semibold text-blue-900 mb-2">✅ Оңай 3 қадам:</p>
      <ol class="list-decimal list-inside space-y-1 ml-2">
        <li><strong>"Кодты кірістіру"</strong> бөліміне дайын React кодты толығымен көшіріп қойыңыз</li>
        <li><strong>"Сақтау"</strong> батырмасын басыңыз</li>
        <li>Готово! Тест автоматически появится у учеников</li>
      </ol>
    </div>
  </div>
</div>
```

#### 📸 Скриншот

**Что снимать:** Форма создания интерактивного задания с инструкциями

---

### 12. AdminSkills.vue - Управление навыками

**Путь:** `/admin/skills`  
**Доступ:** Только ADMIN  
**Файл:** `src/pages/AdminSkills.vue`

#### Функциональность

Создание навыков с код-генератором на Python.

#### Пример кода

```vue
<div class="bg-blue-50 border-l-4 border-blue-400 p-6 mb-6 rounded">
  <h2 class="text-xl font-semibold text-blue-800 mb-3">📋 Нұсқаулық</h2>
  <div class="space-y-3 text-gray-700">
    <div class="bg-white p-4 rounded border border-blue-200">
      <p class="font-semibold text-blue-900 mb-2">✅ Генератор қалай жұмыс істейді:</p>
      <ol class="list-decimal list-inside space-y-1 ml-2">
        <li>Сіз код-генераторды кірістіресіз</li>
        <li>Генератор әр сұрақ үшін жаңа тапсырмалар жасайды</li>
        <li>Тапсырмалар базада сақталмайды - олар динамикалық түрде жасалады</li>
        <li>Жауаптар генератор логикасы арқылы тексеріледі</li>
      </ol>
    </div>
    <div class="bg-green-50 p-3 rounded border border-green-200">
      <p class="text-sm text-green-800">
        <strong>💡 Важно:</strong> Генератор должен быть написан на <strong>Python</strong>! 
        Функция <code>generate(metadata)</code> должна возвращать словарь (dict) с полями:
        <code>prompt</code>, <code>type</code>, <code>data</code>, <code>correct_answer</code>, 
        <code>explanation</code> (опционально).
      </p>
    </div>
  </div>
</div>
```

#### 📸 Скриншот

**Что снимать:** Форма создания навыка с генератором

---

### 13. NotFound.vue - Страница 404

**Путь:** `/*`  
**Доступ:** Без авторизации  
**Файл:** `src/pages/NotFound.vue`

#### Функциональность

Отображает сообщение о несуществующей странице.

#### Пример кода

```vue
<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-gray-900 mb-4">404</h1>
      <p class="text-xl text-gray-600 mb-6">Бет табылмады</p>
      <router-link to="/">
        <Button variant="primary">Басты бетке</Button>
      </router-link>
    </div>
  </div>
</template>
```

---

## Компоненты

### Header.vue - Навигация

**Файл:** `src/components/layout/Header.vue`

#### Пример кода (навигационное меню)

```vue
<template>
  <header class="shadow-md" style="background-color: #38B000;">
    <nav class="container mx-auto px-4 py-3">
      <div class="flex items-center justify-between">
        <!-- Логотип -->
        <router-link to="/" class="flex items-center">
          <span class="text-white font-bold text-xl">Math Edu</span>
        </router-link>

        <!-- Навигация по центру -->
        <div class="flex items-center gap-6 absolute left-1/2 transform -translate-x-1/2">
          <router-link
            v-if="authStore.isAuthenticated"
            to="/"
            class="text-white hover:text-gray-100 transition-colors font-medium"
          >
            Менің Math Edu
          </router-link>
          
          <!-- Админ меню -->
          <div v-if="authStore.isAuthenticated && authStore.user?.role === 'ADMIN'" class="flex items-center gap-4">
            <router-link to="/admin/skills" class="text-white hover:text-gray-100 transition-colors font-medium">
              ⚙️ Админ
            </router-link>
            <router-link to="/admin/plugins" class="text-white hover:text-gray-100 transition-colors font-medium">
              🔌 Плагиндер
            </router-link>
            <router-link to="/admin/questions" class="text-white hover:text-gray-100 transition-colors font-medium">
              📝 Тапсырмалар
            </router-link>
          </div>
        </div>

        <!-- Профиль -->
        <div class="flex items-center gap-3">
          <div v-if="authStore.isAuthenticated" class="relative">
            <button
              @click="showProfileMenu = !showProfileMenu"
              class="flex items-center gap-2 rounded-full px-3 py-1.5 transition-colors"
            >
              <span class="text-white font-medium text-sm">{{ authStore.user?.full_name || 'Пайдаланушы' }}</span>
            </button>
            
            <!-- Выпадающее меню -->
            <div v-if="showProfileMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 z-50">
              <router-link to="/profile" @click="showProfileMenu = false" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">
                Профиль
              </router-link>
              <button @click="handleLogout" class="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100">
                Шығу
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  </header>
</template>
```

#### Ключевые моменты

1. **Условное отображение** - меню зависит от авторизации и роли
2. **Выпадающее меню** - профиль с опциями
3. **Роутинг** - использование `router-link`

#### 📸 Скриншот

**Что снимать:** Полный header с меню, выпадающим меню профиля, админ меню

---

### Footer.vue - Подвал

**Файл:** `src/components/layout/Footer.vue`

#### Пример кода

```vue
<template>
  <footer class="bg-gray-100 mt-auto">
    <div class="container mx-auto px-4 py-6">
      <div class="text-center text-gray-600">
        <p>&copy; 2024 Math Edu. Барлық құқықтар қорғалған.</p>
      </div>
    </div>
  </footer>
</template>
```

---

### Button.vue - Кнопка

**Файл:** `src/components/ui/Button.vue`

#### Пример кода

```vue
<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'px-4 py-2 rounded-lg font-medium transition-colors',
      {
        'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed':
          variant === 'primary',
        'bg-gray-200 text-gray-800 hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed':
          variant === 'secondary',
        'bg-red-600 text-white hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed':
          variant === 'danger',
        'bg-transparent border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed':
          variant === 'outline',
      },
      className,
    ]"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="inline-block mr-2">
      <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </span>
    <slot></slot>
  </button>
</template>
```

#### Варианты

- `primary` - синяя кнопка
- `secondary` - серая кнопка
- `danger` - красная кнопка
- `outline` - кнопка с обводкой

---

### Card.vue - Карточка

**Файл:** `src/components/ui/Card.vue`

#### Пример кода

```vue
<template>
  <div
    :class="[
      'bg-white rounded-lg shadow-md p-6',
      {
        'cursor-pointer hover:shadow-lg transition-shadow': clickable,
      },
      className,
    ]"
    @click="clickable && $emit('click', $event)"
  >
    <slot></slot>
  </div>
</template>
```

---

### Modal.vue - Модальное окно

**Файл:** `src/components/ui/Modal.vue`

#### Пример кода

```vue
<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="fixed inset-0 z-40 flex items-center justify-center p-4 bg-black bg-opacity-30" @click.self="close">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6 relative z-50">
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-xl font-semibold">{{ title }}</h3>
            <button
              v-if="showClose"
              @click="close"
              class="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="mb-6">
            <p class="text-gray-700">{{ message }}</p>
            <slot name="content"></slot>
          </div>
          
          <div class="flex gap-3 justify-end">
            <slot name="actions">
              <Button v-if="showClose" @click="close" variant="outline">Закрыть</Button>
            </slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
```

---

### InteractiveQuestion.vue - Интерактивный вопрос

**Файл:** `src/components/practice/InteractiveQuestion.vue`

#### Функциональность

Отображает интерактивные вопросы через iframe с React компонентами.

#### Пример кода

```vue
<template>
  <div class="interactive-question">
    <!-- Используем iframe для безопасного выполнения React кода -->
    <iframe
      v-if="iframeSrc"
      ref="questionFrame"
      :src="iframeSrc"
      class="w-full border-0 min-h-[600px] rounded-lg"
      sandbox="allow-scripts allow-same-origin allow-forms"
      @load="onIframeLoad"
    ></iframe>
    <div v-else class="text-center py-8 text-gray-500">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <p class="mt-4">Интерактивное задание загружается...</p>
    </div>
  </div>
</template>
```

---

## State Management (Pinia Stores)

### auth.ts - Авторизация

**Файл:** `src/stores/auth.ts`

#### Пример кода (логин)

```typescript
export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const user = ref<UserMeResponse | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value)
  const isStudent = computed(() => user.value?.role === 'STUDENT')
  const isTeacher = computed(() => user.value?.role === 'TEACHER' || user.value?.role === 'ADMIN')

  const login = async (credentials: AuthLoginRequest) => {
    loading.value = true
    try {
      const response = await authApi.login(credentials)
      if (response.data) {
        accessToken.value = response.data.access_token
        refreshToken.value = response.data.refresh_token
        user.value = response.data.user

        // Сохраняем в localStorage
        localStorage.setItem('access_token', response.data.access_token)
        localStorage.setItem('refresh_token', response.data.refresh_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))

        // Если пользователь имеет активную подписку, сбрасываем счетчик пробных вопросов
        const { useTrialQuestions } = await import('@/composables/useTrialQuestions')
        const trialQuestions = useTrialQuestions()
        if (response.data.user?.subscription?.is_active) {
          trialQuestions.resetTrialQuestions()
        }

        return response.data
      }
    } catch (error: any) {
      console.error('Login error:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    loading,
    isAuthenticated,
    isStudent,
    isTeacher,
    login,
    register,
    logout,
    fetchUser,
  }
})
```

#### Ключевые моменты

1. **Computed свойства** - реактивные вычисляемые значения
2. **localStorage** - сохранение токенов и данных пользователя
3. **Интеграция с composables** - сброс пробных вопросов при подписке

---

### catalog.ts - Каталог

**Файл:** `src/stores/catalog.ts`

#### Пример кода (кэширование)

```typescript
const CACHE_TTL = 5 * 60 * 1000 // 5 минут

const isStale = (key: string) => {
  const lastTime = lastFetch.value.get(key)
  if (!lastTime) return true
  return Date.now() - lastTime > CACHE_TTL
}

const getGrades = async (force = false) => {
  if (!force && !isStale('grades') && grades.value.length > 0) {
    return grades.value
  }

  loading.value = true
  try {
    const response = await catalogApi.getGrades()
    if (response.data) {
      grades.value = response.data
      lastFetch.value.set('grades', Date.now())
      
      // Сохраняем в localStorage для офлайн доступа
      localStorage.setItem('catalog_grades', JSON.stringify(response.data))
      localStorage.setItem('catalog_grades_time', Date.now().toString())
    }
    return grades.value
  } catch (error) {
    // Пробуем загрузить из localStorage при ошибке
    const cached = localStorage.getItem('catalog_grades')
    if (cached) {
      try {
        grades.value = JSON.parse(cached)
        return grades.value
      } catch (e) {
        console.error('Failed to parse cached grades', e)
      }
    }
    throw error
  } finally {
    loading.value = false
  }
}
```

---

### practice.ts - Практика

**Файл:** `src/stores/practice.ts`

#### Пример кода (создание сессии)

```typescript
const createSession = async (skillId: number) => {
  loading.value = true
  error.value = null
  
  const authStore = useAuthStore()
  
  try {
    const numericSkillId = typeof skillId === 'string' ? parseInt(skillId, 10) : skillId
    if (isNaN(numericSkillId)) {
      throw new Error('Invalid skill ID')
    }

    const response = await practiceApi.createSession({ skill_id: numericSkillId })
    if (response.data) {
      currentSession.value = response.data
      currentQuestion.value = response.data.current_question || null
      
      // Сохраняем в localStorage
      localStorage.setItem(`session_${numericSkillId}`, response.data.id)

      // Запускаем heartbeat
      startHeartbeat(response.data.id)

      // Сохраняем состояние
      saveSessionState()

      return response.data
    }
    throw new Error('Failed to create session')
  } catch (err: any) {
    // Обработка ошибок...
    throw err
  } finally {
    loading.value = false
  }
}
```

#### Пример кода (heartbeat)

```typescript
const startHeartbeat = (sessionId: string) => {
  // Останавливаем предыдущий heartbeat, если есть
  if (heartbeatTimer.value !== null) {
    clearInterval(heartbeatTimer.value)
  }

  // Отправляем heartbeat каждые 30 секунд
  heartbeatTimer.value = window.setInterval(async () => {
    try {
      await practiceApi.heartbeat(sessionId)
      lastActivity.value = Date.now()
    } catch (err) {
      console.error('Heartbeat error:', err)
    }
  }, HEARTBEAT_INTERVAL) // 30000 мс = 30 секунд
}
```

#### Пример кода (отправка ответа)

```typescript
const submitAnswer = async (
  sessionId: string,
  data: PracticeSubmitRequest
): Promise<PracticeSubmitResponse | null> => {
  if (!currentSession.value) return null

  loading.value = true
  error.value = null

  try {
    const response = await practiceApi.submitAnswer(
      sessionId,
      data,
      (retryAfter) => {
        rateLimitMessage.value = `Слишком много запросов. Попробуйте через ${retryAfter} секунд.`
      }
    )

    if (response.data) {
      // Проверяем пробные вопросы и увеличиваем счетчик только для неавторизованных пользователей
      const authStore = useAuthStore()
      const trialQuestions = useTrialQuestions()
      
      // Увеличиваем счетчик пробных вопросов только для неавторизованных пользователей
      if (!authStore.isAuthenticated) {
        const newCount = trialQuestions.incrementTrialQuestions()
        console.log('Trial questions count:', newCount)
        
        // Если пробные вопросы исчерпаны, отмечаем это
        if (newCount >= trialQuestions.TRIAL_QUESTIONS_LIMIT) {
          console.log('Trial questions exhausted')
        }
      }

      currentSession.value = response.data.session
      currentQuestion.value = response.data.next_question || null

      if (response.data.finished) {
        // Сессия завершена
        stopHeartbeat()
        await finishSession(sessionId)
        router.push({
          name: 'practice-results',
          params: { sessionId },
        })
      }

      saveSessionState()
      return response.data
    }
    throw new Error('Failed to submit answer')
  } catch (err: any) {
    // Обработка ошибки 402 (Payment Required)
    if (err.response?.status === 402) {
      const authStore = useAuthStore()
      const trialQuestions = useTrialQuestions()
      
      // Для авторизованных пользователей ошибка 402 не должна возникать
      if (authStore.isAuthenticated) {
        error.value = 'Қол жеткізу қатесі. Қайталап көріңіз.'
        throw err
      }
      // Если пользователь не авторизован и пробные вопросы исчерпаны
      if (trialQuestions.isTrialQuestionsExhausted.value) {
        error.value = 'Сіз бүгін барлық сынақ сұрақтарды пайдаландыңыз. Шексіз қол жеткізу үшін жүйеге кіріңіз.'
        throw err
      }
    }
    throw err
  } finally {
    loading.value = false
  }
}
```

---

### analytics.ts - Аналитика

**Файл:** `src/stores/analytics.ts`

#### Пример кода

```typescript
export const useAnalyticsStore = defineStore('analytics', () => {
  const overview = ref<AnalyticsOverview | null>(null)
  const skills = ref<AnalyticsSkills>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetch = ref<number>(0)

  const isStale = computed(() => {
    return Date.now() - lastFetch.value > CACHE_TTL
  })

  const totalTime = computed(() => {
    return overview.value?.total_time_sec || overview.value?.total_time || 0
  })

  const totalQuestions = computed(() => {
    return overview.value?.total_questions_answered || overview.value?.total_questions || 0
  })

  const accuracy = computed(() => {
    // Используем avg_accuracy_percent из API, если доступен
    if (overview.value?.avg_accuracy_percent !== undefined) {
      return overview.value.avg_accuracy_percent
    }
    // Иначе вычисляем из total и correct_count
    const total = totalQuestions.value
    const correct = overview.value?.correct_count || 0
    if (total === 0) return 0
    return Math.round((correct / total) * 100)
  })

  const getOverview = async (force = false) => {
    if (!force && !isStale.value && overview.value) {
      return overview.value
    }

    loading.value = true
    error.value = null
    try {
      const response = await analyticsApi.getOverview()
      if (response.data) {
        overview.value = response.data
        lastFetch.value = Date.now()

        // Сохраняем в localStorage для кэша
        localStorage.setItem('analytics_overview', JSON.stringify(response.data))
        localStorage.setItem('analytics_overview_time', lastFetch.value.toString())
      }
      return overview.value
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to fetch overview'
      error.value = errorMsg

      // Пробуем загрузить из localStorage
      const cached = localStorage.getItem('analytics_overview')
      if (cached) {
        try {
          overview.value = JSON.parse(cached)
          return overview.value
        } catch (e) {
          console.error('Failed to parse cached overview', e)
        }
      }

      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    overview,
    skills,
    loading,
    error,
    totalTime,
    totalQuestions,
    accuracy,
    getOverview,
    getSkills,
  }
})
```

---

## API клиенты

### client.ts - Базовый HTTP клиент

**Файл:** `src/api/client.ts`

#### Пример кода (Request Interceptor)

```typescript
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Получаем токен из localStorage напрямую
    const token = localStorage.getItem('access_token')
    
    // Добавляем токен только если он есть
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Добавляем Idempotency-Key для операций, требующих идемпотентности
    const idempotentMethods = ['POST', 'PUT', 'PATCH']
    if (idempotentMethods.includes(config.method?.toUpperCase() || '')) {
      // Генерируем новый ключ для каждой попытки
      if (!idempotencyKey || config.url?.includes('/submit') || config.url?.includes('/attempts')) {
        idempotencyKey = uuidv4()
      }
      config.headers['Idempotency-Key'] = idempotencyKey
    }

    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)
```

#### Пример кода (Response Interceptor - Refresh Token)

```typescript
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Обработка 401 - токен истёк
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('refresh_token')

      if (!refreshToken) {
        // Для пробных вопросов не требуется авторизация
        return Promise.reject(error)
      }

      if (isRefreshing) {
        // Если уже идёт refresh, добавляем запрос в очередь
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`
            }
            return apiClient(originalRequest)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        // Пробуем обновить токен
        const response = await axios.post<ApiResponse>(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken }
        )

        const newAccessToken = response.data?.data?.access_token
        if (newAccessToken) {
          // Обновляем токен в localStorage и store
          localStorage.setItem('access_token', newAccessToken)
          if ((window as any).__authStore) {
            ;(window as any).__authStore.setAccessToken(newAccessToken)
          }

          // Обрабатываем очередь запросов
          processQueue(null, newAccessToken)
          isRefreshing = false

          // Повторяем оригинальный запрос
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          }
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        processQueue(refreshError as Error, null)
        isRefreshing = false
        if ((window as any).__authStore) {
          ;(window as any).__authStore.logout()
        }
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)
```

#### Ключевые моменты

1. **Автоматическое добавление токена** - в каждом запросе
2. **Idempotency Key** - для предотвращения дублирования
3. **Автоматический refresh** - при истечении токена
4. **Очередь запросов** - во время refresh

---

### admin.ts - API админки

**Файл:** `src/api/admin.ts`

#### Пример кода

```typescript
export const adminApi = {
  async uploadPlugin(file: File): Promise<ApiResponse<Record<string, any>>> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post<ApiResponse<Record<string, any>>>(
      '/admin/plugins/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  async listPlugins(): Promise<ApiResponse<Array<Record<string, any>>>> {
    const response = await apiClient.get<ApiResponse<Array<Record<string, any>>>>(
      '/admin/plugins'
    )
    return response.data
  },

  async publishPlugin(
    pluginId: string,
    isPublished: boolean
  ): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.post<ApiResponse<Record<string, any>>>(
      `/admin/plugins/${pluginId}/publish?is_published=${isPublished}`,
      null
    )
    return response.data
  },

  async deletePlugin(pluginId: string): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.delete<ApiResponse<Record<string, any>>>(
      `/admin/plugins/${pluginId}`
    )
    return response.data
  },
}
```

---

### practice.ts - API практики

**Файл:** `src/api/practice.ts`

#### Пример кода

```typescript
export const practiceApi = {
  async createSession(
    data: PracticeSessionCreateRequest
  ): Promise<ApiResponse<PracticeSessionResponse>> {
    const response = await apiClient.post<ApiResponse<PracticeSessionResponse>>(
      '/practice/sessions',
      data
    )
    return response.data
  },

  async submitAnswer(
    sessionId: string,
    data: PracticeSubmitRequest,
    onRateLimit?: (retryAfter: number) => void
  ): Promise<ApiResponse<PracticeSubmitResponse>> {
    return rateLimitedAttempt(
      async () => {
        const response = await apiClient.post<ApiResponse<PracticeSubmitResponse>>(
          `/practice/sessions/${sessionId}/submit`,
          data
        )
        return response.data
      },
      onRateLimit
    )
  },
}
```

---

## Роутинг и защита

### router/index.ts

**Файл:** `src/router/index.ts`

#### Пример кода (Navigation Guard)

```typescript
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Если роут требует аутентификацию
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Редирект на логин с сохранением redirect параметра
      next({ name: 'login', query: { redirect: to.fullPath } })
    } else {
      // Проверяем, есть ли данные пользователя
      if (!authStore.user) {
        try {
          await authStore.fetchUser()
        } catch (error) {
          next({ name: 'login', query: { redirect: to.fullPath } })
          return
        }
      }
      
      // Проверяем роль, если требуется
      if (to.meta.requiresRole && authStore.user?.role !== to.meta.requiresRole) {
        next({ name: 'home' }) // Редирект на главную, если нет прав
        return
      }
      
      next()
    }
  } else {
    // Если роут не требует аутентификации
    if (to.name === 'login' || to.name === 'register') {
      if (authStore.isAuthenticated) {
        next({ name: 'home' })
      } else {
        next()
      }
    } else {
      next()
    }
  }
})
```

#### Ключевые моменты

1. **Проверка авторизации** - перед каждым переходом
2. **Проверка ролей** - для админских страниц
3. **Сохранение redirect** - для возврата после логина
4. **Автоматическая загрузка пользователя** - если токен есть, но данных нет

---

## Особенности реализации

### Кэширование

#### Пример (CatalogStore)

```typescript
const CACHE_TTL = 5 * 60 * 1000 // 5 минут

const isStale = (key: string) => {
  const lastTime = lastFetch.value.get(key)
  if (!lastTime) return true
  return Date.now() - lastTime > CACHE_TTL
}

const getGrades = async (force = false) => {
  if (!force && !isStale('grades') && grades.value.length > 0) {
    return grades.value
  }

  loading.value = true
  try {
    const response = await catalogApi.getGrades()
    if (response.data) {
      grades.value = response.data
      lastFetch.value.set('grades', Date.now())
      
      // Сохраняем в localStorage для офлайн доступа
      localStorage.setItem('catalog_grades', JSON.stringify(response.data))
      localStorage.setItem('catalog_grades_time', Date.now().toString())
    }
    return grades.value
  } catch (error) {
    // Пробуем загрузить из localStorage при ошибке
    const cached = localStorage.getItem('catalog_grades')
    if (cached) {
      try {
        grades.value = JSON.parse(cached)
        return grades.value
      } catch (e) {
        console.error('Failed to parse cached grades', e)
      }
    }
    throw error
  } finally {
    loading.value = false
  }
}
```

### Пробные вопросы

#### Пример (useTrialQuestions.ts)

**Файл:** `src/composables/useTrialQuestions.ts`

```typescript
const TRIAL_QUESTIONS_LIMIT = 10
const TRIAL_QUESTIONS_KEY = 'trial_questions_count'
const TRIAL_QUESTIONS_DATE_KEY = 'trial_questions_date'

export function useTrialQuestions() {
  const getTodayDate = (): string => {
    const today = new Date()
    return today.toISOString().split('T')[0] // YYYY-MM-DD
  }

  const checkAndResetIfNeeded = (): void => {
    const savedDate = localStorage.getItem(TRIAL_QUESTIONS_DATE_KEY)
    const today = getTodayDate()
    
    // Если дата изменилась, сбрасываем счетчик
    if (!savedDate || savedDate !== today) {
      localStorage.setItem(TRIAL_QUESTIONS_KEY, '0')
      localStorage.setItem(TRIAL_QUESTIONS_DATE_KEY, today)
    }
  }

  const incrementTrialQuestions = (): number => {
    checkAndResetIfNeeded()
    const current = getTrialQuestionsCount()
    const newCount = current + 1
    localStorage.setItem(TRIAL_QUESTIONS_KEY, newCount.toString())
    localStorage.setItem(TRIAL_QUESTIONS_DATE_KEY, getTodayDate())
    return newCount
  }

  const isTrialQuestionsExhausted = computed(() => {
    return getTrialQuestionsCount() >= TRIAL_QUESTIONS_LIMIT
  })

  return {
    getTrialQuestionsCount,
    incrementTrialQuestions,
    resetTrialQuestions,
    canUseTrialQuestions,
    remainingTrialQuestions,
    isTrialQuestionsExhausted,
    TRIAL_QUESTIONS_LIMIT,
  }
}
```

---

## Новые функции (Плагины)

### Система плагинов

#### Архитектура

1. **Загрузка** - ZIP архив с manifest.json
2. **Валидация** - JSON Schema проверка
3. **Хранение** - `/static/plugins/{plugin_id}/{version}/`
4. **Preview** - iframe с postMessage
5. **Публикация** - управление видимостью

#### PostMessage контракт

```typescript
// Плагин → Платформа
{
  type: 'INIT',
  // Плагин готов к работе
}

{
  type: 'SUBMIT',
  taskId: 'uuid',
  userAnswer: {
    // Данные ответа
  }
}

// Платформа → Плагин
{
  type: 'SERVER_RESULT',
  correct: boolean,
  score: number,
  explanation: string
}
```

---

## Инструкции для скриншотов

### 1. Главная страница (Home)
- **URL:** `http://localhost:5173/`
- **Что снимать:** Сетка карточек с классами (1 класс, 2 класс, и т.д.)

### 2. Просмотр класса (ClassView)
- **URL:** `http://localhost:5173/class/1`
- **Что снимать:** 
  - Боковая панель с классами (полукруглые кнопки)
  - Список навыков с цветовой индикацией SmartScore
  - Иконки галочек для пройденных навыков

### 3. Сессия практики (PracticeSession)
- **URL:** `http://localhost:5173/practice/{sessionId}`
- **Что снимать:**
  - Вопрос с вариантами ответов
  - Результат после ответа (зеленый/красный блок)
  - SmartScore и зона (для авторизованных)
  - Таймер и счетчики

### 4. Аналитика (Analytics)
- **URL:** `http://localhost:5173/analytics`
- **Что снимать:**
  - Общая статистика (время, вопросы, точность)
  - Список навыков с SmartScore
  - Пройденные темы

### 5. Управление плагинами (AdminPlugins) ⭐
- **URL:** `http://localhost:5173/admin/plugins`
- **Что снимать:**
  - Форма загрузки плагина
  - Список загруженных плагинов
  - Preview модальное окно с iframe и логом событий
  - Кнопки управления (Опубликовать, Скрыть, Удалить)

### 6. Навигация (Header)
- **Что снимать:**
  - Полный header с меню
  - Выпадающее меню профиля
  - Админ меню (для ADMIN)

---

## Статистика проекта

- **Страниц:** 13
- **Компонентов:** 8
- **Stores:** 5
- **API клиентов:** 6
- **Composables:** 2
- **Роутов:** 13

---

## Заключение

Фронтенд проекта Math Edu представляет собой современное SPA приложение на Vue 3 с полной типизацией TypeScript. Основные особенности:

1. ✅ **Модульная архитектура** - четкое разделение ответственности
2. ✅ **Безопасность** - защита роутов, проверка ролей, скрытие данных
3. ✅ **UX** - индикаторы загрузки, обработка ошибок, кэширование
4. ✅ **Новые функции** - система плагинов с postMessage интеграцией
5. ✅ **Адаптивность** - responsive дизайн для всех устройств

---

*Отчет составлен: 23 января 2026*