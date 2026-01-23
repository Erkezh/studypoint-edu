<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8 max-w-5xl">
      <div class="mb-6">
        <h1 class="text-3xl font-bold mb-2">Интерактивті тапсырма қосу</h1>
        <p class="text-gray-600">Мұнда сіз дайын кодты кірістіре аласыз</p>
      </div>

      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {{ error }}
      </div>

      <!-- Инструкция -->
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
          <div class="bg-green-50 p-3 rounded border border-green-200">
            <p class="text-sm text-green-800">
              <strong>💡 Важно:</strong> Вам не нужно ничего настраивать! Просто вставьте код - всё остальное система сделает автоматически:
            </p>
            <ul class="text-sm text-green-700 mt-2 space-y-1 list-disc list-inside ml-2">
              <li>Тест автоматически появится в системе</li>
              <li>Вопросы генерируются автоматически</li>
              <li>Ответы проверяются автоматически</li>
              <li>Вся логика работает из кода</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Форма создания интерактивного задания -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-6">Жаңа тапсырма қосу</h2>
        
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Навык ID полностью скрыт - создается автоматически -->
          <!-- Админу не нужно знать об этом -->

          <!-- Сұрақ мәтіні (скрыто, заполняется автоматически) -->
          <div v-if="showAdvanced" class="border-t pt-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Сұрақ мәтіні (автоматически)
            </label>
            <input
              v-model="formData.prompt"
              type="text"
              class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="Автоматты түрде кодтан анықталады"
            />
            <p class="text-xs text-gray-500 mt-1">Автоматически определяется из кода</p>
          </div>

          <!-- Кодты кірістіру -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Кодты кірістіру <span class="text-red-500">*</span>
            </label>
            <div class="bg-green-50 border-2 border-green-300 rounded-lg p-4 mb-2">
              <p class="text-sm text-green-800 font-medium mb-2">✅ Оңай:</p>
              <p class="text-sm text-green-700">
                Дайын React кодты толығымен көшіріп, төмендегі өріске қойыңыз. 
                Барлық қажетті ақпарат автоматты түрде анықталады!
              </p>
            </div>
            <textarea
              v-model="formData.component_code"
              @input="autoFillFromCode"
              required
              rows="25"
              class="w-full p-4 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none font-mono text-xs"
              placeholder="Мұнда React кодты кірістіріңіз... (Барлық қажетті ақпарат автоматты түрде анықталады)"
            ></textarea>
            <div v-if="autoFilled" class="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700">
              ✅ Автоматты түрде толтырылды: {{ autoFilledFields.join(', ') }}
            </div>
            <p class="text-xs text-gray-500 mt-1">
              💡 Кеңес: Бүкіл кодты (import-тан бастап export default-қа дейін) көшіріп қойыңыз
            </p>
          </div>

          <!-- Расширенные настройки (скрыты по умолчанию) -->
          <div v-if="showAdvanced" class="border-t pt-4 space-y-4">
            <h3 class="text-lg font-semibold text-gray-800">Расширенные настройки</h3>
            
            <!-- Навык создается автоматически - админу не нужно об этом знать -->
            <!-- skill_id всегда 0, система сама создаст новый навык -->
            
            <!-- Дұрыс жауап -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Дұрыс жауап (JSON)
              </label>
              <textarea
                v-model="correctAnswerJson"
                rows="4"
                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none font-mono text-sm"
                placeholder='Автоматты түрде кодтан анықталады'
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">
                Автоматты түрде кодтан анықталады
              </p>
            </div>

            <!-- Түсіндірме -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Түсіндірме
              </label>
              <textarea
                v-model="formData.explanation"
                rows="3"
                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                placeholder="Автоматически из кода"
              ></textarea>
            </div>

            <!-- Деңгей -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Деңгей (1-5)
              </label>
              <input
                v-model.number="formData.level"
                type="number"
                min="1"
                max="5"
                class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none"
                placeholder="1"
              />
              <p class="text-xs text-gray-500 mt-1">1 = ең оңай, 5 = ең қиын (по умолчанию: 1)</p>
            </div>
          </div>

          <!-- Кнопка показать/скрыть расширенные настройки -->
          <div class="text-center">
            <button
              type="button"
              @click="showAdvanced = !showAdvanced"
              class="text-sm text-blue-600 hover:text-blue-800 underline"
            >
              {{ showAdvanced ? 'Скрыть' : 'Показать' }} расширенные настройки
            </button>
          </div>

          <!-- Кнопки -->
          <div class="flex gap-4 pt-4">
            <Button type="submit" variant="primary" :loading="submitting" class="px-8">
              ✅ Сақтау
            </Button>
            <Button type="button" variant="outline" @click="resetForm">
              🔄 Тазалау
            </Button>
          </div>
        </form>
      </div>

      <!-- Пример кода -->
      <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-3">📝 Мысал коды:</h3>
        <p class="text-sm text-gray-600 mb-3">
          Төменде мысал көрсетілген. Осындай кодты көшіріп, жоғарыдағы өріске қойыңыз:
        </p>
        <div class="bg-white p-4 rounded border border-gray-300 overflow-x-auto">
          <pre class="text-xs"><code>{{ exampleCode }}</code></pre>
        </div>
        <button
          @click="copyExampleCode"
          class="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
        >
          📋 Мысал кодты көшіру
        </button>
      </div>

      <!-- Успешное создание -->
      <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
        ✅ {{ successMessage }}
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCatalogStore } from '@/stores/catalog'
import { adminApi } from '@/api/admin'
import router from '@/router'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Button from '@/components/ui/Button.vue'

