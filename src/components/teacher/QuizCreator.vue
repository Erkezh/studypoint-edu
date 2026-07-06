<template>
  <div class="quiz-creator">
    <div class="creator-header bg-white shadow-sm border-b border-gray-100 px-6 py-4 flex items-center justify-between">
      <button @click="$emit('cancel')" class="back-link flex items-center text-gray-500 hover:text-gray-700 transition-colors font-medium">
        <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
        Артқа
      </button>
      <div class="step-indicator text-sm font-bold text-gray-400 tracking-wider uppercase">
        {{ currentStep === 1 ? 'ҚАДАМ 1 / 2: Сұрақтарды қосу' : 'ҚАДАМ 2 / 2: Параметрлер мен Жинақтау' }}
      </div>
    </div>

    <!-- STEP 1: ADD QUESTIONS -->
    <div v-if="currentStep === 1" class="step-container p-6 bg-slate-50 min-h-screen">
      <!-- Quiz Name Banner -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 mb-6 flex flex-col md:flex-row gap-4 items-center justify-between">
        <div class="flex-1 w-full">
          <input 
            v-model="quizName" 
            type="text" 
            placeholder="Квиз атауын енгізіңіз..." 
            class="quiz-name-input w-full px-4 py-3 border border-slate-200 rounded-xl text-lg font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all"
          />
        </div>
        <button 
          @click="nextStep" 
          :disabled="!quizName.trim() || selectedQuestions.length === 0" 
          class="next-btn px-6 py-3.5 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-200 text-white disabled:text-slate-400 rounded-xl font-semibold transition-all shadow-sm shadow-emerald-500/10 cursor-pointer disabled:cursor-not-allowed w-full md:w-auto text-center shrink-0"
        >
          Қарау және жариялау
        </button>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-[80px_1fr_400px] gap-6 items-start">
        
        <!-- Left Question Navigator (Sidebar Index) -->
        <div class="hidden xl:flex flex-col gap-2 sticky top-6 bg-white p-3 rounded-2xl border border-slate-100 shadow-sm items-center">
          <button 
            v-for="(q, idx) in selectedQuestions" 
            :key="q.id"
            @click="scrollToQuestion(idx)"
            class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm border transition-all"
            :class="[
              activeQuestionIndex === idx 
                ? 'bg-emerald-500 border-emerald-500 text-white shadow-sm' 
                : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
            ]"
            :title="`Сұрақ ${idx + 1}`"
          >
            {{ idx + 1 }}
          </button>
          <button 
            @click="addNewQuestionSlot"
            class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg bg-emerald-50 border border-dashed border-emerald-300 text-emerald-600 hover:bg-emerald-100 transition-all"
            title="Жаңа сұрақ ұяшығын қосу"
          >
            +
          </button>
        </div>

        <!-- Main Panel: Cards list of added questions -->
        <div class="flex flex-col gap-6">
          <!-- Selection & Preview Panel (Dynamic Generator Selection) -->
          <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
            <div class="border-b border-slate-100 bg-slate-50/50 px-6 py-4">
              <h3 class="font-bold text-slate-800 text-base">Сұрақтар генераторы</h3>
            </div>
            
            <div class="p-6 grid grid-cols-1 md:grid-cols-4 gap-4">
              <!-- Grade selection -->
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-500">Сынып</label>
                <select v-model="selectedGrade" @change="onGradeChange" class="px-3 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:border-emerald-500 transition-colors">
                  <option :value="null" disabled>Сынып таңдаңыз</option>
                  <option v-for="g in grades" :key="g.id" :value="g.number">{{ g.number }} сынып</option>
                </select>
              </div>

              <!-- Theme selection -->
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-500">Тақырып (Тема)</label>
                <select v-model="selectedTheme" @change="onThemeChange" :disabled="!selectedGrade" class="px-3 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:border-emerald-500 transition-colors disabled:bg-slate-50 disabled:text-slate-400">
                  <option :value="null">Барлығы</option>
                  <option v-for="t in parentThemes" :key="t.id" :value="t">{{ t.title }}</option>
                </select>
              </div>

              <!-- Subtheme selection -->
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-500">Кіші тақырып (Подтема)</label>
                <select v-model="selectedSubtheme" @change="onSubthemeChange" :disabled="!selectedTheme" class="px-3 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:border-emerald-500 transition-colors disabled:bg-slate-50 disabled:text-slate-400">
                  <option :value="null">Барлығы</option>
                  <option v-for="t in childSubthemes" :key="t.id" :value="t">{{ t.title }}</option>
                </select>
              </div>

              <!-- Skill selection -->
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-500">Дағды (Скилл)</label>
                <select v-model="selectedSkill" @change="onSkillChange" :disabled="skillsList.length === 0" class="px-3 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:border-emerald-500 transition-colors disabled:bg-slate-50 disabled:text-slate-400">
                  <option :value="null" disabled>Дағды таңдаңыз</option>
                  <option v-for="s in skillsList" :key="s.id" :value="s">{{ s.code }} - {{ s.title }}</option>
                </select>
              </div>
            </div>

            <!-- Preview Card (renders dynamically when skill is loaded) -->
            <div v-if="selectedSkill" class="px-6 pb-6 border-t border-slate-100 pt-6">
              <div class="bg-slate-50 rounded-xl p-6 border border-slate-200">
                <div class="flex items-center justify-between mb-4">
                  <span class="text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full uppercase tracking-wider">Алдын ала қарау</span>
                  
                  <div class="flex items-center gap-3">
                    <!-- Difficulty selector in Preview -->
                    <div class="flex items-center gap-1.5">
                      <span class="text-xs text-slate-500 font-medium">Деңгей:</span>
                      <select v-model="previewDifficulty" @change="onPreviewDifficultyChange" class="px-2 py-1 text-xs border border-slate-200 rounded bg-white">
                        <option :value="1">Деңгей 1</option>
                        <option :value="2">Деңгей 2</option>
                        <option :value="3">Деңгей 3</option>
                        <option :value="4">Деңгей 4</option>
                      </select>
                    </div>

                    <button @click="regeneratePreview" class="text-xs text-emerald-600 hover:text-emerald-700 font-semibold flex items-center gap-1">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H17m-.002 4l-.007-.04M16.5 12h.01" /></svg>
                      Басқа сұрақ ↻
                    </button>
                  </div>
                </div>

                <div v-if="loadingQuestions" class="py-8 text-center text-slate-400 text-sm">
                  Жүктелуде...
                </div>
                
                <div v-else-if="!previewQuestion" class="py-8 text-center text-slate-400 text-sm">
                  Бұл деңгей үшін сұрақ табылмады. Басқа деңгей таңдаңыз.
                </div>

                <div v-else class="space-y-4">
                  <!-- Prompt -->
                  <div class="text-sm font-semibold text-slate-800" v-html="previewQuestion.prompt"></div>

                  <!-- MCQ Choices -->
                  <div v-if="previewQuestion.type === 'MCQ'" class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div 
                      v-for="(option, index) in (previewQuestion.data?.choices || previewQuestion.data?.options || [])" 
                      :key="index"
                      class="p-3 border rounded-lg text-xs transition-all flex items-center justify-between"
                      :class="[
                        showPreviewAnswer && isOptionCorrect(previewQuestion, option, index)
                          ? 'border-emerald-500 bg-emerald-50 text-emerald-800 font-semibold'
                          : 'border-slate-200 bg-white text-slate-700'
                      ]"
                    >
                      <span v-html="formatMCQOption(option)"></span>
                      <svg v-if="showPreviewAnswer && isOptionCorrect(previewQuestion, option, index)" class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                    </div>
                  </div>

                  <!-- NUMERIC/TEXT Answers -->
                  <div v-else class="p-3 border border-slate-200 bg-white rounded-lg inline-flex items-center gap-2 text-xs">
                    <span class="text-slate-400 font-medium">Жауап өрісі</span>
                    <span v-if="showPreviewAnswer" class="text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      Дұрыс мән: {{ previewQuestion.correct_answer?.value || previewQuestion.correct_answer?.choice || 'Көрсетілмеген' }}
                    </span>
                  </div>

                  <!-- Preview control bottom -->
                  <div class="flex items-center justify-between border-t border-slate-200/60 pt-4 mt-4">
                    <div class="text-xs text-slate-500">
                      Бұл санаттағы жалпы сұрақтар саны: <span class="font-bold text-slate-700">{{ filteredPoolQuestions.length }}</span>
                    </div>

                    <div class="flex items-center gap-4">
                      <!-- Correct answer toggle -->
                      <button @click="showPreviewAnswer = !showPreviewAnswer" class="text-xs text-slate-600 hover:text-slate-800 font-semibold flex items-center gap-1 border border-slate-300 rounded px-2.5 py-1.5 bg-white transition-colors">
                        {{ showPreviewAnswer ? 'Жауапты жасыру' : 'Дұрыс жауабын көрсету' }}
                      </button>

                      <div class="flex items-center gap-2 border border-slate-200 rounded-lg p-1 bg-white">
                        <button @click="previewCount = Math.max(1, previewCount - 1)" class="w-7 h-7 bg-slate-50 hover:bg-slate-100 rounded text-slate-600 font-bold">-</button>
                        <span class="w-6 text-center text-sm font-bold text-slate-700">{{ previewCount }}</span>
                        <button @click="previewCount = Math.min(filteredPoolQuestions.length || 1, previewCount + 1)" class="w-7 h-7 bg-slate-50 hover:bg-slate-100 rounded text-slate-600 font-bold">+</button>
                      </div>

                      <button 
                        @click="addGeneratedQuestions" 
                        :disabled="!previewQuestion" 
                        class="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-200 text-white disabled:text-slate-400 rounded-lg text-xs font-bold transition-colors cursor-pointer"
                      >
                        Сұрақтарды қосу
                      </button>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>

          <!-- Empty placeholder list -->
          <div v-if="selectedQuestions.length === 0" class="bg-white rounded-2xl border border-dashed border-slate-200 p-12 text-center text-slate-400 shadow-sm">
            <svg class="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
            <p class="font-semibold text-slate-700 mb-1">Сұрақтар әлі таңдалмаған</p>
            <p class="text-xs">Жоғарыдағы сұрақтар генераторынан дағдыны таңдап, квизге сұрақтарды қосыңыз.</p>
          </div>

          <!-- List of Question Cards -->
          <div v-else class="flex flex-col gap-6">
            <div 
              v-for="(q, idx) in selectedQuestions" 
              :key="q.id" 
              :id="`question-card-${idx}`"
              class="question-card bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden transition-all duration-200"
              :class="{ 'ring-2 ring-emerald-500/20 border-emerald-500': activeQuestionIndex === idx }"
              @click="activeQuestionIndex = idx"
            >
              <div class="border-b border-slate-100 bg-slate-50/50 px-6 py-3.5 flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <span class="font-bold text-emerald-600 text-sm">СҰРАҚ {{ idx + 1 }}</span>
                  <span class="text-xs text-slate-400 font-medium">Дағды: {{ q.skill_title }}</span>
                </div>
                
                <div class="flex items-center gap-3">
                  <!-- Skill / Difficulty info badge -->
                  <span class="text-xs font-semibold bg-blue-50 text-blue-700 px-2 py-0.5 rounded-md">Деңгей {{ q.level }}</span>

                  <button @click.stop="removeQuestionCard(idx)" class="text-slate-400 hover:text-rose-600 transition-colors" title="Сұрақты өшіру">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                </div>
              </div>

              <!-- Question Content & Custom Options -->
              <div class="p-6 space-y-4">
                <div class="flex flex-col md:flex-row gap-4 items-center justify-between border-b border-slate-100 pb-4 mb-4">
                  <!-- Change skill in Card -->
                  <div class="flex items-center gap-2 text-xs w-full md:w-auto">
                    <span class="text-slate-500">Дағдыны ауыстыру:</span>
                    <select :value="q.skill_id" @change="changeCardSkill(idx, Number(($event.target as HTMLSelectElement).value))" class="px-2.5 py-1 border border-slate-200 rounded bg-white font-medium flex-1 md:flex-none">
                      <option v-for="s in skillsList" :key="s.id" :value="s.id">{{ s.title }}</option>
                    </select>
                  </div>

                  <div class="flex items-center gap-3 w-full md:w-auto justify-end">
                    <!-- Change level in Card -->
                    <div class="flex items-center gap-1.5 text-xs">
                      <span class="text-slate-500">Деңгейі:</span>
                      <select :value="q.level" @change="changeCardLevel(idx, Number(($event.target as HTMLSelectElement).value))" class="px-2 py-0.5 border border-slate-200 rounded bg-white">
                        <option :value="1">Деңгей 1</option>
                        <option :value="2">Деңгей 2</option>
                        <option :value="3">Деңгей 3</option>
                        <option :value="4">Деңгей 4</option>
                      </select>
                    </div>

                    <!-- Regenerate specific question -->
                    <button @click.stop="regenerateQuestionCard(idx)" class="text-xs text-emerald-600 hover:text-emerald-700 font-semibold flex items-center gap-1">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H17m-.002 4l-.007-.04M16.5 12h.01" /></svg>
                      Жаңа сұрақ генерациялау ↻
                    </button>
                  </div>
                </div>

                <!-- Prompt -->
                <div class="text-sm font-semibold text-slate-800" v-html="q.prompt"></div>

                <!-- MCQ Choices -->
                <div v-if="q.type === 'MCQ'" class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div 
                    v-for="(option, optIdx) in (q.data?.choices || q.data?.options || [])" 
                    :key="optIdx"
                    class="p-3 border rounded-lg text-xs flex items-center justify-between transition-colors"
                    :class="[
                      q.showAnswer && isOptionCorrect(q, option, optIdx)
                        ? 'border-emerald-500 bg-emerald-50 text-emerald-800 font-semibold'
                        : 'border-slate-200 bg-white text-slate-700'
                    ]"
                  >
                    <span v-html="formatMCQOption(option)"></span>
                    <svg v-if="q.showAnswer && isOptionCorrect(q, option, optIdx)" class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                  </div>
                </div>

                <!-- NUMERIC/TEXT Answers -->
                <div v-else class="p-3 border border-slate-200 bg-white rounded-lg inline-flex items-center gap-2 text-xs">
                  <span class="text-slate-400 font-medium">Жауап өрісі</span>
                  <span v-if="q.showAnswer" class="text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    Дұрыс мән: {{ q.correct_answer?.value || q.correct_answer?.choice || 'Көрсетілмеген' }}
                  </span>
                </div>

                <!-- Card action bottom -->
                <div class="flex justify-end pt-3 border-t border-slate-100">
                  <button @click.stop="q.showAnswer = !q.showAnswer" class="text-xs text-slate-600 hover:text-slate-800 font-semibold flex items-center gap-1 border border-slate-300 rounded px-2.5 py-1.5 bg-white transition-colors">
                    {{ q.showAnswer ? 'Жауапты жасыру' : 'Дұрыс жауабын көрсету' }}
                  </button>
                </div>

              </div>
            </div>
          </div>

        </div>

        <!-- Sidebar Right: Info & stats summary -->
        <div class="sticky top-6 bg-white p-6 rounded-2xl border border-slate-100 shadow-sm space-y-6">
          <div>
            <h3 class="font-bold text-slate-800 text-sm mb-1">Квиз жиынтығы</h3>
            <p class="text-xs text-slate-400">Квиз құрамы мен негізгі мәліметтері</p>
          </div>

          <div class="divide-y divide-slate-100 text-xs">
            <div class="py-2.5 flex justify-between">
              <span class="text-slate-500">Квиз атауы:</span>
              <span class="font-semibold text-slate-800 truncate max-w-[200px]">{{ quizName || '—' }}</span>
            </div>
            <div class="py-2.5 flex justify-between">
              <span class="text-slate-500">Сұрақтар саны:</span>
              <span class="font-bold text-emerald-600">{{ selectedQuestions.length }} сұрақ</span>
            </div>
            <div class="py-2.5 flex justify-between">
              <span class="text-slate-500">Сынып:</span>
              <span class="font-semibold text-slate-800">{{ selectedGrade ? `${selectedGrade}-сынып` : 'Таңдалмаған' }}</span>
            </div>
          </div>

          <div class="pt-4">
            <button 
              @click="nextStep" 
              :disabled="!quizName.trim() || selectedQuestions.length === 0"
              class="w-full py-3 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-100 text-white disabled:text-slate-400 font-bold rounded-xl text-sm transition-all shadow-sm shadow-emerald-500/10 cursor-pointer disabled:cursor-not-allowed text-center"
            >
              Қарау және жариялау
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- STEP 2: SETTINGS & PUBLISH -->
    <div v-else class="step-container p-6 bg-slate-50 min-h-screen">
      <div class="max-w-3xl mx-auto space-y-6">
        <!-- Back navigation step 2 -->
        <button @click="currentStep = 1" class="flex items-center text-sm font-semibold text-slate-600 hover:text-slate-800 transition-colors">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          Қадам 1-ге оралу (Сұрақтарды өңдеу)
        </button>

        <!-- Main Configuration Box -->
        <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-8 space-y-6">
          <h3 class="font-bold text-slate-800 text-lg border-b border-slate-100 pb-3">Квизді жариялау параметрлері</h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Quiz Name Field -->
            <div class="form-group flex flex-col gap-2">
              <label class="text-sm font-semibold text-slate-700">Квиз атауы</label>
              <input v-model="quizName" type="text" class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:border-emerald-500" />
            </div>

            <!-- Question Order -->
            <div class="form-group flex flex-col gap-2">
              <label class="text-sm font-semibold text-slate-700">Сұрақтар реті</label>
              <select v-model="settings.question_order" class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:border-emerald-500">
                <option value="FIXED">Барлық оқушылар үшін бірдей</option>
                <option value="RANDOMIZED">Кездейсоқ ретпен (Араластыру)</option>
              </select>
            </div>

            <!-- End Quiz type -->
            <div class="form-group flex flex-col gap-2">
              <label class="text-sm font-semibold text-slate-700">Квизді аяқтау</label>
              <select v-model="settings.end_type" class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:border-emerald-500">
                <option value="MANUAL">Қолмен аяқтау</option>
                <option value="SCHEDULED">Белгіленген уақытта аяқтау</option>
              </select>
              
              <div v-if="settings.end_type === 'SCHEDULED'" class="grid grid-cols-2 gap-3 mt-1">
                <input type="date" v-model="settings.end_date" class="px-3 py-2 border border-slate-200 rounded-lg text-xs" />
                <input type="time" v-model="settings.end_time" class="px-3 py-2 border border-slate-200 rounded-lg text-xs" />
              </div>
            </div>

            <!-- ResultsVisibility (submit) -->
            <div class="form-group flex flex-col gap-2">
              <label class="text-sm font-semibold text-slate-700">Оқушы тапсырғаннан кейінгі нәтиже</label>
              <select v-model="settings.result_visibility" class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:border-emerald-500">
                <option value="ALWAYS">Ұпайлар мен дұрыс жауаптарды көрсету</option>
                <option value="SCORE_ONLY">Тек ұпайларды көрсету</option>
                <option value="HIDDEN">Нәтижелерді көрсетпеу</option>
              </select>
            </div>
          </div>

          <!-- Select target students -->
          <div class="border-t border-slate-100 pt-6 space-y-4">
            <div class="flex items-center justify-between">
              <label class="text-sm font-semibold text-slate-700">Оқушыларды таңдау</label>
              <button @click="showStudentSelector = true" class="px-4 py-2 border border-emerald-500 text-emerald-600 hover:bg-emerald-50 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
                Оқушыларды таңдау...
              </button>
            </div>
            
            <div class="bg-slate-50 rounded-xl p-4 border border-slate-100 text-xs text-slate-500 flex items-center gap-2">
              <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <span>{{ assignedStudentsLabel }}</span>
            </div>
          </div>

          <!-- Publish Action row -->
          <div class="border-t border-slate-100 pt-6 flex justify-end">
            <button 
              @click="publishQuiz" 
              :disabled="loading" 
              class="px-8 py-3.5 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-200 text-white disabled:text-slate-400 font-bold rounded-xl text-base transition-colors shadow-lg shadow-emerald-500/10 cursor-pointer disabled:cursor-not-allowed"
            >
              {{ loading ? 'Жариялануда...' : 'Квизді бастау (Жариялау)' }}
            </button>
          </div>
        </div>

        <!-- Mini Preview questions in Step 2 -->
        <div class="bg-slate-100 rounded-2xl p-6 border border-slate-200 space-y-4">
          <h4 class="font-bold text-slate-700 text-sm">Сұрақтар тізімін қарау ({{ selectedQuestions.length }} сұрақ)</h4>
          
          <div class="space-y-4 max-h-[300px] overflow-y-auto pr-2 divide-y divide-slate-200/60">
            <div v-for="(q, idx) in selectedQuestions" :key="q.id" class="pt-4 first:pt-0">
              <div class="text-xs font-bold text-slate-400 mb-1.5">Сұрақ {{ idx + 1 }} • Деңгей {{ q.level }}</div>
              <div class="text-sm text-slate-800 leading-snug" v-html="q.prompt"></div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Student Selection Dialog (Modal) -->
    <div v-if="showStudentSelector" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4" @click.self="showStudentSelector = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md border border-slate-100 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h3 class="font-bold text-slate-800 text-base">Оқушыларды таңдау</h3>
          <button @click="showStudentSelector = false" class="text-slate-400 hover:text-slate-600 font-bold text-lg">&times;</button>
        </div>

        <div class="px-6 py-4 max-h-80 overflow-y-auto space-y-1">
          <label class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-slate-50 cursor-pointer text-sm font-semibold text-slate-800">
            <input type="checkbox" v-model="selectAllStudents" class="w-4.5 h-4.5 text-emerald-600 border-slate-300 rounded focus:ring-emerald-500" />
            <span>Барлық оқушылар</span>
          </label>
          
          <div class="h-px bg-slate-100 my-2"></div>

          <label v-for="student in students" :key="student.id" class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-slate-50 cursor-pointer text-sm text-slate-700">
            <input type="checkbox" :value="student.id" v-model="assignedStudentIds" class="w-4.5 h-4.5 text-emerald-600 border-slate-300 rounded focus:ring-emerald-500" />
            <span>{{ student.full_name }}</span>
          </label>
        </div>

        <div class="px-6 py-4 border-t border-slate-100 bg-slate-50/50 flex justify-end">
          <button @click="showStudentSelector = false" class="px-5 py-2 bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-bold rounded-lg transition-colors">
            Дайын
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useCatalogStore } from '@/stores/catalog'
import { useTeacherStore } from '@/stores/teacher'
import { useQuizStore } from '@/stores/quiz'
import { teacherApi } from '@/api/teacher'
import { QuizQuestionOrder, QuizResultVisibility, QuizEndType } from '@/api/quiz'

