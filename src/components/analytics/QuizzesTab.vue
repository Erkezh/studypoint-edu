<template>
  <div class="quizzes-report-container p-2 md:p-4 bg-[#f3f7fc] min-h-screen">
    <div class="quizzes-report-inner">
      <!-- Тақырып жолы -->
    <div class="flex items-center gap-2 mb-6">
      <h1 class="text-3xl font-bold text-gray-800 tracking-tight">КВИЗ ТАЛДАУЫ</h1>
      <!-- Кесте белгішесі -->
      <svg class="w-6 h-6 text-gray-400 hover:text-cyan-600 transition cursor-pointer" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
      <!-- Анықтама белгішесі -->
      <span class="w-5 h-5 rounded-full border border-gray-300 text-gray-400 flex items-center justify-center text-xs font-medium hover:text-gray-600 cursor-pointer" title="Көмек">?</span>
    </div>

    <!-- Сүзгілер және басқару панелі -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6 bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
      <div class="flex flex-wrap items-center gap-3">
        <!-- Квиз таңдау -->
        <div class="flex items-center bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
          <span class="text-xs font-semibold text-gray-400 uppercase mr-2 tracking-wider">Квиз:</span>
          <select 
            v-model="selectedQuizId" 
            class="bg-transparent font-semibold text-gray-700 focus:outline-none text-sm min-w-[200px]"
          >
            <option value="">-- Квизді таңдаңыз --</option>
            <option v-for="quiz in availableQuizzes" :key="quiz.id" :value="quiz.id">
              {{ quiz.name }}
            </option>
          </select>
        </div>

        <!-- Оқушыны таңдау -->
        <div v-if="selectedQuiz && isTeacher" class="flex items-center bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
          <span class="text-xs font-semibold text-gray-400 uppercase mr-2 tracking-wider">Оқушы:</span>
          <select 
            v-model="selectedStudentFilter" 
            class="bg-transparent font-semibold text-gray-700 focus:outline-none text-sm min-w-[160px]"
          >
            <option value="all">Барлық оқушылар</option>
            <option v-for="student in reportStudents" :key="student.id" :value="student.id">
              {{ student.full_name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Ұпай түрін ауыстырып-қосқыш -->
      <div v-if="selectedQuiz" class="flex items-center gap-3">
        <span 
          class="text-xs font-semibold uppercase transition-colors cursor-pointer select-none"
          :class="scoreType === 'percent' ? 'text-cyan-600' : 'text-gray-400'"
          @click="scoreType = 'percent'"
        >
          Пайыздық ұпай
        </span>
        <!-- Ауыстырып-қосқыш (Switch) -->
        <button 
          @click="scoreType = scoreType === 'questions' ? 'percent' : 'questions'" 
          class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none bg-cyan-500"
        >
          <span 
            class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" 
            :class="scoreType === 'questions' ? 'translate-x-5' : 'translate-x-0'"
          ></span>
        </button>
        <span 
          class="text-xs font-semibold uppercase transition-colors cursor-pointer select-none"
          :class="scoreType === 'questions' ? 'text-cyan-600' : 'text-gray-400'"
          @click="scoreType = 'questions'"
        >
          Сұрақтар саны
        </span>
      </div>
    </div>

    <!-- Жүктелу күйі -->
    <div v-if="loading" class="report-loading flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500"></div>
    </div>

    <!-- Қате туралы хабарлама -->
    <div v-else-if="error" class="report-error bg-red-50 text-red-600 p-4 rounded-lg border border-red-100 mb-6">
      {{ error }}
    </div>

    <!-- Квиз таңдалмаған күй -->
    <div v-else-if="!selectedQuiz" class="report-empty bg-white p-12 rounded-xl border border-gray-100 shadow-sm text-center">
      <div class="empty-icon text-4xl mb-4">📋</div>
      <h3 class="text-lg font-bold text-gray-800 mb-2">Квиз таңдалмады</h3>
      <p class="text-sm text-gray-500">Толық аналитикалық есепті көру үшін жоғарыдағы мәзірден квизді таңдаңыз.</p>
    </div>

    <!-- Квиз нәтижелері мұғалім тарапынан шектелген күй -->
    <div v-else-if="!isTeacher && selectedQuizVisibility === 'HIDDEN'" class="report-empty bg-white p-12 rounded-xl border border-yellow-200 shadow-sm text-center">
      <div class="empty-icon text-4xl mb-4 text-yellow-500">🔒</div>
      <h3 class="text-lg font-bold text-gray-800 mb-2">Нәтижелер шектелген</h3>
      <p class="text-sm text-gray-600 max-w-md mx-auto">
        Мұғалім бұл квиздің нәтижелерін көрсетуді шектеген. Квиздің қорытынды нәтижелерін мұғаліміңізден сұрай аласыз.
      </p>
    </div>

    <!-- Квиз талдауының толық көрінісі -->
    <div v-else class="quiz-report-view max-w-full w-full space-y-6">
      
      <template v-if="selectedStudentFilter === 'all'">
        <!-- Қосымша беттердің навигациясы -->
        <div class="flex border-b border-gray-200 bg-transparent quiz-tabs-nav">
        <button 
          @click="activeSubTab = 'overview'" 
          class="px-6 py-3 font-semibold text-sm transition-all focus:outline-none border-b-2 -mb-[2px] tracking-wide" 
          :class="activeSubTab === 'overview' ? 'border-cyan-500 text-cyan-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
        >
          Жалпы шолу
        </button>
        <button 
          @click="activeSubTab = 'responses'" 
          class="px-6 py-3 font-semibold text-sm transition-all focus:outline-none border-b-2 -mb-[2px] tracking-wide" 
          :class="activeSubTab === 'responses' ? 'border-cyan-500 text-cyan-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
        >
          Оқушылардың жауаптары
        </button>
      </div>

      <!-- ==================== ЖАЛПЫ ШОЛУ БЕТІ (OVERVIEW) ==================== -->
      <div v-if="activeSubTab === 'overview'" class="space-y-6">
        
        <!-- Статистика мен график блогы -->
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
          
          <!-- Сол жақтағы статистикалық мәліметтер -->
          <div class="flex flex-col justify-center divide-y divide-gray-100">
            <!-- Тапсырғандар саны -->
            <div class="flex items-center gap-4 py-6">
              <div class="w-14 h-14 bg-cyan-50 rounded-full flex items-center justify-center text-cyan-600 shrink-0">
                <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <div>
                <div class="flex items-baseline gap-1.5">
                  <span class="text-4xl font-bold text-gray-800">{{ getCompletionStats(selectedQuiz).completed }}</span>
                  <span class="text-sm text-gray-400 font-medium">({{ getCompletionStats(selectedQuiz).total }} оқушының ішінен)</span>
                </div>
                <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mt-0.5">Тапсырылды</div>
              </div>
            </div>

            <!-- Сыныптың орташа ұпайы -->
            <div class="flex items-center gap-4 py-6">
              <div class="w-14 h-14 bg-cyan-50 rounded-full flex items-center justify-center text-cyan-600 shrink-0">
                <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <div class="text-4xl font-bold text-gray-800">
                  {{ getAverageScoreDisplay(selectedQuiz) }}
                </div>
                <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mt-0.5">Сыныптың орташа көрсеткіші</div>
              </div>
            </div>
          </div>

          <!-- Оң жақтағы бағандық диаграмма -->
          <div class="flex flex-col">
            <h3 class="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-6">Оқушылардың үлгерімі</h3>
            
            <div class="flex flex-1 items-end justify-between gap-2 h-44 pb-6 border-b border-gray-200 px-4">
              <!-- Диаграмма бағандары -->
              <div 
                v-for="(bucket, idx) in activeBuckets" 
                :key="idx" 
                class="flex flex-col items-center flex-1 group relative"
              >
                <!-- Баған үстіндегі мәліметтер -->
                <div class="absolute bottom-full mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded py-1 px-2 z-10 whitespace-nowrap shadow-md">
                  {{ bucket.count }} оқушы
                </div>

                <div class="flex items-center gap-0.5 text-xs font-extrabold text-gray-600 mb-1" v-if="bucket.count > 0">
                  <svg class="w-3 h-3 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                  </svg>
                  {{ bucket.count }}
                </div>
                <div class="text-xs font-bold text-gray-300 mb-1" v-else>0</div>

                <!-- Бағанның өзі -->
                <div 
                  class="w-8 sm:w-10 rounded-t transition-all duration-500 ease-out min-h-[4px]" 
                  :style="{ 
                    height: bucket.count > 0 ? ((bucket.count / maxBucketCount) * 100) + 'px' : '4px',
                    backgroundColor: bucket.count > 0 ? bucket.color : '#e5e7eb'
                  }"
                ></div>

                <!-- Диапазон атауы -->
                <div class="text-[10px] font-bold text-gray-500 mt-2 whitespace-nowrap">
                  {{ bucket.label }}
                </div>
              </div>

              <!-- Диаграмма жанындағы қосымша ақпарат -->
              <div class="flex flex-col text-[11px] font-bold text-gray-400 self-center pl-4 border-l border-gray-100 gap-1 min-w-[130px]">
                <div class="flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 bg-yellow-400 rounded-full"></span>
                  {{ inProgressCount }} орындалмаған
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 bg-gray-300 rounded-full"></span>
                  {{ notStartedCount }} басталмаған
                </div>
              </div>
            </div>
            
            <div class="text-[10px] font-bold text-gray-400 uppercase text-center mt-3 tracking-wider">
              {{ scoreType === 'questions' ? 'Дұрыс жауаптар саны' : 'Пайыздық ұпай аралықтары' }}
            </div>
          </div>
        </div>

        <!-- Оқушылардың нәтижелері (Скриншот 1) -->
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div class="relative flex justify-between items-center mb-6">
            <div class="absolute left-1/2 transform -translate-x-1/2">
              <h3 class="text-lg font-semibold text-gray-700">Оқушылардың ұпайлары</h3>
            </div>
            <div class="ml-auto flex items-center gap-2">
              <span class="text-xs font-semibold text-gray-400 uppercase">Сұрыптау:</span>
              <select 
                v-model="sortBy" 
                class="border border-gray-200 rounded-lg px-3 py-1 bg-gray-50 text-gray-700 font-semibold focus:outline-none text-xs"
              >
                <option value="score">Ұпай бойынша</option>
                <option value="name">Әліпби бойынша</option>
              </select>
            </div>
          </div>

          <!-- Топтастырылған оқушылар тізімі -->
          <div v-if="bucketStudents.length === 0" class="text-center py-6 text-gray-400 text-sm">
            Тапсырған оқушылар жоқ.
          </div>
          <div v-else class="space-y-3">
            <div 
              v-for="(group, idx) in bucketStudents" 
              :key="idx"
              class="flex items-center p-3 rounded-xl border border-gray-100 bg-white shadow-sm"
            >
              <!-- Түсті маркер -->
              <span 
                class="w-1.5 h-6 rounded shrink-0 mr-4"
                :style="{ backgroundColor: group.color }"
              ></span>
              
              <!-- Оқушылар тізімі -->
              <div class="flex flex-wrap items-center gap-x-12 gap-y-2">
                <div 
                  v-for="student in group.students" 
                  :key="student.id"
                  class="flex items-center gap-2"
                >
                  <span class="font-normal text-gray-700 text-sm">{{ student.full_name }}</span>
                  <span class="font-semibold text-gray-400 text-sm">
                    <span v-if="scoreType === 'questions'">{{ student.correctAnswers }} / {{ selectedQuiz.questions.length }}</span>
                    <span v-else>{{ student.score }}%</span>
                  </span>
                </div>
              </div>
            </div>

            <!-- Орындалып жатқан оқушылар (орындалмаған) -->
            <div 
              v-if="inProgressStudents.length > 0"
              class="flex items-center p-3 rounded-xl border border-gray-100 bg-white shadow-sm"
            >
              <span class="w-1.5 h-6 rounded shrink-0 mr-4 bg-yellow-400"></span>
              <div class="flex flex-wrap items-center gap-x-12 gap-y-2">
                <div 
                  v-for="student in inProgressStudents" 
                  :key="student.id"
                  class="flex items-center gap-2"
                >
                  <span class="font-normal text-gray-700 text-sm">{{ student.full_name }}</span>
                  <span class="text-xs font-semibold text-yellow-600 px-2 py-0.5 bg-yellow-50 rounded-md">Орындалмаған</span>
                </div>
              </div>
            </div>

            <!-- Bagystalmagan students -->
            <div 
              v-if="notStartedStudents.length > 0"
              class="flex items-center p-3 rounded-xl border border-gray-100 bg-white shadow-sm"
            >
              <span class="w-1.5 h-6 rounded shrink-0 mr-4 bg-gray-300"></span>
              <div class="flex flex-wrap items-center gap-x-12 gap-y-2">
                <div 
                  v-for="student in notStartedStudents" 
                  :key="student.id"
                  class="flex items-center gap-2"
                >
                  <span class="font-normal text-gray-700 text-sm">{{ student.full_name }}</span>
                  <span class="text-xs font-semibold text-gray-500 px-2 py-0.5 bg-gray-100 rounded-md">Басталмаған</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Жауаптарды талдау (Скриншот 2) -->
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <h3 class="text-lg font-bold text-gray-800 mb-6">Жауаптарды талдау</h3>
          
          <div class="overflow-x-auto">
            <table class="w-full min-w-[700px] border-collapse">
              <thead>
                <tr class="bg-[#00b0ff] text-white text-xs font-bold uppercase tracking-wider">
                  <th class="px-4 py-3 text-left">Сұрақ</th>
                  <th class="px-4 py-3 text-left">Оқушы нәтижелері</th>
                  <th class="px-4 py-3 text-left">Дағды</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr 
                  v-for="(q, idx) in selectedQuiz.questions" 
                  :key="q.id"
                  @click="goToResponses(idx)"
                  class="hover:bg-gray-50/50 transition cursor-pointer"
                >
                  <!-- Сұрақ бағаны (Иконкамен) -->
                  <td class="px-4 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-3">
                      <div class="w-7 h-7 bg-gray-100 rounded-full flex items-center justify-center text-gray-400 shrink-0 text-xs">
                        🔍
                      </div>
                      <span class="font-bold text-gray-800 text-sm">{{ idx + 1 }}</span>
                    </div>
                  </td>

                  <!-- Сынып нәтижесі (Пайыз және прогресс-бар) -->
                  <td class="px-4 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-3">
                      <span 
                        class="font-bold text-sm min-w-[40px] text-right"
                        :class="getQuestionStats(idx).correctPercent >= 70 ? 'text-[#7cb342]' : 'text-[#ff9800]'"
                      >
                        {{ getQuestionStats(idx).correctPercent }}%
                      </span>
                      <!-- Жасыл/Қызыл сегменттелген прогресс-бар -->
                      <div class="flex h-3.5 w-32 rounded-full overflow-hidden bg-gray-100 border border-gray-100 shrink-0">
                        <div 
                          class="bg-[#7cb342] transition-all duration-300" 
                          :style="{ width: getQuestionStats(idx).correctPercent + '%' }"
                        ></div>
                        <div 
                          class="bg-[#ff8a80] transition-all duration-300" 
                          :style="{ width: (100 - getQuestionStats(idx).correctPercent) + '%' }"
                        ></div>
                      </div>
                    </div>
                  </td>

                  <!-- Дағды және сілтеме -->
                  <td class="px-4 py-4">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div class="flex items-center gap-2 flex-wrap">
                        <span class="font-bold text-gray-800 text-sm">
                          {{ getQuestionSkillInfo(q.question?.skill_id).code }} {{ getQuestionSkillInfo(q.question?.skill_id).name }}
                        </span>
                        <!-- Дағды аббревиатурасының белгісі -->
                        <span v-if="getQuestionSkillInfo(q.question?.skill_id).code" class="px-1.5 py-0.5 bg-gray-100 text-gray-500 font-bold rounded text-[10px] uppercase">
                          {{ getQuestionSkillInfo(q.question?.skill_id).code.slice(0, 3) }}
                        </span>
                        <!-- Деңгей белгісі -->
                        <span class="px-1.5 py-0.5 bg-cyan-50 text-cyan-600 font-bold rounded text-[10px] uppercase">
                          Level {{ q.question?.level || 2 }}
                        </span>
                      </div>
                      
                      <!-- Сілтеме -->
                      <button 
                        @click.stop="goToResponses(idx)" 
                        class="text-cyan-600 hover:text-cyan-700 font-bold text-xs flex items-center gap-1 transition whitespace-nowrap cursor-pointer"
                      >
                        Оқушылардың жауаптарын көру &rarr;
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- ==================== ОҚУШЫ ЖАУАПТАРЫ БЕТІ (RESPONSES) ==================== -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        
        <!-- Сол жақтағы баған: Сұрақтар тізімі -->
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4 space-y-4">
          <div class="flex items-center justify-between border-b border-gray-100 pb-3">
            <span class="text-xs font-bold text-gray-400 uppercase">Сұрыптау:</span>
            <select class="border border-gray-200 rounded px-2 py-1 bg-gray-50 text-gray-700 font-bold focus:outline-none text-xs">
              <option>Сұрақ нөмірі</option>
            </select>
          </div>
          
          <div class="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            <div 
              v-for="(q, idx) in selectedQuiz.questions" 
              :key="q.id"
              @click="selectedQuestionIndex = idx"
              class="flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all duration-150"
              :class="selectedQuestionIndex === idx ? 'border-cyan-500 bg-[#e3f2fd]/40 font-semibold' : 'border-gray-50 hover:bg-gray-50'"
            >
              <!-- Сұрақ нөмірі -->
              <span class="text-lg font-extrabold text-gray-700 shrink-0 w-6 text-center">{{ idx + 1 }}</span>
              
              <!-- Мәліметтер -->
              <div class="min-w-0 flex-1 space-y-1">
                <div class="text-[11px] font-bold text-gray-500 truncate">
                  {{ getQuestionSkillInfo(q.question?.skill_id).code }} {{ getQuestionSkillInfo(q.question?.skill_id).name }}
                </div>
                
                <div class="flex items-center gap-2">
                  <span class="text-[10px] font-extrabold text-green-600">
                    {{ getQuestionStats(idx).correctPercent }}%
                  </span>
                  <!-- Сегменттелген шағын прогресс-бар -->
                  <div class="flex h-2 w-20 rounded-full overflow-hidden bg-gray-100 shrink-0">
                    <div class="bg-[#7cb342]" :style="{ width: getQuestionStats(idx).correctPercent + '%' }"></div>
                    <div class="bg-[#ff8a80]" :style="{ width: (100 - getQuestionStats(idx).correctPercent) + '%' }"></div>
                  </div>
                </div>
              </div>

              <!-- Деңгей белгішесі -->
              <div class="flex flex-col items-end gap-1 shrink-0">
                <span class="px-1 py-0.5 bg-cyan-50 text-cyan-600 font-bold rounded text-[8px] uppercase">
                  L{{ q.question?.level || 2 }}
                </span>
                <span v-if="getQuestionSkillInfo(q.question?.skill_id).code" class="px-1 py-0.5 bg-gray-100 text-gray-400 font-bold rounded text-[8px] uppercase">
                  {{ getQuestionSkillInfo(q.question?.skill_id).code.slice(0, 3) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Оң жақтағы баған: Сұрақтың толық мәліметтері мен оқушы жауаптары -->
        <div class="lg:col-span-2 bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-6">
          <!-- Сұрақ басы -->
          <div class="flex flex-wrap items-center justify-between gap-4 border-b border-gray-100 pb-4">
            <div>
              <h2 class="text-xl font-bold text-gray-900">Сұрақ {{ selectedQuestionIndex + 1 }}</h2>
              <p class="text-xs text-gray-500 font-bold mt-1">
                {{ getQuestionSkillInfo(selectedQuiz.questions[selectedQuestionIndex]?.question?.skill_id).code }}
                {{ getQuestionSkillInfo(selectedQuiz.questions[selectedQuestionIndex]?.question?.skill_id).name }}
              </p>
            </div>
            
            <div class="flex items-center gap-2">
              <span v-if="getQuestionSkillInfo(selectedQuiz.questions[selectedQuestionIndex]?.question?.skill_id).code" class="px-2 py-1 bg-gray-100 text-gray-500 font-bold rounded text-xs uppercase">
                {{ getQuestionSkillInfo(selectedQuiz.questions[selectedQuestionIndex]?.question?.skill_id).code.slice(0, 3) }}
              </span>
              <span class="px-2 py-1 bg-cyan-50 text-cyan-600 font-bold rounded text-xs uppercase">
                Деңгей {{ selectedQuiz.questions[selectedQuestionIndex]?.question?.level || 2 }}
              </span>
            </div>
          </div>

          <!-- Сұрақтың тапсырмасы (Prompt & Visual/Iframe Preview) -->
          <div class="bg-gray-50 border border-gray-100 rounded-xl p-6">
            <SessionQuestionPreview 
              v-if="selectedQuestionPreview" 
              :question="selectedQuestionPreview" 
            />
          </div>

          <!-- Оқушылардың жауаптарын талдау -->
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <h3 class="text-base font-bold text-gray-800">Оқушылардың жауаптары</h3>
              
              <!-- Оқушылардың барлығын көрсету ауыстырып-қосқышы -->
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-gray-500">Барлық оқушыларды көрсету</span>
                <button 
                  @click="showAllStudents = !showAllStudents" 
                  class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
                  :class="showAllStudents ? 'bg-cyan-500' : 'bg-gray-200'"
                >
                  <span 
                    class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" 
                    :class="showAllStudents ? 'translate-x-4' : 'translate-x-0'"
                  ></span>
                </button>
              </div>
            </div>

            <!-- Түрлі көріністер: Топтастырылған немесе Әр оқушы жеке -->
            <div v-if="!showAllStudents" class="space-y-4">
              <div 
                v-for="(group, gIdx) in getGroupedResponsesForQuestion(selectedQuestionIndex)" 
                :key="gIdx"
                class="p-4 rounded-xl border transition-all"
                :class="group.isCorrect ? 'bg-[#f8fcf5] border-green-100' : 'bg-[#fdf8f8] border-red-100'"
              >
                <!-- Plugin question: render answer as iframe -->
                <div v-if="isSelectedQuestionPlugin && group.rawAnswer" class="mb-2 rounded-lg border bg-white p-2 overflow-hidden" :class="group.isCorrect ? 'border-green-200' : 'border-red-200'">
                  <SessionQuestionPreview :question="buildResponsePreview(group.rawAnswer, group.isCorrect)!" />
                </div>
                <!-- Non-plugin question: render answer as text -->
                <div 
                  v-else
                  class="border rounded-lg bg-white px-4 py-3 font-semibold text-lg w-full max-w-sm mb-2 shadow-sm"
                  :class="group.isCorrect ? 'border-green-200 text-green-700' : 'border-red-200 text-red-700'"
                >
                  {{ group.answer }}
                </div>
                <!-- Статистика белгішесі мен тінтуірді апарғанда ашылатын оқушылар тізімі -->
                <div class="relative inline-block group mt-1">
                  <div 
                    class="text-xs font-extrabold inline-flex items-center gap-1.5 py-1 px-3 rounded-lg border transition-all cursor-pointer select-none"
                    :class="group.isCorrect ? 'text-[#558b2f] bg-green-50/80 border-green-200 hover:bg-green-100/80' : 'text-[#c62828] bg-red-50/80 border-red-200 hover:bg-red-100/80'"
                  >
                    <span v-if="group.isCorrect">✓ Дұрыс жауап: {{ group.students.length }} оқушы тапсырды</span>
                    <span v-else>✗ Қате жауап: {{ group.students.length }} оқушы тапсырды</span>
                    
                    <svg class="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 transition-opacity shrink-0 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>

                  <!-- Поповер терезесі (Тінтуірді апарғанда көрінеді - Светлая тема) -->
                  <div 
                    class="absolute left-0 bottom-full mb-2 hidden group-hover:block z-50 w-64 p-3.5 bg-white text-gray-800 rounded-xl shadow-xl border border-gray-200/80 text-xs transition-all duration-200 pointer-events-none"
                  >
                    <!-- Стрелка -->
                    <div class="absolute -bottom-1.5 left-6 w-3 h-3 bg-white rotate-45 border-r border-b border-gray-200/80"></div>

                    <div class="font-bold text-gray-800 border-b border-gray-100 pb-2 mb-2 flex items-center justify-between">
                      <span class="flex items-center gap-1.5">
                        <svg class="w-3.5 h-3.5 text-cyan-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                        Оқушылар тізімі
                      </span>
                      <span class="px-2 py-0.5 rounded-full text-[10px] bg-cyan-50 text-cyan-700 font-mono font-bold border border-cyan-100">{{ group.students.length }}</span>
                    </div>

                    <div v-if="group.students.length > 0" class="max-h-48 overflow-y-auto space-y-1.5 pr-1">
                      <div 
                        v-for="st in group.students" 
                        :key="st.id"
                        class="flex items-center gap-2.5 text-gray-700 font-medium py-1 px-1.5 rounded-lg hover:bg-gray-50 transition"
                      >
                        <div class="w-6 h-6 rounded-full bg-cyan-50 text-cyan-600 border border-cyan-200 flex items-center justify-center text-[10px] font-bold shrink-0">
                          {{ st.full_name ? st.full_name[0].toUpperCase() : 'S' }}
                        </div>
                        <span class="truncate text-xs font-semibold text-gray-800">{{ st.full_name }}</span>
                      </div>
                    </div>
                    <div v-else class="text-gray-400 italic py-1 text-center">
                      Бұл жауапты ешқандай оқушы белгілемеді
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="space-y-3">
              <div 
                v-for="student in filteredReportStudents" 
                :key="student.id"
                class="p-4 rounded-xl border flex items-center justify-between transition-all"
                :class="!student.completed ? 'bg-gray-50 border-gray-100' : student.questionDetails[selectedQuestionIndex]?.correct ? 'bg-[#f8fcf5] border-green-100' : 'bg-[#fdf8f8] border-red-100'"
              >
                <div class="flex items-center gap-2">
                  <span class="font-bold text-gray-800 text-sm">{{ student.full_name }}</span>
                </div>
                
                <div class="flex items-center gap-4">
                  <div 
                    class="border rounded-lg bg-white px-4 py-2 font-semibold text-sm w-44 shadow-sm truncate"
                    :class="!student.completed ? 'border-gray-200 text-gray-400' : student.questionDetails[selectedQuestionIndex]?.correct ? 'border-green-200 text-green-700' : 'border-red-200 text-red-700'"
                  >
                    {{ !student.completed ? 'Орындалмаған' : student.questionDetails[selectedQuestionIndex]?.submitted }}
                  </div>
                  
                  <div class="text-xs font-bold w-24">
                    <span v-if="!student.completed" class="text-gray-400">Тапсырмады</span>
                    <span v-else-if="student.questionDetails[selectedQuestionIndex]?.correct" class="text-[#7cb342]">✓ Дұрыс</span>
                    <span v-else class="text-[#ff8a80]">✗ Қате</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

    </template>

    <!-- If a specific student is selected, show their individual quiz results review -->
    <template v-else>
      
      <!-- Оқушы статистикасы & Сұрақтарды талдау -->
      <div>
        
        <!-- Оқушы статистикасы -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Дұрыс жауаптар саны -->
          <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm flex items-center gap-5">
            <div class="w-14 h-14 bg-green-50 rounded-full flex items-center justify-center text-green-500 shrink-0 text-xl font-bold">
              ✓
            </div>
            <div>
              <div class="text-2xl font-black text-gray-800 font-mono">
                <template v-if="currentStudentReport?.completed">
                  {{ currentStudentReport.correctAnswers }} <span class="text-gray-400 font-normal text-sm">/ {{ selectedQuiz.questions.length }}</span>
                </template>
                <template v-else>
                  - <span class="text-gray-400 font-normal text-sm">/ {{ selectedQuiz.questions.length }}</span>
                </template>
              </div>
              <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mt-0.5">Дұрыс жауаптар</div>
            </div>
          </div>

          <!-- Ұпайы -->
          <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm flex items-center gap-5">
            <div class="w-14 h-14 bg-blue-50 rounded-full flex items-center justify-center text-blue-500 shrink-0 text-xl font-bold">
              %
            </div>
            <div>
              <div class="text-2xl font-black text-blue-600 font-mono">
                <template v-if="currentStudentReport?.completed">
                  {{ currentStudentReport.score }}%
                </template>
                <template v-else>
                  -
                </template>
              </div>
              <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mt-0.5">Ұпайы</div>
            </div>
          </div>

          <!-- Жұмсалған уақыт -->
          <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-sm flex items-center gap-5">
            <div class="w-14 h-14 bg-cyan-50 rounded-full flex items-center justify-center text-cyan-500 shrink-0 text-xl font-bold">
              ⏱
            </div>
            <div>
              <div class="text-2xl font-black text-gray-800 font-mono">
                <template v-if="currentStudentReport?.completed">
                  {{ currentStudentReport.timeSpent }}
                </template>
                <template v-else>
                  -
                </template>
              </div>
              <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mt-0.5">Жұмсалған уақыт</div>
            </div>
          </div>
        </div>

        <!-- Сұрақтарды талдау блогы -->
        <div v-if="selectedQuizVisibility === 'ALWAYS'" class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden mt-6">
          <div class="bg-cyan-600 px-6 py-4">
            <h3 class="text-lg font-bold text-white">Сұрақтарды талдау</h3>
          </div>

          <div class="divide-y divide-gray-150">
            <div 
              v-for="(q, idx) in selectedQuiz.questions" 
              :key="q.id"
              class="flex border-b border-gray-100 last:border-b-0 bg-white"
            >
              <!-- Left border indicator -->
              <div 
                class="w-1.5 shrink-0" 
                :class="(currentStudentReport?.completed && currentStudentReport.questionResults[idx]) ? 'bg-green-500' : 'bg-red-500'"
              ></div>

              <div class="flex-1 flex gap-4 p-6 text-left">
                <!-- Number + icon -->
                <div class="flex flex-col items-center gap-1 shrink-0 w-14">
                  <span class="text-[11px] text-gray-400 text-center font-bold">
                    {{ idx + 1 }} / {{ selectedQuiz.questions.length }}
                  </span>
                  <span 
                    class="text-lg font-black"
                    :class="(currentStudentReport?.completed && currentStudentReport.questionResults[idx]) ? 'text-green-600' : 'text-red-500'"
                  >
                    {{ (currentStudentReport?.completed && currentStudentReport.questionResults[idx]) ? '✓' : '✗' }}
                  </span>
                </div>

                <!-- Content -->
                <div class="flex-1 min-w-0 space-y-6">
                  <!-- Header info -->
                  <div class="flex items-center justify-between border-b border-gray-100 pb-2">
                    <div>
                      <h4 class="text-sm font-bold text-gray-800">Сұрақ {{ idx + 1 }}</h4>
                      <p class="text-[10px] text-gray-400 font-bold mt-0.5">
                        Деңгей {{ q?.question?.level || 2 }}
                      </p>
                    </div>
                  </div>

                  <!-- Question Iframe/Prompt Preview -->
                  <div class="bg-gray-50 border border-gray-100 rounded-xl p-5">
                    <div class="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-2">Сұрақ:</div>
                    <SessionQuestionPreview 
                      :question="buildQuestionReview(q)"
                    />
                  </div>

                  <!-- Student and Correct Answers -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Student's submitted answer -->
                    <div class="space-y-2">
                      <div class="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
                        {{ currentStudentReport ? currentStudentReport.full_name : 'Оқушы' }} жауабы:
                      </div>
                      
                      <template v-if="currentStudentReport?.completed">
                        <!-- Plugin visual answer -->
                        <div v-if="isQuestionPluginType(q) && buildStudentResponseReview(q, currentStudentReport.questionDetails[idx]?.rawSubmitted, currentStudentReport.questionResults[idx])" class="rounded-xl border p-2 overflow-hidden bg-white shadow-sm" :class="currentStudentReport.questionResults[idx] ? 'border-green-200' : 'border-red-200'">
                          <SessionQuestionPreview :question="buildStudentResponseReview(q, currentStudentReport.questionDetails[idx]?.rawSubmitted, currentStudentReport.questionResults[idx])!" />
                        </div>

                        <!-- Textual fallback -->
                        <div 
                          v-else
                          class="border rounded-xl bg-white px-5 py-4 font-semibold text-lg shadow-sm"
                          :class="currentStudentReport.questionResults[idx] ? 'border-green-200 text-green-700 bg-green-50/20' : 'border-red-200 text-red-700 bg-red-50/20'"
                        >
                          {{ currentStudentReport.questionDetails[idx]?.submitted || '—' }}
                        </div>
                      </template>

                      <!-- If quiz was not completed / not answered -->
                      <template v-else>
                        <div class="border border-red-200 text-red-700 bg-red-50/20 rounded-xl bg-white px-5 py-4 font-semibold text-sm shadow-sm">
                          ⚠️ {{ currentStudentReport ? currentStudentReport.full_name : 'Оқушы' }} бұл сұраққа жауап бермеді
                        </div>
                      </template>
                    </div>

                    <!-- Correct answer (only shown if student's answer was incorrect or quiz not completed) -->
                    <div v-if="!currentStudentReport?.completed || !currentStudentReport.questionResults[idx]" class="space-y-2">
                      <div class="text-[11px] font-bold text-gray-400 uppercase tracking-wider">Дұрыс жауап:</div>

                      <!-- Plugin visual correct answer -->
                      <div v-if="isQuestionPluginType(q) && buildCorrectReviewPayloadForIdx(q, idx)" class="rounded-xl border border-green-200 p-2 overflow-hidden bg-white bg-green-50/10 shadow-sm">
                        <SessionQuestionPreview :question="buildCorrectReviewPayloadForIdx(q, idx)!" />
                      </div>

                      <!-- Textual fallback -->
                      <div 
                        v-else
                        class="border border-green-200 rounded-xl bg-white px-5 py-4 font-semibold text-lg shadow-sm text-green-700 bg-green-50/20"
                      >
                        {{ currentStudentReport?.questionDetails[idx]?.correctAnswer || getCorrectText(q, null) }}
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
        <div v-else-if="selectedQuizVisibility === 'SCORE_ONLY'" class="bg-blue-50 border border-blue-200 rounded-xl p-6 text-blue-800 text-sm flex items-center gap-4 mt-6 shadow-sm">
          <svg class="w-6 h-6 text-blue-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 class="font-bold text-base text-blue-900">Тек жалпы ұпай көрсетіледі</h4>
            <p class="text-sm mt-0.5 text-blue-700">Мұғалім сұрақтар бойынша толық талдауды және дұрыс жауаптарды көрсетуді шектеген.</p>
          </div>
        </div>
      </div>
    </template>

    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useQuizStore } from '@/stores/quiz'
import { useTeacherStore } from '@/stores/teacher'
import { useAnalyticsStore } from '@/stores/analytics'
import { useCatalogStore } from '@/stores/catalog'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import type { QuizResponse } from '@/api/quiz'
import SessionQuestionPreview from './SessionQuestionPreview.vue'

import { getQuizEffectiveVisibility } from '@/utils/quizVisibility'

interface QuizQuestion {
  id?: string | number
  seed?: number | string | null
  question?: {
    prompt?: string
    type?: string
    data?: Record<string, unknown> | null
    correct_answer?: Record<string, unknown> | null
    level?: number | string
  }
}


const quizStore = useQuizStore()
const teacherStore = useTeacherStore()
const analyticsStore = useAnalyticsStore()
const catalogStore = useCatalogStore()
const authStore = useAuthStore()

const isTeacher = computed(() => authStore.isTeacher)

const { quizzes: allQuizzes, loading, error } = storeToRefs(quizStore)
const { students: teacherStudents } = storeToRefs(teacherStore)

// Filter available quizzes based on student visibility
const availableQuizzes = computed(() => {
  if (isTeacher.value) return allQuizzes.value
  return allQuizzes.value.filter(q => {
    const vis = getQuizEffectiveVisibility(q, authStore.user?.id)
    return vis !== 'HIDDEN'
  })
})

const selectedQuizId = ref('')
const selectedStudentFilter = ref(authStore.isTeacher ? 'all' : (authStore.user?.id || ''))
const scoreType = ref<'questions' | 'percent'>('questions')
const activeSubTab = ref<'overview' | 'responses'>('overview')
const sortBy = ref<'score' | 'name'>('score')
const route = useRoute()

watch(
  () => authStore.user,
  (user) => {
    if (user && !isTeacher.value) {
      selectedStudentFilter.value = user.id
    }
  },
  { immediate: true }
)

const selectedQuiz = computed<QuizResponse | null>(() => {
  if (!selectedQuizId.value) return null
  const quiz = availableQuizzes.value.find(q => q.id === selectedQuizId.value) || allQuizzes.value.find(q => q.id === selectedQuizId.value) || null
  if (quiz && quiz.questions) {
    return {
      ...quiz,
      questions: [...quiz.questions].sort((a, b) => (a.position || 0) - (b.position || 0))
    }
  }
  return quiz
})

const selectedQuizVisibility = computed(() => {
  if (!selectedQuiz.value) return 'ALWAYS'
  if (isTeacher.value) return 'ALWAYS'
  return getQuizEffectiveVisibility(selectedQuiz.value, authStore.user?.id)
})

const loadedSkills = ref<Map<number, { code: string; title: string }>>(new Map())

const uniqueSkillIds = computed(() => {
  if (!selectedQuiz.value) return []
  const ids = new Set<number>()
  selectedQuiz.value.questions.forEach(q => {
    if (q.question?.skill_id) {
      ids.add(q.question.skill_id)
    }
  })
  return Array.from(ids)
})

watch(
  uniqueSkillIds,
  async (ids) => {
    if (!ids || ids.length === 0) return
    // Load each unique skill details sequentially or in parallel
    await Promise.all(
      ids.map(async (id) => {
        if (!loadedSkills.value.has(id)) {
          try {
            const skill = await catalogStore.getSkill(id)
            if (skill) {
              loadedSkills.value.set(id, {
                code: skill.code || '',
                title: skill.title || ''
              })
            }
          } catch (err) {
            console.warn(`Failed to load skill details for #${id}:`, err)
          }
        }
      })
    )
  },
  { immediate: true }
)

onMounted(async () => {
  const promises: Promise<unknown>[] = [
    quizStore.fetchQuizzes(),
    analyticsStore.getSkills(true)
  ]
  if (isTeacher.value) {
    promises.push(teacherStore.fetchStudents())
  }
  await Promise.all(promises)
})

watch(
  [() => route.query.quizId, allQuizzes],
  ([newQuizId, quizzes]) => {
    if (quizzes && quizzes.length > 0) {
      if (newQuizId && typeof newQuizId === 'string') {
        const found = quizzes.find(q => q.id === newQuizId)
        if (found) {
          selectedQuizId.value = found.id
          return
        }
      }
      
      // Default to the latest quiz based on creation date
      const sorted = [...quizzes].sort((a, b) => {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      })
      selectedQuizId.value = sorted[0].id
    }
  },
  { immediate: true }
)



const getCompletionStats = (quiz: QuizResponse) => {
  const assignments = quiz.assignments || []
  const total = assignments.length
  const completed = assignments.filter(a => a.completed_at !== null).length
  return { completed, total }
}

const getAverageScoreDisplay = (quiz: QuizResponse) => {
  const assignments = quiz.assignments || []
  const completedAssignments = assignments.filter(a => a.completed_at !== null)
  if (completedAssignments.length === 0) {
    return scoreType.value === 'questions' ? `0 / ${quiz.questions.length}` : '0%'
  }
  const totalScore = completedAssignments.reduce((acc, a) => acc + (a.score || 0), 0)
  const avgPct = Math.round(totalScore / completedAssignments.length)
  
  if (scoreType.value === 'questions') {
    const avgCorrect = (avgPct / 100) * quiz.questions.length
    return `${Math.round(avgCorrect * 10) / 10} / ${quiz.questions.length}`
  } else {
    return `${avgPct}%`
  }
}

const formatAnswer = (answer: unknown): string => {
  if (!answer) return '—'
  if (typeof answer === 'object' && answer !== null) {
    const obj = answer as Record<string, unknown>
    if ('userAnswer' in obj) return String(obj.userAnswer ?? '—')
    if ('user_answer' in obj) return String(obj.user_answer ?? '—')
    if ('choice' in obj) return String(obj.choice ?? '—')
    if ('value' in obj) return String(obj.value ?? '—')
    if ('text' in obj) return String(obj.text ?? '—')
    if ('correctAnswer' in obj) return String(obj.correctAnswer ?? '—')
    if ('correct_answer' in obj) return String(obj.correct_answer ?? '—')
    return (obj.value || obj.label || obj.text || JSON.stringify(answer)) as string
  }
  return String(answer)
}

const getCorrectText = (
  q: QuizQuestion,
  savedCorrectAnswer: unknown
): string => {
  if (savedCorrectAnswer) {
    return formatAnswer(savedCorrectAnswer)
  }
  const question = q.question
  if (!question) return '—'
  const correct = question.correct_answer
  if (!correct) return '—'
  if (question.type === 'MCQ') {
    const choices = (question.data?.choices || question.data?.options || []) as Array<Record<string, unknown> | string | number>
    const correctChoiceId = String(correct.choice ?? '')
    const found = choices.find((c) => {
      if (c && typeof c === 'object') {
        return String(c.id ?? '') === correctChoiceId
      }
      return String(c) === correctChoiceId
    })
    if (found) {
      return typeof found === 'object' ? String(found.label || found.text || found.value || '') : String(found)
    }
    return correctChoiceId || '—'
  }
  if (question.type === 'NUMERIC') {
    return String(correct.value ?? '—')
  }
  if (question.type === 'TEXT') {
    return String(correct.text ?? '—')
  }
  return formatAnswer(correct)
}

const reportStudents = computed(() => {
  if (!selectedQuiz.value) return []
  const quiz = selectedQuiz.value
  let assignments = quiz.assignments || []

  if (!isTeacher.value) {
    assignments = assignments.filter(a => String(a.student_id) === String(authStore.user?.id))
  }

  return assignments.map(assignment => {
    let fullName = `Оқушы (${assignment.student_id?.slice(0, 8) || 'Белгісіз'})`
    if (!isTeacher.value && String(assignment.student_id) === String(authStore.user?.id)) {
      fullName = authStore.user?.full_name || 'Мен'
    } else {
      const student = teacherStudents.value.find(s => s.id === assignment.student_id)
      if (student) fullName = student.full_name
    }

    const isCompleted = assignment.completed_at !== null
    const score = assignment.score || 0

    let timeSpent = '—'
    if (isCompleted && assignment.time_spent_seconds !== null && assignment.time_spent_seconds !== undefined) {
      const mins = Math.floor(assignment.time_spent_seconds / 60)
      const secs = assignment.time_spent_seconds % 60
      timeSpent = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
    }

    const totalQuestions = quiz.questions.length || 5
    let correctAnswers = 0
    let questionResults: boolean[] = []
    let questionDetails: Array<{ correct: boolean; submitted: string; correctAnswer: string; rawSubmitted: unknown; rawCorrectAnswer: unknown }> = []

    if (isCompleted) {
      const sortedQs = [...quiz.questions].sort((a, b) => a.position - b.position)
      const resultsMap = (assignment.question_results as Record<string, unknown>) || {}
      
      for (const q of sortedQs) {
        const qId = q.id
        const res = resultsMap[String(qId)]
        
        let correct = false
        let submitted = '—'
        let correctAnswer = '—'
        let rawSubmitted: unknown = null
        let rawCorrectAnswer: unknown = null

        if (res !== undefined) {
          if (res === true || res === false) {
            correct = res
          } else if (typeof res === 'object' && res !== null) {
            const resObj = res as Record<string, unknown>
            correct = resObj.correct === true
            submitted = formatAnswer(resObj.submitted_answer)
            correctAnswer = getCorrectText(q, resObj.correct_answer)
            rawSubmitted = resObj.submitted_answer
            rawCorrectAnswer = resObj.correct_answer
          }
        }

        if (submitted === '—') {
          submitted = correct ? 'Correct Answer' : 'Incorrect Answer'
        }
        if (correctAnswer === '—') {
          correctAnswer = getCorrectText(q, null)
        }

        if (correct) correctAnswers++
        questionResults.push(correct)
        questionDetails.push({ correct, submitted, correctAnswer, rawSubmitted, rawCorrectAnswer })
      }
    } else {
      questionResults = Array(totalQuestions).fill(false)
      const sortedQs = [...quiz.questions].sort((a, b) => (a.position || 0) - (b.position || 0))
      questionDetails = sortedQs.map(q => ({
        correct: false,
        submitted: '—',
        correctAnswer: getCorrectText(q, null),
        rawSubmitted: null,
        rawCorrectAnswer: q.question?.correct_answer || null
      }))
    }

    return { 
      id: assignment.student_id || assignment.id, 
      full_name: fullName, 
      started: assignment.started_at !== null && assignment.started_at !== undefined,
      completed: isCompleted, 
      score, 
      correctAnswers, 
      timeSpent, 
      questionResults,
      questionDetails
    }
  })
})

const filteredReportStudents = computed(() => {
  let list = [...reportStudents.value]
  if (selectedStudentFilter.value !== 'all') {
    list = list.filter(s => s.id === selectedStudentFilter.value)
  }
  if (sortBy.value === 'score') {
    list.sort((a, b) => b.score - a.score)
  } else {
    list.sort((a, b) => a.full_name.localeCompare(b.full_name))
  }
  return list
})

const inProgressCount = computed(() => {
  return reportStudents.value.filter(s => s.started && !s.completed).length
})

const notStartedCount = computed(() => {
  return reportStudents.value.filter(s => !s.started && !s.completed).length
})

const questionBuckets = computed(() => {
  if (!selectedQuiz.value) return []
  const quiz = selectedQuiz.value
  const N = quiz.questions.length
  
  if (N < 5) {
    const buckets = []
    buckets.push({ label: `0 - 1`, color: '#ff9800', count: 0 })
    for (let i = 2; i <= N; i++) {
      let color = '#cddc39'
      if (i === N) color = '#00b0ff'
      else if (i === N - 1) color = '#26a69a'
      else if (i === 2) color = '#d4e157'
      
      buckets.push({
        label: `${i}`,
        color,
        count: 0
      })
    }
    
    const completedStudents = reportStudents.value.filter(s => s.completed)
    for (const s of completedStudents) {
      const correct = s.correctAnswers
      const idx = correct <= 1 ? 0 : correct - 1
      if (buckets[idx]) {
        buckets[idx].count++
      }
    }
    return buckets
  } else {
    const buckets = [
      { label: `0 - ${N - 5}`, color: '#ff9800', count: 0 },
      { label: `${N - 4}`, color: '#cddc39', count: 0 },
      { label: `${N - 3}`, color: '#d4e157', count: 0 },
      { label: `${N - 2}`, color: '#26a69a', count: 0 },
      { label: `${N - 1} - ${N}`, color: '#00b0ff', count: 0 }
    ]
    
    const completedStudents = reportStudents.value.filter(s => s.completed)
    for (const s of completedStudents) {
      const correct = s.correctAnswers
      let idx = 0
      if (correct <= N - 5) idx = 0
      else if (correct === N - 4) idx = 1
      else if (correct === N - 3) idx = 2
      else if (correct === N - 2) idx = 3
      else idx = 4
      
      if (buckets[idx]) {
        buckets[idx].count++
      }
    }
    return buckets
  }
})

const percentBuckets = computed(() => {
  const buckets = [
    { label: '0 - 59%', color: '#ff9800', count: 0 },
    { label: '60 - 69%', color: '#cddc39', count: 0 },
    { label: '70 - 79%', color: '#d4e157', count: 0 },
    { label: '80 - 89%', color: '#26a69a', count: 0 },
    { label: '90 - 100%', color: '#00b0ff', count: 0 }
  ]
  const completedStudents = reportStudents.value.filter(s => s.completed)
  for (const s of completedStudents) {
    const score = s.score
    if (score <= 59) buckets[0].count++
    else if (score <= 69) buckets[1].count++
    else if (score <= 79) buckets[2].count++
    else if (score <= 89) buckets[3].count++
    else buckets[4].count++
  }
  return buckets
})

const activeBuckets = computed(() => {
  return scoreType.value === 'questions' ? questionBuckets.value : percentBuckets.value
})

const maxBucketCount = computed(() => {
  const counts = activeBuckets.value.map(b => b.count)
  return Math.max(...counts, 1)
})

const getStudentBucketIndex = (correct: number, N: number) => {
  if (N < 5) {
    if (correct <= 1) return 0
    return correct - 1
  } else {
    if (correct <= N - 5) return 0
    if (correct === N - 4) return 1
    if (correct === N - 3) return 2
    if (correct === N - 2) return 3
    return 4
  }
}

const getStudentPercentBucketIndex = (score: number) => {
  if (score <= 59) return 0
  if (score <= 69) return 1
  if (score <= 79) return 2
  if (score <= 89) return 3
  return 4
}

// Топтастырылған оқушылар тізімі
const bucketStudents = computed(() => {
  if (!selectedQuiz.value) return []
  const quiz = selectedQuiz.value
  const N = quiz.questions.length
  
  const buckets = activeBuckets.value.map(b => ({
    ...b,
    students: [] as typeof reportStudents.value
  }))
  
  const completedStudents = filteredReportStudents.value.filter(s => s.completed)
  for (const s of completedStudents) {
    const idx = scoreType.value === 'questions' 
      ? getStudentBucketIndex(s.correctAnswers, N)
      : getStudentPercentBucketIndex(s.score)
    if (buckets[idx]) {
      buckets[idx].students.push(s)
    }
  }
  return buckets.filter(b => b.students.length > 0)
})

const inProgressStudents = computed(() => {
  return filteredReportStudents.value.filter(s => s.started && !s.completed)
})

const notStartedStudents = computed(() => {
  return filteredReportStudents.value.filter(s => !s.started && !s.completed)
})

// Сұрақтардың аналитикалық статистикасы
const getQuestionStats = (qIndex: number) => {
  const completedStudents = reportStudents.value.filter(s => s.completed)
  if (completedStudents.length === 0) {
    return { correctPercent: 0, correctCount: 0, totalCount: 0 }
  }
  const correctCount = completedStudents.filter(s => s.questionDetails[qIndex]?.correct === true).length
  const totalCount = completedStudents.length
  const correctPercent = Math.round((correctCount / totalCount) * 100)
  return { correctPercent, correctCount, totalCount }
}

// Дағдыны іздеу функциясы
const getQuestionSkillInfo = (skillId?: number) => {
  if (!skillId) {
    return { code: '', name: 'Жалпы дайындық (General practice)' }
  }
  const loaded = loadedSkills.value.get(skillId)
  if (loaded) {
    return { code: loaded.code, name: loaded.title }
  }
  const skill = analyticsStore.skills.find(s => Number(s.skill_id) === Number(skillId))
  if (skill) {
    return {
      code: String(skill.skill_code || ''),
      name: String(skill.skill_name || skill.title || '')
    }
  }
  return {
    code: '',
    name: `Дағды #${skillId}`
  }
}

const selectedQuestionIndex = ref(0)
const showAllStudents = ref(false)

const selectedQuestionPreview = computed(() => {
  const quiz = selectedQuiz.value
  if (!quiz) return null
  const q = quiz.questions[selectedQuestionIndex.value]
  if (!q) return null
  return {
    prompt: q.question?.prompt || '',
    type: q.question?.type || '',
    data: (q.question?.data as Record<string, unknown> | null) || null,
    userAnswer: null,
    isCorrect: false,
    correctAnswer: getCorrectText(q, null),
    seed: q.seed || null
  }
})

const isSelectedQuestionPlugin = computed(() => {
  const quiz = selectedQuiz.value
  if (!quiz) return false
  const q = quiz.questions[selectedQuestionIndex.value]
  if (!q) return false
  const qType = String(q.question?.type || '').toUpperCase()
  return qType === 'PLUGIN' || qType === 'INTERACTIVE'
})

const buildResponsePreview = (rawAnswer: unknown, isCorrect: boolean) => {
  const quiz = selectedQuiz.value
  if (!quiz) return null
  const q = quiz.questions[selectedQuestionIndex.value]
  if (!q) return null
  return {
    prompt: q.question?.prompt || '',
    type: q.question?.type || '',
    data: (q.question?.data as Record<string, unknown> | null) || null,
    userAnswer: rawAnswer,
    isCorrect,
    correctAnswer: q.question?.correct_answer || null,
    seed: q.seed || null
  }
}

const currentStudentReport = computed(() => {
  return reportStudents.value.find(s => s.id === selectedStudentFilter.value) || null
})



const buildQuestionReview = (q: QuizQuestion) => {
  return {
    prompt: q.question?.prompt || '',
    type: q.question?.type || '',
    data: (q.question?.data as Record<string, unknown> | null) || null,
    userAnswer: null,
    isCorrect: false,
    correctAnswer: getCorrectText(q, null),
    seed: q.seed || null
  }
}

const isQuestionPluginType = (q: QuizQuestion): boolean => {
  const qType = String(q.question?.type || '').toUpperCase()
  return qType === 'PLUGIN' || qType === 'INTERACTIVE'
}

const buildStudentResponseReview = (q: QuizQuestion, rawAnswer: unknown, isCorrect: boolean) => {
  return {
    prompt: q.question?.prompt || '',
    type: q.question?.type || '',
    data: (q.question?.data as Record<string, unknown> | null) || null,
    userAnswer: rawAnswer,
    isCorrect,
    correctAnswer: q.question?.correct_answer || null,
    seed: q.seed || null
  }
}

const buildCorrectReviewPayloadForIdx = (q: QuizQuestion, qIndex: number) => {
  const detail = currentStudentReport.value?.questionDetails[qIndex]
  const rawCorrectAnswer = detail?.rawCorrectAnswer || q.question?.correct_answer || null
  const rawSubmitted = detail?.rawSubmitted as Record<string, unknown> | null
  const studentQData = rawSubmitted ? (rawSubmitted.questionData || rawSubmitted.visualData) : null
  const studentAnsData = rawSubmitted ? rawSubmitted.answerData : null

  const mockCorrectPayload = {
    isCorrect: true,
    userAnswer: rawCorrectAnswer,
    studentAnswer: rawCorrectAnswer,
    correctAnswer: rawCorrectAnswer,
    questionData: studentQData || q.question?.data || null,
    answerData: studentAnsData
  }

  return {
    prompt: q.question?.prompt || '',
    type: q.question?.type || '',
    data: (q.question?.data as Record<string, unknown> | null) || null,
    userAnswer: mockCorrectPayload,
    isCorrect: true,
    correctAnswer: rawCorrectAnswer,
    seed: q.seed || null
  }
}

const getGroupedResponsesForQuestion = (qIndex: number) => {
  const quiz = selectedQuiz.value
  if (!quiz) return []
  const question = quiz.questions[qIndex]
  if (!question) return []
  
  const completedStudents = reportStudents.value.filter(s => s.completed)
  const groupsMap = new Map<string, { answer: string, isCorrect: boolean, rawAnswer: unknown, students: typeof reportStudents.value }>()
  
  for (const student of completedStudents) {
    const detail = student.questionDetails[qIndex]
    if (!detail) continue
    const ans = formatAnswer(detail.submitted)
    const correct = detail.correct
    
    if (!groupsMap.has(ans)) {
      groupsMap.set(ans, {
        answer: ans,
        isCorrect: correct,
        rawAnswer: detail.rawSubmitted,
        students: []
      })
    }
    groupsMap.get(ans)!.students.push(student)
  }
  
  // If no student answered correctly, add a standalone correct answer group so the teacher can see the right answer
  const anyCorrect = Array.from(groupsMap.values()).some(g => g.isCorrect)
  if (!anyCorrect) {
    const studentDetail = completedStudents.find(s => s.questionDetails[qIndex]?.rawSubmitted)
    const studentRaw = studentDetail ? (studentDetail.questionDetails[qIndex]?.rawSubmitted as Record<string, unknown>) : null
    const studentQData = studentRaw ? (studentRaw.questionData || studentRaw.visualData) : null
    const studentAnsData = studentRaw ? studentRaw.answerData : null

    const rawCorrectAnswer = question.question?.correct_answer || completedStudents[0]?.questionDetails[qIndex]?.rawCorrectAnswer || null
    const correctAnswer = formatAnswer(rawCorrectAnswer || completedStudents[0]?.questionDetails[qIndex]?.correctAnswer || getCorrectText(question, null))

    // Construct a full wrapper payload for the correct answer to be passed to SessionQuestionPreview
    const mockCorrectPayload = {
      isCorrect: true,
      userAnswer: rawCorrectAnswer,
      studentAnswer: rawCorrectAnswer,
      correctAnswer: rawCorrectAnswer,
      questionData: studentQData || question.question?.data || null,
      answerData: studentAnsData
    }

    groupsMap.set('__correct__', {
      answer: correctAnswer,
      isCorrect: true,
      rawAnswer: mockCorrectPayload,
      students: []
    })
  }
  
  const groups = Array.from(groupsMap.values())
  groups.sort((a, b) => {
    if (a.isCorrect && !b.isCorrect) return -1
    if (!a.isCorrect && b.isCorrect) return 1
    return b.students.length - a.students.length
  })
  
  return groups
}

const goToResponses = (index: number) => {
  selectedQuestionIndex.value = index
  activeSubTab.value = 'responses'
}
</script>

<style scoped>
.quizzes-report-container {
  font-family: 'Outfit', 'Inter', sans-serif;
}
table th, table td {
  border-bottom: 1px solid #f3f4f6;
  padding: 12px 16px;
}
</style>