const authStore = useAuthStore()
const loading = ref(false)
const submitting = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const correctAnswerJson = ref('{}')
const autoFilled = ref(false)
const autoFilledFields = ref<string[]>([])
const showAdvanced = ref(false)

const formData = ref({
  skill_id: 0,
  prompt: '',
  component_code: '',
  explanation: '',
  level: 1,
  metadata: {},
})

const exampleCode = ref(`import React, { useState, useEffect } from 'react';
import { RefreshCw, CheckCircle, XCircle, Brain, Award } from 'lucide-react';

const KazakhPlaceValueGenerator = () => {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState({ correct: 0, total: 0 });
  
  const placeValues = {
    ones: { kz: "бірліктер орны", en: "ones place" },
    tens: { kz: "ондықтар орны", en: "tens place" },
    hundreds: { kz: "жүздіктер орны", en: "hundreds place" },
  };

  const generateQuestion = () => {
    const number = Math.floor(Math.random() * 900) + 100;
    const place = 'ones';
    const correctAnswer = number % 10;
    
    setCurrentQuestion({
      number: number.toString(),
      place: place,
      question: \`\${number.toString()} санында \${placeValues[place].kz}нда қандай цифр тұр?\`,
      options: [correctAnswer, 1, 2, 3],
      correctAnswer: correctAnswer.toString(),
    });
  };

  const checkAnswer = () => {
    if (!currentQuestion) return;
    const isCorrect = selectedAnswer === currentQuestion.correctAnswer;
    setShowResult(true);
    setScore(prev => ({
      correct: prev.correct + (isCorrect ? 1 : 0),
      total: prev.total + 1
    }));
    if (isCorrect) {
      setTimeout(() => {
        generateQuestion();
      }, 1500);
    }
  };

  useEffect(() => {
    generateQuestion();
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Разрядтар</h1>
        
        {currentQuestion && (
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 text-center">
              {currentQuestion.question}
            </h2>
            
            <div className="text-center mb-6">
              <div className="text-4xl font-bold text-blue-600 font-mono">
                {currentQuestion.number}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 max-w-md mx-auto">
              {currentQuestion.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedAnswer(option.toString())}
                  disabled={showResult}
                  className={\`p-3 rounded-lg border-2 transition-all \${
                    selectedAnswer === option.toString()
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:border-gray-400 bg-white'
                  }\`}
                >
                  {option}
                </button>
              ))}
            </div>

            {!showResult && selectedAnswer && (
              <div className="text-center mt-6">
                <button
                  onClick={checkAnswer}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700"
                >
                  Жауапты тексеру
                </button>
              </div>
            )}

            {showResult && (
              <div className="mt-6 p-4 rounded-lg text-center">
                {selectedAnswer === currentQuestion.correctAnswer ? (
                  <div className="flex items-center justify-center gap-2 text-green-600">
                    <CheckCircle size={24} />
                    <span className="text-lg font-semibold">Дұрыс!</span>
                  </div>
                ) : (
                  <div className="text-red-600">
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <XCircle size={24} />
                      <span className="text-lg font-semibold">Қате!</span>
                    </div>
                    <div className="text-sm">
                      Дұрыс жауап: <span className="font-bold">{currentQuestion.correctAnswer}</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default KazakhPlaceValueGenerator;`)