const emit = defineEmits(['cancel', 'created'])

const props = defineProps({
  initialQuiz: {
    type: Object as () => any | null,
    default: null
  }
})

const catalogStore = useCatalogStore()
const teacherStore = useTeacherStore()
const quizStore = useQuizStore()

const currentStep = ref(1)
const quizName = ref('')

// Catalog Selections
const selectedGrade = ref<number | null>(null)
const selectedTheme = ref<any | null>(null)
const selectedSubtheme = ref<any | null>(null)
const selectedSkill = ref<any | null>(null)

// Skills, Question Pool and Preview states
const skillsList = ref<any[]>([])
const poolQuestions = ref<any[]>([])
const previewDifficulty = ref<number>(1)
const previewCount = ref<number>(1)
const showPreviewAnswer = ref(false)
const previewQuestion = ref<any | null>(null)

const activeQuestionIndex = ref<number | null>(null)
const selectedQuestions = ref<any[]>([])

const loadingQuestions = ref(false)
const loading = ref(false)

const showStudentSelector = ref(false)
const assignedStudentIds = ref<string[]>([])
const selectAllStudents = ref(false)

const settings = ref({
  question_order: QuizQuestionOrder.FIXED,
  result_visibility: QuizResultVisibility.ALWAYS,
  end_type: QuizEndType.MANUAL,
  end_date: '',
  end_time: ''
})

