<template>
  <div class="quiz-creator min-h-screen bg-[#dcf2ff] py-8 px-4">
    <!-- STEP 1: ADD QUESTIONS -->
    <div v-if="currentStep === 1" class="step-container max-w-[1215px] w-[82%] mx-auto">
      
      <div class="relative flex gap-6 items-start">
        
        <!-- Left Question Navigator (Sidebar Index - Vertically Centered Pill) -->
        <div class="hidden xl:flex flex-col gap-2.5 sticky top-[35vh] -left-16 bg-[#c6e8fa] p-3 rounded-3xl border border-cyan-200/50 items-center z-20 max-h-[calc(100vh-140px)] overflow-y-auto shrink-0 shadow-xs">
          <button 
            v-for="(q, idx) in selectedQuestions" 
            :key="q.id"
            @click="scrollToQuestion(idx)"
            class="w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm border transition-all shrink-0 shadow-xs cursor-pointer"
            :class="[
              activeQuestionIndex === idx 
                ? 'bg-[#00a5e5] border-[#00a5e5] text-white shadow-sm scale-105' 
                : 'bg-white border-transparent text-[#00a5e5] hover:bg-cyan-50'
            ]"
            :title="`Сұрақ ${idx + 1}`"
          >
            {{ idx + 1 }}
          </button>
          <button 
            @click="openGeneratorPanel"
            class="w-9 h-9 rounded-full flex items-center justify-center font-bold text-lg bg-white border border-transparent text-[#00a5e5] hover:bg-cyan-50 transition-all shrink-0 shadow-xs cursor-pointer"
            title="Жаңа сұрақ ұяшығын қосу"
          >
            +
          </button>
        </div>

        <!-- Main Content Column -->
        <div class="flex-1 flex flex-col gap-6 min-w-0">

          <!-- Quiz Name, Step Title & Exit Button (Combined Card Container) -->
          <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs space-y-4">
            <!-- Top row inside card: STEP 1 OF 2 & Exit/Back button -->
            <div class="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider border-b border-slate-100 pb-3">
              <span>1-ҚАДАМ / 2: Сұрақтарды қосу</span>
              <div class="flex items-center gap-3">
                <span class="flex items-center gap-1.5 text-slate-400 font-normal lowercase normal-case text-xs">
                  <svg class="w-3.5 h-3.5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                  Өзгерістер автоматты түрде сақталады
                </span>
                <button @click="handleBack" class="text-slate-400 hover:text-slate-700 transition-colors p-1" title="Шығу / Артқа">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                </button>
              </div>
            </div>

            <!-- Input field -->
            <div>
              <input 
                v-model="quizName" 
                type="text" 
                placeholder="Квиз атауын енгізіңіз..." 
                class="w-full px-4 py-3.5 border border-slate-200 rounded-lg text-lg font-normal text-slate-700 placeholder-slate-400 focus:outline-none focus:border-[#00a5e5] focus:ring-1 focus:ring-[#00a5e5] transition-all bg-slate-50/20"
              />
            </div>

            <!-- Review and publish button -->
            <div>
              <button 
                @click="nextStep" 
                :disabled="!quizName.trim() || selectedQuestions.length === 0" 
                class="px-6 py-2.5 bg-[#00a5e5] hover:bg-[#0092cc] disabled:bg-slate-200 text-white disabled:text-slate-400 rounded-lg font-bold text-sm transition-all shadow-xs cursor-pointer disabled:cursor-not-allowed"
              >
                Қарап шығу және жариялау
              </button>
            </div>
          </div>

          <!-- Empty placeholder when nothing added yet AND generator is closed -->
          <div v-if="selectedQuestions.length === 0 && !showGeneratorPanel" class="bg-white rounded-2xl border border-dashed border-slate-200 p-12 text-center text-slate-400 shadow-sm">
            <svg class="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
            <p class="font-semibold text-slate-700 mb-1">Сұрақтар әлі таңдалмаған</p>
            <p class="text-xs">Жоғарыдағы сұрақтар генераторынан дағдыны таңдап, квизге сұрақтарды қосыңыз.</p>
          </div>

          <!-- List of Question Cards -->
          <div v-if="selectedQuestions.length > 0" class="flex flex-col gap-6">
            <div 
              v-for="(q, idx) in selectedQuestions" 
              :key="q.id" 
              :id="`question-card-${idx}`"
              class="question-card bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden transition-all duration-200"
              :class="{ 'ring-2 ring-[#00a5e5]/30 border-[#00a5e5]': activeQuestionIndex === idx }"
              @click="activeQuestionIndex = idx"
            >
              <div class="border-b border-slate-100 bg-slate-50/50 px-6 py-3.5 space-y-2">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span class="text-slate-400 font-bold text-base cursor-grab">≡</span>
                    <span class="font-extrabold text-slate-700 text-xs tracking-wider uppercase">QUESTION {{ idx + 1 }}</span>
                  </div>

                  <button @click.stop="removeQuestionCard(idx)" class="text-slate-400 hover:text-rose-600 transition-colors p-1" title="Сұрақты өшіру">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                </div>
                
                <div class="flex flex-wrap items-center justify-between gap-3 text-xs pt-1">
                  <div class="flex flex-wrap items-center gap-3">
                    <!-- Skill Selector Button (Opens IXL Hierarchical Dropdown) -->
                    <div class="relative dropdown-container-el flex items-center gap-1.5">
                      <span class="text-slate-400 font-semibold text-xs">Дағды:</span>
                      <button 
                        @click.stop="toggleCardSkillDropdown(idx)" 
                        class="flex items-center justify-between gap-2 px-3 py-1.5 bg-white border border-cyan-200 rounded-xl text-slate-700 font-semibold text-xs shadow-xs hover:border-cyan-300 transition-all cursor-pointer max-w-[280px]"
                      >
                        <span class="truncate text-slate-700">
                          {{ q.skill_title ? `${q.skill_title}` : 'Дағдыны таңдаңыз' }}
                        </span>
                        <svg class="w-3.5 h-3.5 text-cyan-500 shrink-0 transition-transform duration-200" :class="{ 'rotate-180': activeCardDropdownIdx === idx }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                      </button>

                      <!-- CUSTOM HIERARCHICAL DROPDOWN PANEL FOR CARD -->
                      <div v-if="activeCardDropdownIdx === idx" class="absolute z-30 top-full left-0 mt-2 bg-white border border-slate-200/90 rounded-2xl shadow-2xl p-4 min-w-[340px] max-w-[360px] max-h-[440px] overflow-y-auto space-y-3 text-left">
                        <!-- Search Input Bar -->
                        <div class="relative mb-2">
                          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                          </div>
                          <input 
                            v-model="skillSearchQuery" 
                            type="text" 
                            placeholder="Дағды атауы бойынша іздеу..." 
                            class="w-full pl-9 pr-3 py-2 border border-slate-200 rounded-xl text-xs text-slate-700 placeholder:italic placeholder-slate-400 focus:outline-none focus:border-[#00a5e5] focus:ring-1 focus:ring-[#00a5e5] transition-all bg-slate-50/50"
                          />
                        </div>

                        <!-- Search Results (if searching) -->
                        <div v-if="skillSearchQuery.trim()" class="divide-y divide-slate-100">
                          <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider pb-1 px-4">Нәтижелер</div>
                          <div v-if="searchSkillsList.length === 0" class="py-4 text-center text-xs text-slate-400">
                            Дағды табылмады.
                          </div>
                          <button 
                            v-for="s in searchSkillsList" 
                            :key="s.id as PropertyKey" 
                            @click="selectDropdownSkill(s)"
                            class="w-full text-left px-4 py-2.5 text-xs font-medium text-slate-700 hover:bg-[#00a5e5] hover:text-white transition-all flex items-center justify-between group cursor-pointer"
                          >
                            <div class="flex flex-col gap-0.5">
                              <span class="text-[10px] font-bold text-[#00a5e5] group-hover:text-cyan-100 uppercase">{{ s.code }}</span>
                              <span>{{ s.title }}</span>
                            </div>
                            <span class="opacity-0 group-hover:opacity-100 font-bold text-sm transition-opacity">›</span>
                          </button>
                        </div>

                        <!-- Browse Catalog Mode -->
                        <template v-else>
                          <div class="border-b border-slate-100 pb-2 space-y-1 px-1">
                            <div class="text-[11px] italic text-slate-400">немесе төмендегі тізімнен таңдаңыз</div>
                            <div class="flex items-center justify-between">
                              <button 
                                v-if="dropdownStep !== 'grade'" 
                                @click="goBackDropdown" 
                                class="text-xs font-bold text-slate-700 hover:text-[#00a5e5] flex items-center gap-1 cursor-pointer transition-colors"
                              >
                                <span class="text-[#00a5e5] font-bold text-sm">‹</span> Сыныпты таңдау
                              </button>
                              <span v-else class="text-xs font-bold text-slate-700 flex items-center gap-1">
                                <span class="text-slate-400 font-bold text-sm">‹</span> Сыныпты таңдау
                              </span>

                              <span v-if="selectedGrade" class="text-xs font-semibold text-[#00a5e5] bg-cyan-50 px-2 py-0.5 rounded-md">
                                {{ selectedGrade }} сынып
                              </span>
                            </div>
                          </div>

                          <!-- STEP 1: GRADE LIST -->
                          <div v-if="dropdownStep === 'grade'" class="divide-y divide-slate-100 pt-1">
                            <button 
                              v-for="g in grades" 
                              :key="g.id" 
                              @click="selectDropdownGrade(g.number)"
                              class="w-full text-left px-4 py-2.5 text-xs font-medium text-slate-700 hover:bg-[#00a5e5] hover:text-white transition-all flex items-center justify-between cursor-pointer group"
                            >
                              <span>{{ g.number }}-сынып</span>
                              <span class="opacity-0 group-hover:opacity-100 font-bold text-sm transition-opacity">›</span>
                            </button>
                          </div>

                          <!-- STEP 2: CATALOG (THEMES & SKILLS) -->
                          <div v-else-if="dropdownStep === 'catalog'" class="space-y-3 pt-1">
                            <div v-if="catalogGroups.groups.length === 0 && catalogGroups.orphaned.length === 0" class="py-6 text-center text-xs text-slate-400">
                              Дағдылар табылмады.
                            </div>

                            <div class="space-y-3">
                              <div v-for="group in catalogGroups.groups" :key="group.theme.id" class="space-y-1">
                                <h5 class="text-[11px] font-bold text-slate-800 border-b border-slate-100 pb-1 mt-2 uppercase tracking-wider px-2">
                                  {{ group.theme.title }}
                                </h5>
                                
                                <div v-if="group.directSkills.length > 0" class="divide-y divide-slate-100">
                                  <button 
                                    v-for="skill in group.directSkills" 
                                    :key="skill.id" 
                                    @click="selectDropdownSkill(skill)"
                                    class="w-full text-left px-4 py-2 text-xs font-medium text-slate-700 hover:bg-[#00a5e5] hover:text-white transition-all flex items-center justify-between cursor-pointer group"
                                  >
                                    <div class="flex flex-col gap-0.5">
                                      <span class="text-[9px] font-bold text-[#00a5e5] group-hover:text-cyan-100 uppercase">{{ skill.code }}</span>
                                      <span>{{ skill.title }}</span>
                                    </div>
                                    <span class="opacity-0 group-hover:opacity-100 font-bold text-sm transition-opacity">›</span>
                                  </button>
                                </div>

                                <div v-for="sub in group.subthemes" :key="sub.subtheme.id" class="space-y-1">
                                  <h6 class="text-[10px] font-bold text-slate-500 mt-2 mb-1 px-2">
                                    {{ sub.subtheme.title }}
                                  </h6>
                                  
                                  <div class="divide-y divide-slate-100">
                                    <button 
                                      v-for="skill in sub.skills" 
                                      :key="skill.id" 
                                      @click="selectDropdownSkill(skill)"
                                      class="w-full text-left px-4 py-2 text-xs font-medium text-slate-700 hover:bg-[#00a5e5] hover:text-white transition-all flex items-center justify-between cursor-pointer group"
                                    >
                                      <div class="flex flex-col gap-0.5">
                                        <span class="text-[9px] font-bold text-[#00a5e5] group-hover:text-cyan-100 uppercase">{{ skill.code }}</span>
                                        <span>{{ skill.title }}</span>
                                      </div>
                                      <span class="opacity-0 group-hover:opacity-100 font-bold text-sm transition-opacity">›</span>
                                    </button>
                                  </div>
                                </div>
                              </div>

                              <div v-if="catalogGroups.orphaned.length > 0" class="space-y-1">
                                <h5 class="text-[11px] font-bold text-slate-800 border-b border-slate-100 pb-1 mt-2 uppercase tracking-wider px-2">
                                  Басқа дағдылар
                                </h5>
                                <div class="divide-y divide-slate-100">
                                  <button 
                                    v-for="skill in catalogGroups.orphaned" 
                                    :key="skill.id" 
                                    @click="selectDropdownSkill(skill)"
                                    class="w-full text-left px-4 py-2 text-xs font-medium text-slate-700 hover:bg-[#00a5e5] hover:text-white transition-all flex items-center justify-between cursor-pointer group"
                                  >
                                    <div class="flex flex-col gap-0.5">
                                      <span class="text-[9px] font-bold text-[#00a5e5] group-hover:text-cyan-100 uppercase">{{ skill.code }}</span>
                                      <span>{{ skill.title }}</span>
                                    </div>
                                    <span class="opacity-0 group-hover:opacity-100 font-bold text-sm transition-opacity">›</span>
                                  </button>
                                </div>
                              </div>
                            </div>
                          </div>
                        </template>
                      </div>
                    </div>

                    <!-- Level Selector Dropdown -->
                    <div class="flex items-center gap-1.5">
                      <span class="text-slate-400 font-semibold text-xs">Деңгей:</span>
                      <select 
                        :value="q.level" 
                        @change="changeCardLevel(idx, Number(($event.target as HTMLSelectElement).value))" 
                        class="px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white text-slate-700 font-bold text-xs focus:outline-none focus:border-[#00a5e5] shadow-xs cursor-pointer"
                      >
                        <option :value="1">1-деңгей 🏷️</option>
                        <option :value="2">2-деңгей 🏷️</option>
                        <option :value="3">3-деңгей 🏷️</option>
                        <option :value="4">4-деңгей 🏷️</option>
                        <option :value="5">5-деңгей 🏷️</option>
                      </select>
                    </div>
                  </div>

                  <button @click.stop="regenerateQuestionCard(idx)" class="text-xs text-[#00a5e5] hover:text-[#0082b5] font-semibold flex items-center gap-1 cursor-pointer">
                    Жаңа сұрақ генерациялау ↻
                  </button>
                </div>
              </div>

              <!-- Question Content & Custom Options -->
              <div class="p-6 space-y-4">
                <!-- Prompt -->
                <div v-if="!isQuestionPlugin(q)" class="text-sm font-semibold text-slate-800" v-html="q.prompt"></div>

                <!-- PLUGIN / INTERACTIVE -->
                <div v-if="isQuestionPlugin(q)" class="space-y-3">
                  <div class="relative w-full overflow-hidden rounded-xl border border-slate-200 bg-white">
                    <iframe
                      v-if="q.iframeSrcdoc || q.iframeSrc"
                      :srcdoc="q.iframeSrcdoc || undefined"
                      :src="q.iframeSrcdoc ? undefined : q.iframeSrc"
                      :data-card-id="q.id"
                      :style="{ height: (q.height || 500) + 'px' }"
                      class="w-full border-0"
                      sandbox="allow-scripts"
                      scrolling="no"
                    ></iframe>
                  </div>
                  <div v-if="q.showAnswer && q.explanation" class="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600 leading-relaxed">
                    <span class="font-semibold text-slate-700">Түсіндірме:</span> {{ q.explanation }}
                  </div>
                </div>

                <!-- MCQ Choices -->
                <div v-else-if="q.type === 'MCQ'" class="grid grid-cols-1 md:grid-cols-2 gap-3">
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
                <div class="flex items-center justify-between pt-3 border-t border-slate-100">
                  <div v-if="q.showAnswer" class="flex items-center gap-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-lg">
                    <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                    <span>Дұрыс жауабы көрсетілді</span>
                  </div>
                  <div v-else></div>

                  <button @click.stop="toggleCardAnswer(q)" class="text-xs font-semibold text-[#00a5e5] hover:text-[#0082b5] flex items-center gap-1 cursor-pointer">
                    {{ q.showAnswer ? 'Жауапты жасыру ⊟' : 'Дұрыс жауабын көрсету ⊞' }}
                  </button>
                </div>

              </div>
            </div>
          </div>

          <!-- ─── Generator Panel (White Container, 10% Narrower) ─── -->
          <div v-if="showGeneratorPanel" id="generator-panel" class="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-xs space-y-4 max-w-[765px] w-full mx-auto">
            
            <!-- Top Controls Row: Skill Pill & Level Selector with Arrows -->
            <div class="flex flex-wrap items-center justify-between gap-3">
              
              <!-- Left: Skill Selector Dropdown Pill -->
              <div class="relative dropdown-container-el flex-1 min-w-[280px]">
                <button 
                  @click="showSkillDropdown = !showSkillDropdown" 
                  class="w-full flex items-center justify-between px-4 py-2.5 bg-white border border-cyan-200 rounded-xl text-slate-700 font-semibold text-sm shadow-xs hover:border-cyan-300 transition-all cursor-pointer"
                >
                  <span class="truncate text-slate-700">
                    {{ selectedSkill ? `${selectedSkill.code} - ${selectedSkill.title}` : 'Дағдыны таңдаңыз' }}
                  </span>
                  <svg class="w-4 h-4 text-cyan-500 shrink-0 ml-2 transition-transform duration-200" :class="{ 'rotate-180': showSkillDropdown }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                </button>

                <!-- CUSTOM HIERARCHICAL DROPDOWN PANEL (IXL STYLE) -->
                <div v-if="showSkillDropdown" class="absolute z-30 top-full left-0 right-0 mt-2 bg-white border border-slate-200/90 rounded-2xl shadow-2xl p-4 min-w-[340px] max-h-[460px] overflow-y-auto space-y-3">
                  
                  <!-- Search Input Bar -->
                  <div class="relative mb-2">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                    </div>
                    <input 
                      v-model="skillSearchQuery" 
                      type="text" 
                      placeholder="Дағды атауы бойынша іздеу..." 
                      class="w-full pl-9 pr-3 py-2 border border-slate-200 rounded-xl text-xs text-slate-700 placeholder:italic placeholder-slate-400 focus:outline-none focus:border-[#00a5e5] focus:ring-1 focus:ring-[#00a5e5] transition-all bg-slate-50/50"
                    />
                  </div>

                  <!-- Search Results (if searching) -->
                  <div v-if="skillSearchQuery.trim()" class="divide-y divide-slate-100">
                    <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider pb-1 px-4">Нәтижелер</div>
                    <div v-if="searchSkillsList.length === 0" class="py-4 text-center text-xs text-slate-400">
                      Дағды табылмады.
                    </div>
                    <button 
                      v-for="s in searchSkillsList" 
                      :key="s.id as PropertyKey" 
                      @click="selectDropdownSkill(s); skillSearchQuery = ''"
                      class="w-full text-left px-4 py-2.5 text-xs font-medium text-slate-700 hover:bg-[#00a5e5] hover:text-white transition-all flex items-center justify-between group cursor-pointer"
                    >
                      <div class="flex flex-col gap-0.5">
                        <span class="text-[10px] font-bold text-[#00a5e5] group-hover:text-cyan-100 uppercase">{{ s.code }}</span>
                        <span>{{ s.title }}</span>
                      </div>
                      <span class="opacity-0 group-hover:opacity-100 font-bold text-sm transition-opacity">›</span>
                    </button>
                  </div>

                  <!-- Browse Catalog Mode (when not searching) -->
                  <template v-else>
                    <!-- Sub-header & Navigation -->
                    <div class="border-b border-slate-100 pb-2 space-y-1 px-1">
                      <div class="text-[11px] italic text-slate-400">немесе төмендегі тізімнен таңдаңыз</div>
                      <div class="flex items-center justify-between">
                        <button 
                          v-if="dropdownStep !== 'grade'" 
                          @click="goBackDropdown" 
                          class="text-xs font-bold text-slate-700 hover:text-[#00a5e5] flex items-center gap-1 cursor-pointer transition-colors"
                        >
                          <span class="text-[#00a5e5] font-bold text-sm">‹</span> Сыныпты таңдау
                        </button>
                        <span v-else class="text-xs font-bold text-slate-700 flex items-center gap-1">
                          <span class="text-slate-400 font-bold text-sm">‹</span> Сыныпты таңдау
                        </span>

                        <span v-if="selectedGrade" class="text-xs font-semibold text-[#00a5e5] bg-cyan-50 px-2 py-0.5 rounded-md">
                          {{ selectedGrade }} сынып
                        </span>
                      </div>
                    </div>

                    <!-- STEP 1: GRADE LIST (Vertical list without rounding matching IXL) -->
                    <div v-if="dropdownStep === 'grade'" class="divide-y divide-slate-100 pt-1">
                      <button 
                        v-for="g in grades" 
                        :key="g.id" 
                        @click="selectDropdownGrade(g.number)"
                        class="w-full text-left px-4 py-2.5 text-xs font-medium text-slate-700 hover:bg-[#00a5e5] hover:text-white transition-all flex items-center justify-between cursor-pointer group"
                      >
                        <span>{{ g.number }}-сынып</span>
                        <span class="opacity-0 group-hover:opacity-100 font-bold text-sm transition-opacity">›</span>
                      </button>
                    </div>

                    <!-- STEP 2: CATALOG (THEMES & SKILLS) -->
                    <div v-else-if="dropdownStep === 'catalog'" class="space-y-3 pt-1">
                      <div v-if="catalogGroups.groups.length === 0 && catalogGroups.orphaned.length === 0" class="py-6 text-center text-xs text-slate-400">
                        Дағдылар табылмады.
                      </div>

                      <div class="space-y-3">
                        <!-- Grouped Themes -->
                        <div v-for="group in catalogGroups.groups" :key="group.theme.id" class="space-y-1">
                          <h5 class="text-[11px] font-bold text-slate-800 border-b border-slate-100 pb-1 mt-2 uppercase tracking-wider px-2">
                            {{ group.theme.title }}
                          </h5>
                          
                          <div v-if="group.directSkills.length > 0" class="divide-y divide-slate-100">
                            <button 
                              v-for="skill in group.directSkills" 
                              :key="skill.id" 
                              @click="selectDropdownSkill(skill)"
                              class="w-full text-left px-4 py-2 text-xs font-medium text-slate-700 hover:bg-[#00a5e5] hover:text-white transition-all flex items-center justify-between cursor-pointer group"
                            >
                              <div class="flex flex-col gap-0.5">
                                <span class="text-[9px] font-bold text-[#00a5e5] group-hover:text-cyan-100 uppercase">{{ skill.code }}</span>
                                <span>{{ skill.title }}</span>
                              </div>
                              <span class="opacity-0 group-hover:opacity-100 font-bold text-sm transition-opacity">›</span>
                            </button>
                          </div>

                          <div v-for="sub in group.subthemes" :key="sub.subtheme.id" class="space-y-1">
                            <h6 class="text-[10px] font-bold text-slate-500 mt-2 mb-1 px-2">
                              {{ sub.subtheme.title }}
                            </h6>
                            
                            <div class="divide-y divide-slate-100">
                              <button 
                                v-for="skill in sub.skills" 
                                :key="skill.id" 
                                @click="selectDropdownSkill(skill)"
                                class="w-full text-left px-4 py-2 text-xs font-medium text-slate-700 hover:bg-[#00a5e5] hover:text-white transition-all flex items-center justify-between cursor-pointer group"
                              >
                                <div class="flex flex-col gap-0.5">
                                  <span class="text-[9px] font-bold text-[#00a5e5] group-hover:text-cyan-100 uppercase">{{ skill.code }}</span>
                                  <span>{{ skill.title }}</span>
                                </div>
                                <span class="opacity-0 group-hover:opacity-100 font-bold text-sm transition-opacity">›</span>
                              </button>
                            </div>
                          </div>
                        </div>

                        <!-- Orphaned Skills -->
                        <div v-if="catalogGroups.orphaned.length > 0" class="space-y-1">
                          <h5 class="text-[11px] font-bold text-slate-800 border-b border-slate-100 pb-1 mt-2 uppercase tracking-wider px-2">
                            Басқа дағдылар
                          </h5>
                          <div class="divide-y divide-slate-100">
                            <button 
                              v-for="skill in catalogGroups.orphaned" 
                              :key="skill.id" 
                              @click="selectDropdownSkill(skill)"
                              class="w-full text-left px-4 py-2 text-xs font-medium text-slate-700 hover:bg-[#00a5e5] hover:text-white transition-all flex items-center justify-between cursor-pointer group"
                            >
                              <div class="flex flex-col gap-0.5">
                                <span class="text-[9px] font-bold text-[#00a5e5] group-hover:text-cyan-100 uppercase">{{ skill.code }}</span>
                                <span>{{ skill.title }}</span>
                              </div>
                              <span class="opacity-0 group-hover:opacity-100 font-bold text-sm transition-opacity">›</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </template>
                </div>
              </div>

              <!-- Right: Level selector with arrows -->
              <div class="flex items-center gap-1.5 shrink-0">
                <button 
                  @click="previewDifficulty = Math.max(1, previewDifficulty - 1); onPreviewDifficultyChange()" 
                  class="text-[#00a5e5] hover:text-[#0082b5] font-bold text-sm px-1 cursor-pointer"
                  title="Алдыңғы деңгей"
                >&lt;</button>
                
                <select v-model="previewDifficulty" @change="onPreviewDifficultyChange" class="px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 focus:outline-none focus:border-[#00a5e5] cursor-pointer">
                  <option :value="1">1-деңгей 🏷️</option>
                  <option :value="2">2-деңгей 🏷️</option>
                  <option :value="3">3-деңгей 🏷️</option>
                  <option :value="4">4-деңгей 🏷️</option>
                  <option :value="5">5-деңгей 🏷️</option>
                </select>

                <button 
                  @click="previewDifficulty = Math.min(5, previewDifficulty + 1); onPreviewDifficultyChange()" 
                  class="text-[#00a5e5] hover:text-[#0082b5] font-bold text-sm px-1 cursor-pointer"
                  title="Келесі деңгей"
                >&gt;</button>
              </div>

            </div>

            <!-- Center Box: Question Preview (or Empty State if no skill selected) -->
            <div class="bg-slate-50/60 rounded-2xl p-6 min-h-[160px] flex items-center justify-center border border-slate-100/80">
              <!-- Empty state: no skill selected -->
              <div v-if="!selectedSkill" class="py-8 text-center text-slate-400 font-medium text-sm">
                Бастау үшін дағдыны таңдап сұрақ қосыңыз!
              </div>

              <!-- Loading state -->
              <div v-else-if="loadingQuestions" class="py-8 text-center text-slate-400 font-medium text-sm">
                Жүктелуде...
              </div>

              <!-- No question for level -->
              <div v-else-if="!previewQuestion" class="py-8 text-center text-slate-400 font-medium text-sm">
                Бұл деңгей үшін сұрақ табылмады. Басқа деңгей таңдаңыз.
              </div>

              <!-- Preview Question Content -->
              <div v-else class="w-full space-y-4">
                <!-- Prompt -->
                <div v-if="!isQuestionPlugin(previewQuestion)" class="text-sm font-semibold text-slate-800" v-html="previewQuestion.prompt"></div>

                <!-- PLUGIN / INTERACTIVE -->
                <div v-if="isQuestionPlugin(previewQuestion)" class="relative w-full overflow-hidden rounded-xl border border-slate-200 bg-white pointer-events-none select-none">
                  <iframe
                    v-if="previewIframeSrcdoc || previewIframeSrc"
                    :srcdoc="previewIframeSrcdoc || undefined"
                    :src="previewIframeSrcdoc ? undefined : previewIframeSrc"
                    data-preview-iframe="true"
                    :style="{ height: previewIframeHeight + 'px' }"
                    class="w-full border-0"
                    sandbox="allow-scripts"
                    scrolling="no"
                  ></iframe>
                </div>

                <!-- MCQ Choices -->
                <div v-else-if="previewQuestion.type === 'MCQ'" class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div 
                    v-for="(option, index) in ((previewQuestion.data as Record<string, unknown>)?.choices as unknown[] || (previewQuestion.data as Record<string, unknown>)?.options as unknown[] || [])" 
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
                    Дұрыс мән: {{ (previewQuestion.correct_answer as Record<string, unknown>)?.value || (previewQuestion.correct_answer as Record<string, unknown>)?.choice || 'Көрсетілмеген' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Bottom Row: Stepper Counter & Add Questions Button -->
            <div class="flex items-center justify-between pt-1">
              <!-- Left: Number of questions stepper -->
              <div class="flex items-center gap-2 text-xs font-semibold text-slate-600">
                <span>Сұрақтар саны:</span>
                <button 
                  type="button" 
                  @click.prevent="previewCount = Math.max(1, previewCount - 1)" 
                  class="w-7 h-7 bg-white hover:bg-cyan-50 rounded-full border border-cyan-200 text-[#00a5e5] font-bold flex items-center justify-center shadow-xs cursor-pointer"
                >-</button>
                <span class="w-6 text-center text-sm font-bold text-slate-700">{{ previewCount }}</span>
                <button 
                  type="button" 
                  @click.prevent="previewCount = Math.min(20, previewCount + 1)" 
                  class="w-7 h-7 bg-white hover:bg-cyan-50 rounded-full border border-cyan-200 text-[#00a5e5] font-bold flex items-center justify-center shadow-xs cursor-pointer"
                >+</button>
              </div>

              <!-- Right: Add questions button -->
              <button 
                @click="addGeneratedQuestions" 
                :disabled="!previewQuestion" 
                class="px-6 py-2.5 bg-[#00a5e5] hover:bg-[#0092cc] disabled:bg-slate-200 text-white disabled:text-slate-400 font-bold rounded-xl text-sm transition-all shadow-xs cursor-pointer disabled:cursor-not-allowed"
              >
                Сұрақтарды қосу
              </button>
            </div>

          </div>

          <!-- ─── Add More Questions button (shown after questions are added and generator is hidden) ─── -->
          <button
            v-if="!showGeneratorPanel"
            @click="openGeneratorPanel"
            class="flex items-center justify-center gap-3 w-full py-5 border-2 border-dashed border-emerald-300 rounded-2xl text-emerald-600 hover:bg-emerald-50 hover:border-emerald-400 transition-all font-bold text-sm group"
          >
            <span class="w-9 h-9 rounded-full bg-emerald-100 group-hover:bg-emerald-200 flex items-center justify-center text-xl font-bold transition-colors">+</span>
            Жаңа дағды таңдап сұрақ қосу
          </button>

        </div>


      </div>
    </div>

    <!-- STEP 2: SETTINGS & PUBLISH -->
    <div v-else class="step-container max-w-[1215px] w-[82%] mx-auto py-6">
      <div class="w-full space-y-6">
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
                <option value="ALWAYS" :disabled="settings.ended_result_visibility === 'SCORE_ONLY' || settings.ended_result_visibility === 'HIDDEN'">Ұпайлар мен дұрыс жауаптарды көрсету</option>
                <option value="SCORE_ONLY" :disabled="settings.ended_result_visibility === 'HIDDEN'">Тек ұпайларды көрсету</option>
                <option value="HIDDEN">Нәтижелерді көрсетпеу</option>
              </select>
            </div>

            <!-- ResultsVisibility (ended) -->
            <div class="form-group flex flex-col gap-2">
              <label class="text-sm font-semibold text-slate-700">Мұғалім квизді аяқтағаннан кейінгі нәтиже</label>
              <select v-model="settings.ended_result_visibility" class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:border-emerald-500">
                <option value="ALWAYS">Ұпайлар мен дұрыс жауаптарды көрсету</option>
                <option value="SCORE_ONLY" :disabled="settings.result_visibility === 'ALWAYS'">Тек ұпайларды көрсету</option>
                <option value="HIDDEN" :disabled="settings.result_visibility === 'ALWAYS' || settings.result_visibility === 'SCORE_ONLY'">Нәтижелерді көрсетпеу</option>
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
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl border border-slate-100 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h3 class="font-bold text-slate-800 text-base">Оқушыларды таңдау</h3>
          <button @click="showStudentSelector = false" class="text-slate-400 hover:text-slate-600 font-bold text-lg">&times;</button>
        </div>

        <div class="px-6 py-4 max-h-80 overflow-y-auto space-y-1">
          <label class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-slate-50 cursor-pointer text-xs font-semibold text-slate-800">
            <input type="checkbox" v-model="selectAllStudents" class="w-4 h-4 text-emerald-600 border-slate-300 rounded focus:ring-emerald-500" />
            <span>Барлық оқушылар</span>
          </label>
          
          <div class="h-px bg-slate-100 my-2"></div>

          <label v-for="student in students" :key="student.id" class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-slate-50 cursor-pointer text-xs text-slate-700">
            <input type="checkbox" :value="student.id" v-model="assignedStudentIds" class="w-4 h-4 text-emerald-600 border-slate-300 rounded focus:ring-emerald-500" />
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
import { ref, computed, onMounted, onUnmounted, onBeforeUnmount, watch } from 'vue'
import { useCatalogStore } from '@/stores/catalog'
import { useTeacherStore } from '@/stores/teacher'
import { useQuizStore } from '@/stores/quiz'
import { teacherApi } from '@/api/teacher'
import { QuizQuestionOrder, QuizResultVisibility, QuizEndType } from '@/api/quiz'

const emit = defineEmits(['cancel', 'created'])

const props = defineProps({
  initialQuiz: {
    type: Object as () => Record<string, unknown> | null,
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
const selectedTheme = ref<Record<string, unknown> | null>(null)
const selectedSubtheme = ref<Record<string, unknown> | null>(null)
const selectedSkill = ref<Record<string, unknown> | null>(null)

// Hierarchical Dropdown state
const showSkillDropdown = ref(false)
const activeCardDropdownIdx = ref<number | null>(null)
const dropdownStep = ref<'grade' | 'catalog'>('grade')

const toggleCardSkillDropdown = (idx: number) => {
  if (activeCardDropdownIdx.value === idx) {
    activeCardDropdownIdx.value = null
  } else {
    showSkillDropdown.value = false
    activeCardDropdownIdx.value = idx
    dropdownStep.value = 'grade'
    skillSearchQuery.value = ''
  }
}

const selectDropdownGrade = async (gradeNum: number) => {
  selectedGrade.value = gradeNum
  loadingQuestions.value = true
  try {
    await catalogStore.getSkills({ grade_number: gradeNum, page_size: 500 })
    dropdownStep.value = 'catalog'
  } catch (err) {
    console.error('Failed to get skills for grade:', err)
  } finally {
    loadingQuestions.value = false
  }
}

const selectDropdownSkill = async (skill: Record<string, unknown>) => {
  if (activeCardDropdownIdx.value !== null) {
    const cardIdx = activeCardDropdownIdx.value
    activeCardDropdownIdx.value = null
    skillSearchQuery.value = ''
    await changeCardSkill(cardIdx, skill.id as number, skill)
    return
  }

  selectedSkill.value = skill
  showSkillDropdown.value = false
  skillSearchQuery.value = ''
  
  // Randomize preview difficulty between 1 and 5
  previewDifficulty.value = Math.floor(Math.random() * 5) + 1

  loadingQuestions.value = true
  poolQuestions.value = []
  previewQuestion.value = null
  showPreviewAnswer.value = false
  
  try {
    const res = await teacherApi.getSkillQuestions(skill.id as number)
    poolQuestions.value = res.data?.data || []
    selectNextPreviewQuestion()
  } catch (err) {
    console.error('Failed to get questions:', err)
  } finally {
    loadingQuestions.value = false
  }
}

// Compute nested catalog groups: Themes -> Subthemes -> Skills & direct skills
const catalogGroups = computed(() => {
  const currentSkills = catalogStore.skills
  const allTopics = catalogStore.topics
  
  // Find top level themes (parent_id is null)
  const topThemes = allTopics.filter(t => !t.parent_id).sort((a, b) => a.order - b.order)

  const groups: Array<{
    theme: ReturnType<typeof allTopics.filter>[number]
    subthemes: Array<{
      subtheme: ReturnType<typeof allTopics.filter>[number]
      skills: ReturnType<typeof currentSkills.filter>
    }>
    directSkills: ReturnType<typeof currentSkills.filter>
  }> = []
  
  const accountedSkillIds = new Set<number>()
  
  topThemes.forEach(theme => {
    // Find subthemes under this theme
    const subthemes = allTopics.filter(t => t.parent_id === theme.id).sort((a, b) => a.order - b.order)
    const subthemeList: { subtheme: ReturnType<typeof allTopics.filter>[number]; skills: ReturnType<typeof currentSkills.filter> }[] = []
    
    subthemes.forEach(sub => {
      const subSkills = currentSkills.filter(s => s.topic_id === sub.id)
      if (subSkills.length > 0) {
        subthemeList.push({
          subtheme: sub,
          skills: subSkills
        })
        subSkills.forEach(s => accountedSkillIds.add(s.id))
      }
    })
    
    // Direct skills belonging to this theme directly
    const directSkills = currentSkills.filter(s => s.topic_id === theme.id)
    directSkills.forEach(s => accountedSkillIds.add(s.id))
    
    if (subthemeList.length > 0 || directSkills.length > 0) {
      groups.push({
        theme,
        subthemes: subthemeList,
        directSkills
      })
    }
  })
  
  // Skills with no theme or topic_id that doesn't match any theme/subtheme
  const orphanedSkills = currentSkills.filter(s => !accountedSkillIds.has(s.id))
  
  return {
    groups,
    orphaned: orphanedSkills
  }
})



const goBackDropdown = () => {
  if (dropdownStep.value === 'catalog') {
    dropdownStep.value = 'grade'
  }
}

const closeDropdownOnOutside = (e: MouseEvent) => {
  const target = e.target as Node | null
  // If element was unmounted from DOM during click re-render, do not treat as outside click
  if (!target || !document.body.contains(target)) return

  const containers = document.querySelectorAll('.dropdown-container-el')
  let isInside = false
  containers.forEach(c => {
    if (c.contains(target)) isInside = true
  })
  if (!isInside) {
    showSkillDropdown.value = false
    activeCardDropdownIdx.value = null
  }
}

// Skills, Question Pool and Preview states
type QuestionCard = {
  id: string
  question_id: number
  skill_id: number
  skill_title: string
  level: number
  prompt: string
  type: string
  data: Record<string, unknown>
  correct_answer: Record<string, unknown>
  explanation: string
  showAnswer: boolean
  iframeSrcdoc: string
  iframeSrc: string
  height?: number
  seed: number
}
const skillsList = ref<Record<string, unknown>[]>([])
const skillSearchQuery = ref('')

const searchSkillsList = computed(() => {
  if (!skillSearchQuery.value.trim()) return []
  const query = skillSearchQuery.value.toLowerCase().trim()
  return skillsList.value.filter(s => {
    const title = String(s.title || '').toLowerCase()
    const code = String(s.code || '').toLowerCase()
    return title.includes(query) || code.includes(query)
  })
})
const poolQuestions = ref<Record<string, unknown>[]>([])
const previewDifficulty = ref<number>(1)
const previewCount = ref<number>(1)
const showPreviewAnswer = ref(false)
const previewQuestion = ref<Record<string, unknown> | null>(null)
const previewIframeSrcdoc = ref<string>('')
const previewIframeSrc = ref<string>('')
const previewIframeHeight = ref<number>(500)

const activeQuestionIndex = ref<number | null>(null)
const selectedQuestions = ref<QuestionCard[]>([])
const showGeneratorPanel = ref(true)

const loadingQuestions = ref(false)
const loading = ref(false)

const showStudentSelector = ref(false)
const assignedStudentIds = ref<string[]>([])
const selectAllStudents = ref(false)

const settings = ref({
  question_order: QuizQuestionOrder.FIXED,
  result_visibility: QuizResultVisibility.ALWAYS,
  ended_result_visibility: QuizResultVisibility.ALWAYS,
  end_type: QuizEndType.MANUAL,
  end_date: '',
  end_time: ''
})

const grades = computed(() => catalogStore.grades)
const students = computed(() => teacherStore.students)
const allSkills = computed(() => {
  return catalogStore.skills.length > 0 ? catalogStore.skills : skillsList.value
})

// Extract parent themes (parent_id is null)
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const parentThemes = computed(() => {
  return catalogStore.topics.filter(t => !t.parent_id)
})

// Extract subthemes for the active parent theme
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const childSubthemes = computed(() => {
  if (!selectedTheme.value) return []
  return catalogStore.topics.filter((t) => t.parent_id === (selectedTheme.value as Record<string, unknown>)?.id)
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

const visibilityLevels: Record<QuizResultVisibility, number> = {
  [QuizResultVisibility.ALWAYS]: 3,
  [QuizResultVisibility.SCORE_ONLY]: 2,
  [QuizResultVisibility.HIDDEN]: 1
}

watch(
  () => settings.value.result_visibility,
  (newVal) => {
    const curLevel = visibilityLevels[newVal]
    const endedLevel = visibilityLevels[settings.value.ended_result_visibility]
    if (endedLevel < curLevel) {
      settings.value.ended_result_visibility = newVal
    }
  }
)

watch(
  () => settings.value.ended_result_visibility,
  (newVal) => {
    const curLevel = visibilityLevels[newVal]
    const resultLevel = visibilityLevels[settings.value.result_visibility]
    if (curLevel < resultLevel) {
      settings.value.result_visibility = newVal
    }
  }
)

// Catalog event handlers
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const onGradeChange = async () => {
  selectedTheme.value = null
  selectedSubtheme.value = null
  selectedSkill.value = null
  skillsList.value = []
  poolQuestions.value = []
  previewQuestion.value = null
  await loadSkills()
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const onThemeChange = async () => {
  selectedSubtheme.value = null
  selectedSkill.value = null
  poolQuestions.value = []
  previewQuestion.value = null
  await loadSkills()
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
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
      topic_id: topicId as number | null | undefined,
      page_size: 500
    })
  } catch (err) {
    console.error('Failed to load skills:', err)
  }
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const onSkillChange = async () => {
  if (!selectedSkill.value) return
  loadingQuestions.value = true
  poolQuestions.value = []
  previewQuestion.value = null
  showPreviewAnswer.value = false
  
  try {
    const res = await teacherApi.getSkillQuestions(selectedSkill.value.id as number)
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
    const randIdx = Math.floor(Math.random() * pool.length)
    previewQuestion.value = { ...pool[randIdx], level: previewDifficulty.value }
  } else if (poolQuestions.value.length > 0) {
    // Fallback: take any question from pool and set level to previewDifficulty
    previewQuestion.value = {
      ...poolQuestions.value[0],
      level: previewDifficulty.value
    }
  } else {
    previewQuestion.value = null
  }

  if (previewQuestion.value) {
    loadPreviewPlugin(previewQuestion.value)
  } else {
    previewIframeSrcdoc.value = ''
  }
}

const regeneratePreview = () => {
  selectNextPreviewQuestion()
}

// Helper to check if a question is a plugin/interactive miniapp
const isQuestionPlugin = (q: Record<string, unknown> | null | undefined): boolean => {
  if (!q) return false
  const type = q.type as string | undefined
  return type === 'PLUGIN' || type === 'INTERACTIVE'
}

const getRegularPluginSrc = (q: Record<string, unknown> | null | undefined): string => {
  if (!q || !q.data) return ''
  const data = q.data as Record<string, unknown>
  const id = data.plugin_id as string | undefined
  const ver = data.plugin_version as string | undefined
  const entry = data.entry as string | undefined
  if (!id || !ver || !entry) return ''
  return `/static/modules/${id}/${ver}/${entry}`
}

// Load plugin iframe for a preview question (frozen preview with level)
const loadPreviewPlugin = async (q: Record<string, unknown>) => {
  previewIframeSrc.value = ''
  if (!isQuestionPlugin(q)) return
  const base = getRegularPluginSrc(q)
  if (!base) return
  const level = previewDifficulty.value || 1
  previewIframeSrc.value = `${base}?embed=1&level=${level}&frozen=1`
}

// Load plugin iframe for a card object (frozen preview with seed and level, or review mode)
const loadCardPlugin = async (card: QuestionCard) => {
  card.iframeSrc = ''
  if (!isQuestionPlugin(card)) return
  const base = getRegularPluginSrc(card)
  if (!base) return
  const level = card.level || 1
  if (card.showAnswer) {
    const ca = card.correct_answer ? encodeURIComponent(JSON.stringify(card.correct_answer)) : ''
    const qd = card.data ? encodeURIComponent(JSON.stringify(card.data)) : ''
    card.iframeSrc = `${base}?embed=1&seed=${card.seed}&level=${level}&mode=review&showCorrectAnswer=1&correctAnswer=${ca}&questionData=${qd}`
  } else {
    card.iframeSrc = `${base}?embed=1&seed=${card.seed}&level=${level}&frozen=1`
  }
}

// Add N questions to the list of selected questions
const addGeneratedQuestions = async () => {
  if (!previewQuestion.value) return
  
  const pool = filteredPoolQuestions.value.length > 0 ? filteredPoolQuestions.value : poolQuestions.value
  if (!pool.length) return

  // Select N questions (allowing duplicates if pool size is less than requested count)
  const poolCopy = [...pool]
  let tempPool = [...poolCopy]
  
  const added: QuestionCard[] = []
  for (let i = 0; i < previewCount.value; i++) {
    if (tempPool.length === 0) {
      tempPool = [...poolCopy] // Refill to allow duplicates
    }
    if (tempPool.length === 0) break

    const randIdx = Math.floor(Math.random() * tempPool.length)
    const q = tempPool.splice(randIdx, 1)[0] as Record<string, unknown>
    
    // Generate a unique card ID for Vue :key rendering
    const uniqueCardId = `card-${q.id}-${Date.now()}-${Math.floor(Math.random() * 1000000)}`
    
    // Generate a deterministic seed for this question
    const questionSeed = Math.floor(Math.random() * 2147483647)
    
    // Randomize card level between 1 and 5
    const cardLevel = Math.floor(Math.random() * 5) + 1

    // Add custom properties for cards
    const cardObj: QuestionCard = {
      id: uniqueCardId,
      question_id: q.id as number,
      skill_id: (selectedSkill.value as Record<string, unknown>).id as number,
      skill_title: (selectedSkill.value as Record<string, unknown>).title as string,
      level: cardLevel,
      prompt: q.prompt as string,
      type: q.type as string,
      data: (q.data as Record<string, unknown>) || {},
      correct_answer: (q.correct_answer as Record<string, unknown>) || {},
      explanation: q.explanation as string,
      showAnswer: false,
      iframeSrcdoc: '',
      iframeSrc: '',
      seed: questionSeed
    }
    await loadCardPlugin(cardObj)
    added.push(cardObj)
  }

  // Push all added questions to selected questions list
  added.forEach(q => {
    selectedQuestions.value.push(q)
  })

  // Set active question to the last added one
  if (selectedQuestions.value.length > 0) {
    activeQuestionIndex.value = selectedQuestions.value.length - 1
  }
  
  previewCount.value = 1

  // Collapse the generator panel after adding
  showGeneratorPanel.value = false
  // Reset preview state for next use
  selectedSkill.value = null
  poolQuestions.value = []
  previewQuestion.value = null
  previewIframeSrcdoc.value = ''
  showPreviewAnswer.value = false
  showSkillDropdown.value = false
  dropdownStep.value = 'grade'
}

// Question navigation and actions in cards list
// Opens the generator panel at the bottom (and resets to fresh state)
const openGeneratorPanel = () => {
  showGeneratorPanel.value = true
  selectedSkill.value = null
  poolQuestions.value = []
  previewQuestion.value = null
  previewIframeSrcdoc.value = ''
  showPreviewAnswer.value = false
  dropdownStep.value = 'grade'
  // Scroll to generator panel
  setTimeout(() => {
    document.getElementById('generator-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, 50)
}

const scrollToQuestion = (idx: number) => {
  activeQuestionIndex.value = idx
  document.getElementById(`question-card-${idx}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
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
const changeCardSkill = async (idx: number, skillId: number, skillObjParam?: Record<string, unknown>) => {
  const card = selectedQuestions.value[idx]
  try {
    const res = await teacherApi.getSkillQuestions(skillId)
    const questionsPool = res.data?.data || []
    
    // Choose a question from the new skill matching level
    const levelMatch = questionsPool.filter(q => q.level === selectedQuestions.value[idx].level)
    const newQ = levelMatch[0] || questionsPool[0]
    
    if (newQ) {
      const skillObj = skillObjParam || (allSkills.value.find(s => (s as Record<string, unknown>).id === skillId) as Record<string, unknown> | undefined)
      const randSuffix = Math.floor(Math.random() * 1000000)
      const skillTitleStr = (skillObj?.title as string) || (card?.skill_title as string) || ''
      const cardObj: QuestionCard = {
        ...selectedQuestions.value[idx],
        id: `card-${newQ.id}-${Date.now()}-${randSuffix}`,
        question_id: newQ.id,
        skill_id: skillId,
        skill_title: skillTitleStr,
        prompt: newQ.prompt,
        type: newQ.type,
        data: (newQ.data as Record<string, unknown>) || {},
        correct_answer: (newQ.correct_answer as Record<string, unknown>) || {},
        explanation: newQ.explanation,
        iframeSrcdoc: '',
        iframeSrc: '',
        seed: Math.floor(Math.random() * 2147483647)
      }
      await loadCardPlugin(cardObj)
      selectedQuestions.value[idx] = cardObj
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
    const newQ = levelMatch[0] || questionsPool[0] || card
    
    if (newQ) {
      const randSuffix = Math.floor(Math.random() * 1000000)
      const cardObj: QuestionCard = {
        ...card,
        id: `card-${newQ.id || card.question_id}-${Date.now()}-${randSuffix}`,
        question_id: newQ.id || card.question_id,
        level: level, // Explicitly set to selected level
        prompt: newQ.prompt || card.prompt,
        type: newQ.type || card.type,
        data: (newQ.data as Record<string, unknown>) || card.data || {},
        correct_answer: (newQ.correct_answer as Record<string, unknown>) || card.correct_answer || {},
        explanation: newQ.explanation || card.explanation,
        iframeSrcdoc: '',
        iframeSrc: '',
        seed: Math.floor(Math.random() * 2147483647)
      }
      await loadCardPlugin(cardObj)
      selectedQuestions.value[idx] = cardObj
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
      matches = matches.filter(q => q.id !== card.question_id)
    }
    
    const newQ = matches[Math.floor(Math.random() * matches.length)] || questionsPool[0]
    
    if (newQ) {
      const randSuffix = Math.floor(Math.random() * 1000000)
      const cardObj: QuestionCard = {
        ...card,
        id: `card-${newQ.id}-${Date.now()}-${randSuffix}`,
        question_id: newQ.id,
        prompt: newQ.prompt,
        type: newQ.type,
        data: (newQ.data as Record<string, unknown>) || {},
        correct_answer: (newQ.correct_answer as Record<string, unknown>) || {},
        explanation: newQ.explanation,
        iframeSrcdoc: '',
        iframeSrc: '',
        seed: Math.floor(Math.random() * 2147483647)
      }
      await loadCardPlugin(cardObj)
      selectedQuestions.value[idx] = cardObj
    }
  } catch (err) {
    console.error('Failed to regenerate card question:', err)
  }
}

const toggleCardAnswer = (targetCard: QuestionCard) => {
  const nextState = !targetCard.showAnswer
  
  // Toggle answer visibility for ALL selected questions in the quiz
  selectedQuestions.value.forEach((card) => {
    card.showAnswer = nextState
    if (isQuestionPlugin(card)) {
      loadCardPlugin(card)
    }
  })
}

// Option formatting and correct answer matching
const formatMCQOption = (option: unknown) => {
  if (typeof option === 'object' && option !== null) {
    const o = option as Record<string, unknown>
    return o.text || o.label || o.value || o.id || ''
  }
  return String(option)
}

const isOptionCorrect = (question: Record<string, unknown>, option: unknown, index: number) => {
  const correctAnswer = question.correct_answer as Record<string, unknown> | undefined
  const correctChoice = correctAnswer?.choice
  if (correctChoice) {
    const o = typeof option === 'object' && option !== null ? option as Record<string, unknown> : null
    const optionId = o?.id || o?.label || index
    return String(optionId).toUpperCase() === String(correctChoice).toUpperCase()
  }
  
  const correctVal = correctAnswer?.value
  if (correctVal) {
    const o = typeof option === 'object' && option !== null ? option as Record<string, unknown> : null
    const optionText = o?.text || o?.value || option
    return String(optionText).toUpperCase() === String(correctVal).toUpperCase()
  }
  return false
}

// Step controls
const nextStep = () => {
  currentStep.value = 2
}

const isEditing = computed(() => !!props.initialQuiz)
const draftId = ref<string | null>(null)
const isLoaded = ref(false)
const skipAutoSave = ref(false)
const isPublished = ref(false)

const buildPayload = (isPublishing: boolean) => {
  const nameToSave = quizName.value.trim() || getDefaultQuizName()
  
  let endAtStr: string | null = null
  if (settings.value.end_type === 'SCHEDULED' && settings.value.end_date) {
    const timeStr = settings.value.end_time || '00:00'
    const dt = new Date(`${settings.value.end_date}T${timeStr}`)
    if (!isNaN(dt.getTime())) {
      endAtStr = dt.toISOString()
    }
  }

  const isDraft = !isPublished.value && !isPublishing
  
  return {
    name: nameToSave,
    question_order: settings.value.question_order,
    result_visibility: settings.value.result_visibility,
    ended_result_visibility: settings.value.ended_result_visibility,
    end_type: settings.value.end_type,
    questions: selectedQuestions.value.map((q, i) => ({
      question_id: q.question_id,
      position: i,
      seed: q.seed,
      level: q.level
    })),
    is_draft: isDraft,
    student_ids: !isDraft ? (selectAllStudents.value || assignedStudentIds.value.length === 0 ? null : assignedStudentIds.value) : null,
    classroom_id: null,
    end_at: !isDraft ? endAtStr : null
  }
}

// Generate default quiz name like "Quiz 7/13"
const getDefaultQuizName = () => {
  const d = new Date()
  return `Quiz ${d.getMonth() + 1}/${d.getDate()}`
}

// Auto-save draft silently (no alerts, no UI blocking)
const autoSaveDraft = async () => {
  if (selectedQuestions.value.length === 0) return

  try {
    const payload = buildPayload(false)

    if (isEditing.value || draftId.value) {
      const idToUpdate = draftId.value || (props.initialQuiz as Record<string, unknown>).id as string
      const updated = await quizStore.updateQuiz(idToUpdate, payload)
      if (updated && updated.id) {
        draftId.value = updated.id
      }
    } else {
      const created = await quizStore.createQuiz(payload)
      if (created && created.id) {
        draftId.value = created.id
      }
    }
  } catch (err) {
    console.error('Auto-save draft failed:', err)
  }
}

// Debounce timer for auto-saving
let autoSaveTimeout: ReturnType<typeof setTimeout> | null = null

const triggerAutoSave = () => {
  if (autoSaveTimeout) clearTimeout(autoSaveTimeout)
  autoSaveTimeout = setTimeout(async () => {
    await autoSaveDraft()
  }, 1000) // auto-save after 1 second of inactivity
}

// Watch fields for changes
watch(
  [quizName, () => [...selectedQuestions.value], () => ({ ...settings.value })],
  () => {
    if (!isLoaded.value) return
    triggerAutoSave()
  },
  { deep: true }
)

// When clicking Back, cancel any pending debounced save, trigger instant save, and exit
const handleBack = async () => {
  if (autoSaveTimeout) clearTimeout(autoSaveTimeout)
  if (selectedQuestions.value.length > 0) {
    await autoSaveDraft()
  }
  skipAutoSave.value = true
  emit('created')
}

// Also auto-save on component unmount (e.g. when leaving the tab)
onBeforeUnmount(async () => {
  if (autoSaveTimeout) clearTimeout(autoSaveTimeout)
  if (!skipAutoSave.value && selectedQuestions.value.length > 0) {
    await autoSaveDraft()
  }
})

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

  skipAutoSave.value = true
  loading.value = true
  try {
    const payload = buildPayload(true)

    if (isEditing.value || draftId.value) {
      const idToUpdate = draftId.value || (props.initialQuiz as Record<string, unknown>).id as string
      await quizStore.updateQuiz(idToUpdate, payload)
    } else {
      await quizStore.createQuiz(payload)
    }

    emit('created')
  } catch (err: unknown) {
    const e = err as { response?: { data?: { message?: string } }; message?: string }
    alert(e.response?.data?.message || e.message || 'Error publishing quiz')
  } finally {
    loading.value = false
  }
}

const handleIframeResize = (e: MessageEvent) => {
  try {
    const d = typeof e.data === 'string' ? JSON.parse(e.data) : e.data
    if (!d) return
    if (d.type === 'resize' || d.type === 'RESIZE' || d.type === 'content-height') {
      const height = d.height ?? d.contentHeight ?? d.scrollHeight
      if (typeof height === 'number' && height > 0) {
        const iframes = document.querySelectorAll('iframe')
        iframes.forEach((iframe) => {
          if (iframe.contentWindow === e.source) {
            const cardId = iframe.getAttribute('data-card-id')
            if (cardId) {
              const card = selectedQuestions.value.find(sq => sq.id === cardId)
              if (card) {
                card.height = Math.max(height + 20, 300)
              }
            }
            if (iframe.getAttribute('data-preview-iframe') === 'true') {
              previewIframeHeight.value = Math.max(height + 20, 300)
            }
          }
        })
      }
    }
  } catch { /* ignore */ }
}

onMounted(async () => {
  window.addEventListener('click', closeDropdownOnOutside)
  window.addEventListener('message', handleIframeResize)
  await Promise.all([
    catalogStore.getGrades(),
    catalogStore.getTopics(),
    catalogStore.getSkills({ page_size: 1000 }),
    teacherStore.fetchStudents()
  ])
  
  if (props.initialQuiz) {
    const iq = props.initialQuiz as Record<string, unknown>
    draftId.value = iq.id as string
    quizName.value = iq.name as string
    settings.value.question_order = iq.question_order as QuizQuestionOrder
    settings.value.result_visibility = iq.result_visibility as QuizResultVisibility
    settings.value.ended_result_visibility = (iq.ended_result_visibility || QuizResultVisibility.ALWAYS) as QuizResultVisibility
    settings.value.end_type = iq.end_type as QuizEndType

    // Load assignments / selected students
    if (iq.assignments && (iq.assignments as Record<string, unknown>[]).length > 0) {
      isPublished.value = true
      const assignments = iq.assignments as Record<string, unknown>[]
      const isAll = assignments.some(a => !a.student_id && !a.classroom_id)
      
      if (isAll) {
        selectAllStudents.value = true
        assignedStudentIds.value = students.value.map(s => s.id)
      } else {
        selectAllStudents.value = false
        assignedStudentIds.value = assignments
          .filter(a => a.student_id)
          .map(a => a.student_id as string)
      }

      // Pre-fill end_date and end_time from first assignment's end_at if present
      const firstA = assignments[0]
      if (firstA.end_at) {
        const endAt = new Date(firstA.end_at as string)
        if (!isNaN(endAt.getTime())) {
          const year = endAt.getFullYear()
          const month = String(endAt.getMonth() + 1).padStart(2, '0')
          const day = String(endAt.getDate()).padStart(2, '0')
          settings.value.end_date = `${year}-${month}-${day}`
          
          const hours = String(endAt.getHours()).padStart(2, '0')
          const minutes = String(endAt.getMinutes()).padStart(2, '0')
          settings.value.end_time = `${hours}:${minutes}`
        }
      }
    } else {
      selectAllStudents.value = false
      assignedStudentIds.value = []
    }
    
    // Map initial questions with custom details
    if (iq.questions) {
      const mapped = (iq.questions as Record<string, unknown>[]).map((q) => {
        const question = q.question as Record<string, unknown> | undefined
        const skill = question?.skill as Record<string, unknown> | undefined
        const randSuffix = Math.floor(Math.random() * 1000000)
        return {
          id: `card-${q.question_id}-${randSuffix}`,
          question_id: q.question_id as number,
          skill_id: (question?.skill_id as number) || 0,
          skill_title: (skill?.title as string) || 'Енгізілген дағды',
          level: (q.level as number) || (question?.level as number) || 1,
          prompt: question ? (question.prompt as string) : 'Сұрақ мәтіні жүктелмеді',
          type: (question?.type as string) || 'MCQ',
          data: (question?.data as Record<string, unknown>) || {},
          correct_answer: (question?.correct_answer as Record<string, unknown>) || {},
          explanation: (question?.explanation as string) || '',
          showAnswer: false,
          iframeSrcdoc: '',
          iframeSrc: '',
          seed: (q.seed as number) || Math.floor(Math.random() * 2147483647)
        } as QuestionCard
      })
      for (const card of mapped) {
        await loadCardPlugin(card)
      }
      selectedQuestions.value = mapped
    }
    
    if (selectedQuestions.value.length > 0) {
      activeQuestionIndex.value = 0
    }
  }
  
  isLoaded.value = true
})

onUnmounted(() => {
  window.removeEventListener('click', closeDropdownOnOutside)
  window.removeEventListener('message', handleIframeResize)
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