const handleSubmit = async () => {
  submitting.value = true
  error.value = null
  successMessage.value = null

  // Проверяем авторизацию
  if (!authStore.isAuthenticated) {
    error.value = 'Жүйеге кіру қажет!'
    submitting.value = false
    return
  }

  // Проверяем роль
  if (authStore.user?.role !== 'ADMIN') {
    error.value = 'Тек әкімшілер тапсырма қоса алады!'
    submitting.value = false
    return
  }

  // Автоматически заполняем недостающие поля из кода
  if (formData.value.component_code) {
    autoFillFromCode()
  }

  // Проверяем обязательные поля
  if (!formData.value.component_code) {
    error.value = 'Кодты кірістіру міндетті!'
    submitting.value = false
    return
  }

  // Если prompt не заполнен или пустой, используем название компонента
  if (!formData.value.prompt || !formData.value.prompt.trim()) {
    const componentNameMatch = formData.value.component_code.match(/const\s+(\w+)\s*=|export\s+default\s+(\w+)|function\s+(\w+)/i)
    if (componentNameMatch) {
      const componentName = componentNameMatch[1] || componentNameMatch[2] || componentNameMatch[3]
      formData.value.prompt = componentName
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim() || 'Интерактивті тапсырма'
    } else {
      formData.value.prompt = 'Интерактивті тапсырма'
    }
  }
  
  // Убеждаемся, что prompt не пустой (убираем пробелы)
  formData.value.prompt = formData.value.prompt.trim() || 'Интерактивті тапсырма'

  try {
    let correctAnswer = {}
    if (correctAnswerJson.value.trim() && correctAnswerJson.value !== '{}') {
      try {
        correctAnswer = JSON.parse(correctAnswerJson.value)
      } catch (e) {
        // Если JSON невалидный, создаем простой объект
        correctAnswer = { answer: correctAnswerJson.value }
      }
    } else {
      // Если правильный ответ не указан, создаем пустой объект
      correctAnswer = {}
    }

    // Всегда создаем новый навык автоматически - админ просто вставляет код
    // Это упрощает процесс: админ не должен думать о skill_id
    let finalSkillId = 0
    // Удаляем проверку на skill_id - всегда создаем новый
    {
      try {
        // Используем API для получения subjects и grades
        const catalogStore = useCatalogStore()
        const subjects = await catalogStore.getSubjects()
        const grades = await catalogStore.getGrades()
        
        const firstSubject = subjects[0]
        const firstGrade = grades[0]
        
        if (firstSubject && firstGrade) {
          // Создаем навык через админ API
          const skillCode = `INTERACTIVE_${Date.now()}`
          
          // Убеждаемся, что prompt не пустой - если пустой, используем название из кода или дефолтное
          let skillTitle = (formData.value.prompt || '').trim()
          if (!skillTitle) {
            // Пытаемся извлечь название из кода
            const componentNameMatch = formData.value.component_code.match(/const\s+(\w+)\s*=|export\s+default\s+(\w+)|function\s+(\w+)/i)
            if (componentNameMatch) {
              const componentName = componentNameMatch[1] || componentNameMatch[2] || componentNameMatch[3]
              skillTitle = componentName
                .replace(/([A-Z])/g, ' $1')
                .replace(/^./, str => str.toUpperCase())
                .trim()
            }
          }
          
          // Если все еще пустой, используем дефолтное значение
          if (!skillTitle || skillTitle.length < 3) {
            skillTitle = 'Интерактивті тапсырма'
          }
          
          console.log('Creating skill:', { subject_id: firstSubject.id, grade_id: firstGrade.id, code: skillCode, title: skillTitle })
          
          const skillResponse = await adminApi.createSkill({
            subject_id: firstSubject.id,
            grade_id: firstGrade.id,
            code: skillCode,
            title: skillTitle,
            description: 'Автоматически созданный навык для интерактивного теста',
            is_published: true
          })
          
          console.log('Skill created:', skillResponse)
          
          if (!skillResponse.data || !skillResponse.data.id) {
            throw new Error('Не удалось получить ID созданного навыка')
          }
          
          finalSkillId = skillResponse.data.id
          console.log('Using skill_id:', finalSkillId)
          successMessage.value = `✅ Автоматически создан новый навык: ${skillTitle} (ID: ${finalSkillId})`
        } else {
          throw new Error('Не найдены предметы или классы для создания навыка')
        }
      } catch (err: any) {
        console.error('Failed to create skill:', err)
        const errorMsg = err.response?.data?.error?.message || err.response?.data?.message || err.message
        error.value = `Не удалось автоматически создать навык: ${errorMsg}. Обратитесь к разработчику.`
        submitting.value = false
        return
      }
    }
    // Всегда создаем новый навык - админ не должен указывать skill_id

    const requestData = {
      skill_id: finalSkillId,
      prompt: formData.value.prompt,
      component_code: formData.value.component_code,
      correct_answer: correctAnswer,
      explanation: formData.value.explanation || '',
      level: formData.value.level || 1,
      metadata: formData.value.metadata,
    }

    console.log('Sending request to create interactive question:', {
      url: '/admin/questions/interactive',
      data: { ...requestData, component_code: requestData.component_code.substring(0, 100) + '...' }
    })

    await adminApi.createInteractiveQuestion(requestData)

    // Успешно создано
    successMessage.value = 'Интерактивное задание успешно создано!'
    resetForm()
    setTimeout(() => {
      successMessage.value = null
    }, 5000)
  } catch (err: any) {
    console.error('Failed to create interactive question:', err)
    console.error('Error details:', {
      message: err.message,
      response: err.response?.data,
      status: err.response?.status,
      url: err.config?.url
    })
    
    if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error')) {
      error.value = 'Желі қатесі: Серверге қосылу мүмкін емес. Сервер жұмыс істеп тұрғанын тексеріңіз (http://localhost:8000).'
    } else if (err.response?.status === 401) {
      const errorDetail = err.response.data?.detail || err.response.data?.error
      if (errorDetail?.message) {
        error.value = `Авторизация қатесі: ${errorDetail.message}. Жүйеге қайта кіріңіз.`
      } else {
        error.value = 'Авторизация қажет! Токен мерзімі аяқталған болуы мүмкін. Жүйеге қайта кіріңіз.'
      }
      
      // Предлагаем перелогиниться через 2 секунды
      setTimeout(() => {
        if (confirm('Токен мерзімі аяқталған сияқты. Жүйеге қайта кіру керек пе?')) {
          router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
        }
      }, 2000)
    } else if (err.response?.status === 403) {
      error.value = 'Сізде бұл әрекетті орындауға рұқсат жоқ. Тек әкімшілер тапсырма қоса алады. Рөліңізді тексеріңіз.'
    } else if (err.response?.status === 404) {
      error.value = 'Endpoint табылмады. Сервер жаңартылғанын тексеріңіз.'
    } else {
      const errorMessage = err.response?.data?.message || err.response?.data?.detail?.message || err.message
      error.value = errorMessage || 'Тапсырма қосу кезінде қате пайда болды.'
    }
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  formData.value = {
    skill_id: 0,
    prompt: '',
    component_code: '',
    explanation: '',
    level: 1,
    metadata: {},
  }
  correctAnswerJson.value = '{}'
  error.value = null
  successMessage.value = null
}