const grades = computed(() => catalogStore.grades)
const students = computed(() => teacherStore.students)

// Extract parent themes (parent_id is null)
const parentThemes = computed(() => {
  return catalogStore.topics.filter(t => !t.parent_id)
})

// Extract subthemes for the active parent theme
const childSubthemes = computed(() => {
  if (!selectedTheme.value) return []
  return catalogStore.topics.filter(t => t.parent_id === selectedTheme.value.id)
})

const assignedStudentsLabel = computed(() => {
  if (selectAllStudents.value) return 'Барлық оқушылар таңдалды'
  if (assignedStudentIds.value.length === 0) return 'Ешқандай оқушы таңдалмаған'
  return `${assignedStudentIds.value.length} оқушы таңдалды`
})

// Watch selectAllStudents change
watch(selectAllStudents, (val) => {
  if (val) {
    assignedStudentIds.value = students.value.map(s => s.id)
  } else if (assignedStudentIds.value.length === students.value.length) {
    assignedStudentIds.value = []
  }
})

// Catalog event handlers
const onGradeChange = async () => {
  selectedTheme.value = null
  selectedSubtheme.value = null
  selectedSkill.value = null
  skillsList.value = []
  poolQuestions.value = []
  previewQuestion.value = null
  await loadSkills()
}

const onThemeChange = async () => {
  selectedSubtheme.value = null
  selectedSkill.value = null
  poolQuestions.value = []
  previewQuestion.value = null
  await loadSkills()
}

const onSubthemeChange = async () => {
  selectedSkill.value = null
  poolQuestions.value = []
  previewQuestion.value = null
  await loadSkills()
}

const loadSkills = async () => {
  if (!selectedGrade.value) return
  
  let topicId = null
  if (selectedSubtheme.value) {
    topicId = selectedSubtheme.value.id
  } else if (selectedTheme.value) {
    topicId = selectedTheme.value.id
  }

  try {
    skillsList.value = await catalogStore.getSkills({
      grade_number: selectedGrade.value,
      topic_id: topicId,
      page_size: 500
    })
  } catch (err) {
    console.error('Failed to load skills:', err)
  }
}

const onSkillChange = async () => {
  if (!selectedSkill.value) return
  loadingQuestions.value = true
  poolQuestions.value = []
  previewQuestion.value = null
  showPreviewAnswer.value = false
  
  try {
    const res = await teacherApi.getSkillQuestions(selectedSkill.value.id)
    poolQuestions.value = res.data?.data || []
    selectNextPreviewQuestion()
  } catch (err) {
    console.error('Failed to load skill questions:', err)
  } finally {
    loadingQuestions.value = false
  }
}