const copyExampleCode = () => {
  navigator.clipboard.writeText(exampleCode.value)
  successMessage.value = 'Мысал код көшірілді! Енді оны жоғарыдағы өріске қойыңыз.'
  setTimeout(() => {
    successMessage.value = null
  }, 3000)
}

// Автоматическое заполнение полей из кода
const autoFillFromCode = () => {
  const code = formData.value.component_code
  if (!code || code.length < 50) {
    autoFilled.value = false
    autoFilledFields.value = []
    return
  }

  const filled: string[] = []

  // Извлекаем название компонента для prompt
  const componentNameMatch = code.match(/const\s+(\w+)\s*=|export\s+default\s+(\w+)|function\s+(\w+)/i)
  if (componentNameMatch) {
    const componentName = componentNameMatch[1] || componentNameMatch[2] || componentNameMatch[3]
    if (componentName && !formData.value.prompt) {
      // Пытаемся найти заголовок в коде
      const titleMatch = code.match(/h1[^>]*>([^<]+)|title[^>]*>([^<]+)|['"]([^'"]+)[^>]*>.*Разряд|Разряд[^<]*/i)
      if (titleMatch) {
        formData.value.prompt = titleMatch[1] || titleMatch[2] || titleMatch[3] || componentName
        filled.push('Сұрақ мәтіні')
      } else {
        formData.value.prompt = componentName.replace(/([A-Z])/g, ' $1').trim()
        filled.push('Сұрақ мәтіні')
      }
    }
  }

  // Извлекаем правильный ответ из логики компонента
  if (!correctAnswerJson.value || correctAnswerJson.value === '{}') {
    // Ищем проверку правильности ответа
    const correctAnswerMatch = code.match(/correctAnswer[:\s=]+['"]([^'"]+)['"]|correctAnswer[:\s=]+(\d+)|isCorrect.*===.*['"]([^'"]+)['"]|isCorrect.*===.*(\d+)/i)
    if (correctAnswerMatch) {
      const answer = correctAnswerMatch[1] || correctAnswerMatch[2] || correctAnswerMatch[3] || correctAnswerMatch[4]
      if (answer) {
        correctAnswerJson.value = JSON.stringify({ answer: answer })
        filled.push('Дұрыс жауап')
      }
    } else {
      // Ищем в currentQuestion
      const questionMatch = code.match(/correctAnswer[:\s=]+['"]([^'"]+)['"]|correctAnswer[:\s=]+(\d+)/i)
      if (questionMatch) {
        const answer = questionMatch[1] || questionMatch[2]
        if (answer) {
          correctAnswerJson.value = JSON.stringify({ answer: answer })
          filled.push('Дұрыс жауап')
        }
      }
    }
  }

  // Извлекаем explanation если есть
  if (!formData.value.explanation) {
    const explanationMatch = code.match(/explanation[:\s=]+['"]([^'"]+)['"]|Түсіндірме[:\s=]+['"]([^'"]+)['"]/i)
    if (explanationMatch) {
      formData.value.explanation = explanationMatch[1] || explanationMatch[2]
      filled.push('Түсіндірме')
    }
  }

  if (filled.length > 0) {
    autoFilled.value = true
    autoFilledFields.value = filled
  }
}

// Проверка прав доступа
if (!authStore.isAuthenticated || authStore.user?.role !== 'ADMIN') {
  error.value = 'Только администраторы могут создавать интерактивные задания'
}
</script>