// Filtered pool of questions by previewDifficulty
const filteredPoolQuestions = computed(() => {
  if (!poolQuestions.value.length) return []
  return poolQuestions.value.filter(q => q.level === previewDifficulty.value)
})

const onPreviewDifficultyChange = () => {
  selectNextPreviewQuestion()
  previewCount.value = 1
}

const selectNextPreviewQuestion = () => {
  const pool = filteredPoolQuestions.value
  if (pool.length > 0) {
    // Select a random question from pool
    const randIdx = Math.floor(Math.random() * pool.length)
    previewQuestion.value = pool[randIdx]
  } else {
    // Fallback: take any question from the pool if exact level not found
    previewQuestion.value = poolQuestions.value[0] || null
  }
}

const regeneratePreview = () => {
  selectNextPreviewQuestion()
}

// Add N questions to the list of selected questions
const addGeneratedQuestions = () => {
  if (!previewQuestion.value) return
  
  const pool = filteredPoolQuestions.value.length > 0 ? filteredPoolQuestions.value : poolQuestions.value
  if (!pool.length) return

  // Select N unique questions from pool randomly
  const poolCopy = [...pool]
  const countToAdd = Math.min(previewCount.value, poolCopy.length)
  
  const added: any[] = []
  for (let i = 0; i < countToAdd; i++) {
    const randIdx = Math.floor(Math.random() * poolCopy.length)
    const q = poolCopy.splice(randIdx, 1)[0]
    
    // Add custom properties for cards
    added.push({
      id: q.id,
      skill_id: selectedSkill.value.id,
      skill_title: selectedSkill.value.title,
      level: q.level,
      prompt: q.prompt,
      type: q.type,
      data: q.data,
      correct_answer: q.correct_answer,
      explanation: q.explanation,
      showAnswer: false
    })
  }

  // Deduplicate and push
  added.forEach(q => {
    if (!selectedQuestions.value.some(sq => sq.id === q.id)) {
      selectedQuestions.value.push(q)
    }
  })

  // Set active question
  if (selectedQuestions.value.length > 0) {
    activeQuestionIndex.value = selectedQuestions.value.length - 1
  }
  
  previewCount.value = 1
}

// Question navigation and actions in cards list
const scrollToQuestion = (idx: number) => {
  activeQuestionIndex.value = idx
  document.getElementById(`question-card-${idx}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

const addNewQuestionSlot = () => {
  // Try to copy the preview question, or the last selected question
  if (previewQuestion.value && selectedSkill.value) {
    const q = previewQuestion.value
    selectedQuestions.value.push({
      id: q.id,
      skill_id: selectedSkill.value.id,
      skill_title: selectedSkill.value.title,
      level: q.level,
      prompt: q.prompt,
      type: q.type,
      data: q.data,
      correct_answer: q.correct_answer,
      explanation: q.explanation,
      showAnswer: false
    })
    activeQuestionIndex.value = selectedQuestions.value.length - 1
  } else if (selectedQuestions.value.length > 0) {
    const lastQ = selectedQuestions.value[selectedQuestions.value.length - 1]
    selectedQuestions.value.push({
      ...lastQ,
      id: lastQ.id + Math.floor(Math.random() * 1000) + 1, // temporary unique key
      showAnswer: false
    })
    activeQuestionIndex.value = selectedQuestions.value.length - 1
  } else {
    alert('Сұрақ қосу үшін алдымен оқу санатынан дағдыны таңдаңыз.')
  }
}

const removeQuestionCard = (idx: number) => {
  selectedQuestions.value.splice(idx, 1)
  if (selectedQuestions.value.length === 0) {
    activeQuestionIndex.value = null
  } else {
    activeQuestionIndex.value = Math.max(0, idx - 1)
  }
}

// Change card specific skill
const changeCardSkill = async (idx: number, skillId: number) => {
  const skillObj = skillsList.value.find(s => s.id === skillId)
  if (!skillObj) return
  
  try {
    const res = await teacherApi.getSkillQuestions(skillId)
    const questionsPool = res.data?.data || []
    
    // Choose a question from the new skill matching level
    const levelMatch = questionsPool.filter(q => q.level === selectedQuestions.value[idx].level)
    const newQ = levelMatch[0] || questionsPool[0]
    
    if (newQ) {
      selectedQuestions.value[idx] = {
        ...selectedQuestions.value[idx],
        id: newQ.id,
        skill_id: skillId,
        skill_title: skillObj.title,
        prompt: newQ.prompt,
        type: newQ.type,
        data: newQ.data,
        correct_answer: newQ.correct_answer,
        explanation: newQ.explanation
      }
    } else {
      alert('Бұл дағдыда сұрақтар табылмады.')
    }
  } catch (err) {
    console.error('Failed to change card skill:', err)
  }
}

// Change card specific difficulty level
const changeCardLevel = async (idx: number, level: number) => {
  const card = selectedQuestions.value[idx]
  try {
    const res = await teacherApi.getSkillQuestions(card.skill_id)
    const questionsPool = res.data?.data || []
    
    const levelMatch = questionsPool.filter(q => q.level === level)
    const newQ = levelMatch[0] || questionsPool[0]
    
    if (newQ) {
      selectedQuestions.value[idx] = {
        ...card,
        id: newQ.id,
        level: newQ.level,
        prompt: newQ.prompt,
        type: newQ.type,
        data: newQ.data,
        correct_answer: newQ.correct_answer,
        explanation: newQ.explanation
      }
    } else {
      alert(`Таңдалған деңгей (${level}) үшін сұрақ табылмады.`);
    }
  } catch (err) {
    console.error('Failed to change card level:', err)
  }
}

// Regenerate specific question inside a card slot (Жаңа сұрақ генерациялау)
const regenerateQuestionCard = async (idx: number) => {
  const card = selectedQuestions.value[idx]
  try {
    const res = await teacherApi.getSkillQuestions(card.skill_id)
    const questionsPool = res.data?.data || []
    
    // Filter questions matching card level, exclude current question id if possible
    let matches = questionsPool.filter(q => q.level === card.level)
    if (matches.length > 1) {
      matches = matches.filter(q => q.id !== card.id)
    }
    
    const newQ = matches[Math.floor(Math.random() * matches.length)] || questionsPool[0]
    
    if (newQ) {
      selectedQuestions.value[idx] = {
        ...card,
        id: newQ.id,
        prompt: newQ.prompt,
        type: newQ.type,
        data: newQ.data,
        correct_answer: newQ.correct_answer,
        explanation: newQ.explanation
      }
    }
  } catch (err) {
    console.error('Failed to regenerate card question:', err)
  }
}

// Option formatting and correct answer matching
const formatMCQOption = (option: any) => {
  if (typeof option === 'object' && option !== null) {
    return option.text || option.label || option.value || option.id || ''
  }
  return String(option)
}

const isOptionCorrect = (question: any, option: any, index: number) => {
  const correctChoice = question.correct_answer?.choice
  if (correctChoice) {
    const optionId = option.id || option.label || index
    return String(optionId).toUpperCase() === String(correctChoice).toUpperCase()
  }
  
  const correctVal = question.correct_answer?.value
  if (correctVal) {
    const optionText = option.text || option.value || option
    return String(optionText).toUpperCase() === String(correctVal).toUpperCase()
  }
  return false
}

// Step controls
const nextStep = () => {
  currentStep.value = 2
}

const isEditing = computed(() => !!props.initialQuiz)

// Publish the created or modified quiz to DB and assign it
const publishQuiz = async () => {
  if (selectedQuestions.value.length === 0) {
    alert('Кем дегенде 1 сұрақ таңдаңыз')
    return
  }
  if (!quizName.value.trim()) {
    alert('Квиз атауын енгізіңіз')
    return
  }

  loading.value = true
  try {
    const payload = {
      name: quizName.value,
      question_order: settings.value.question_order as any,
      result_visibility: settings.value.result_visibility as any,
      end_type: settings.value.end_type as any,
      questions: selectedQuestions.value.map((q, i) => ({
        question_id: q.id,
        position: i
      }))
    }

    let createdQuiz
    if (isEditing.value) {
      createdQuiz = await quizStore.updateQuiz(props.initialQuiz.id, payload)
    } else {
      createdQuiz = await quizStore.createQuiz(payload)
    }

    // Assign to students
    if (selectAllStudents.value) {
      await quizStore.assignQuiz({
        quiz_id: createdQuiz.id,
      })
    } else {
      for (const studentId of assignedStudentIds.value) {
        await quizStore.assignQuiz({
          quiz_id: createdQuiz.id,
          student_id: studentId
        })
      }
    }

    emit('created')
  } catch (err: any) {
    alert(err.response?.data?.message || err.message || 'Error publishing quiz')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    catalogStore.getGrades(),
    catalogStore.getTopics(),
    teacherStore.fetchStudents()
  ])
  
  if (props.initialQuiz) {
    quizName.value = props.initialQuiz.name
    settings.value.question_order = props.initialQuiz.question_order
    settings.value.result_visibility = props.initialQuiz.result_visibility
    settings.value.end_type = props.initialQuiz.end_type
    
    // Map initial questions with custom details
    if (props.initialQuiz.questions) {
      selectedQuestions.value = props.initialQuiz.questions.map((q: any) => ({
        id: q.question_id,
        skill_id: q.question?.skill_id || 0,
        skill_title: q.question?.skill?.title || 'Енгізілген дағды',
        level: q.question?.level || 1,
        prompt: q.question ? q.question.prompt : 'Сұрақ мәтіні жүктелмеді',
        type: q.question?.type || 'MCQ',
        data: q.question?.data || {},
        correct_answer: q.question?.correct_answer || {},
        explanation: q.question?.explanation || '',
        showAnswer: false
      }))
    }
    
    if (selectedQuestions.value.length > 0) {
      activeQuestionIndex.value = 0
    }
  }
})
</script>

<style scoped>
.quiz-creator {
  background: #f8fbff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.next-btn:disabled {
  box-shadow: none;
}
</style>
