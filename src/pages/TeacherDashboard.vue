<template>
  <div class="teacher-dashboard">
    <Header />

    <!-- Sub-navigation tabs -->
    <div class="tabs-bar">
      <div class="tabs-inner">
        <div
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-item-group"
          @mouseenter="hoverTab = tab.key"
          @mouseleave="hoverTab = null"
        >
          <button
            @click="tab.dropdown ? (hoverTab === tab.key ? hoverTab = null : hoverTab = tab.key) : (activeTab = tab.key)"
            class="tab-btn"
            :class="{ active: activeTab === tab.key || (tab.dropdown && tab.dropdown.some(d => d.key === activeTab)) }"
          >
            <component :is="tab.icon" class="tab-icon" />
            {{ tab.label }}
            <svg v-if="tab.dropdown" class="w-4 h-4 ml-1 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
          </button>

          <div v-if="tab.dropdown && hoverTab === tab.key" class="tab-dropdown">
            <button v-for="sub in tab.dropdown" :key="sub.key"
              @click.stop="activeTab = sub.key; hoverTab = null; $nextTick(() => { if(sub.key === 'glance') startGlancePolling(); else stopGlancePolling(); })"
              :class="['dropdown-item', { active: activeTab === sub.key }]">
              {{ sub.label }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <main class="main-content">

      <!-- ===================== ВЗГЛЯНУТЬ ===================== -->
      <template v-if="activeTab === 'glance'">

        <!-- Loading -->
        <div v-if="loadingData" class="loading-state">
          <div class="spinner"></div>
          <p>Жүктелуде...</p>
        </div>

        <template v-else>
          <!-- Welcome -->
          <div class="welcome-row">
            <h1 class="welcome-title">
              Қош келдіңіз, {{ teacherName }}!
            </h1>
            <div class="student-selector">
              <select v-model="selectedStudentId" class="student-select">
                <option value="all">Барлық оқушылар</option>
                <option v-for="s in studentsBreakdown" :key="s.student_id" :value="s.student_id">
                  {{ s.full_name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Big blue stats strip -->
          <div class="blue-strip">
            <div class="blue-strip-inner">
              <span class="blue-strip-label">ОСЫ ЖЫЛЫ БІЗ</span>
              <span class="digit-row">
                <span
                  v-for="(d, i) in questionsDigits"
                  :key="i"
                  class="digit-box"
                >{{ d }}</span>
              </span>
              <span class="blue-strip-label">СҰРАҚҚА ЖАУАП БЕРДІК!</span>
            </div>
          </div>

          <!-- Two-column cards -->
          <div class="dashboard-cards">
            <!-- Skill progress -->
            <div class="card">
              <h2 class="card-title">Дағды прогресі</h2>
              <div class="mountain-area">
                <!-- Mountain SVG -->
                <svg viewBox="0 0 320 200" class="mountain-svg" preserveAspectRatio="xMidYMax meet">
                  <!-- Sky -->
                  <rect x="0" y="0" width="320" height="200" fill="#e8f4f8" rx="0"/>
                  <!-- Clouds -->
                  <ellipse cx="50" cy="40" rx="25" ry="10" fill="white" opacity="0.7"/>
                  <ellipse cx="70" cy="35" rx="20" ry="8" fill="white" opacity="0.6"/>
                  <ellipse cx="260" cy="30" rx="18" ry="7" fill="white" opacity="0.5"/>
                  <ellipse cx="280" cy="35" rx="22" ry="9" fill="white" opacity="0.6"/>
                  <!-- Back mountain -->
                  <polygon points="180,200 230,100 290,200" fill="#b8d4e3"/>
                  <polygon points="200,200 260,80 320,200" fill="#a3c4d6"/>
                  <!-- Main green mountain -->
                  <polygon points="40,200 160,55 280,200" fill="#8ec63f"/>
                  <!-- Mountain shading -->
                  <polygon points="160,55 220,140 280,200 160,200" fill="#7bb336" opacity="0.6"/>
                  <!-- Snow cap -->
                  <polygon points="160,55 145,85 155,80 165,90 180,82" fill="white"/>
                  <!-- Trees -->
                  <polygon points="80,200 95,165 110,200" fill="#5a9a20" opacity="0.7"/>
                  <polygon points="110,200 130,155 150,200" fill="#6aab28" opacity="0.6"/>
                  <polygon points="190,200 205,160 220,200" fill="#5a9a20" opacity="0.7"/>
                  <polygon points="220,200 240,170 260,200" fill="#6aab28" opacity="0.5"/>
                  <!-- Ground -->
                  <rect x="0" y="195" width="320" height="5" fill="#c5e1a5"/>
                </svg>

                <!-- Stats overlaid on left side -->
                <div class="mountain-stats">
                  <div class="stat-row stat-mastered">
                    <span class="stat-number">{{ currentMastered }}</span>
                    <span class="stat-line"></span>
                    <span class="stat-label">МЕҢГЕРІЛГЕН</span>
                  </div>
                  <div class="stat-row stat-proficient">
                    <span class="stat-number">{{ currentProficient }}</span>
                    <span class="stat-line"></span>
                    <span class="stat-label">БІЛІКТІ</span>
                  </div>
                  <div class="stat-row stat-practiced">
                    <span class="stat-number">{{ currentSkillsPracticed }}</span>
                    <span class="stat-line"></span>
                    <span class="stat-label">ЖАТТЫҒУДА</span>
                  </div>
                </div>
              </div>
              <div class="card-footer">
                <a href="#" class="card-footer-link">
                  🎯 Осы аптада {{ currentSkillsPracticedThisWeek }} дағды жаттықтырылды ›
                </a>
              </div>
            </div>

            <!-- Time spent -->
            <div class="card">
              <h2 class="card-title">Жұмсалған уақыт</h2>
              <div class="donut-area">
                <div class="donut-wrapper">
                  <svg viewBox="0 0 120 120" class="donut-svg">
                    <circle cx="60" cy="60" r="48" fill="none" stroke="#e8f0f4" stroke-width="14"/>
                    <circle
                      v-if="currentTotalTime > 0"
                      cx="60" cy="60" r="48"
                      fill="none"
                      stroke="#00bcd4"
                      stroke-width="14"
                      :stroke-dasharray="`${(currentTotalTime / Math.max(currentTotalTime, 1)) * 301.6} 301.6`"
                      stroke-linecap="round"
                      class="donut-arc"
                    />
                  </svg>
                  <div class="donut-center">
                    <span class="donut-value">{{ currentTimeFormatted }}</span>
                    <span class="donut-sub">ОСЫ ЖЫЛ</span>
                  </div>
                </div>
                <div class="donut-legend">
                  <div class="legend-item">
                    <span class="legend-dot" style="background: #0097a7;"></span>
                    МЕКТЕП
                  </div>
                  <div class="legend-item">
                    <span class="legend-dot" style="background: #4dd0e1;"></span>
                    ҮЙ
                  </div>
                </div>
              </div>
              <div class="card-footer">
                <a href="#" class="card-footer-link">
                  ⚡ Қазір StudyPoint-та {{ students.length }} оқушы ›
                </a>
              </div>
            </div>
          </div>

          <!-- Achievement summary footer -->
          <div class="achievement-footer">
            <a href="#" class="achievement-link">
              🏆 Жетістіктер қорытындысы ›
            </a>
          </div>
        </template>
      </template>

      <!-- ===================== ROSTER (ОҚУШЫЛАР ТІЗІМІ) ===================== -->
      <template v-if="activeTab === 'roster'">
        <div class="tools-section">
          <div class="tools-header">
            <div>
              <h1 class="tools-title">Оқушылар тізімі</h1>
              <p class="tools-subtitle">Барлық оқушылардың логині мен құпиясөзі осында</p>
            </div>
            <button @click="showAddModal = true" class="add-btn">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
              Оқушы қосу
            </button>
          </div>

          <div class="table-card">
            <div v-if="loadingStudents" class="table-loading">
              <div class="spinner"></div>
            </div>
            <div v-else-if="studentsError" class="table-error">{{ studentsError }}</div>
            <div v-else-if="students.length === 0" class="table-empty">
              <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              <p class="font-medium text-gray-500">Оқушылар жоқ</p>
              <p class="text-sm text-gray-400 mt-1">«Оқушы қосу» түймесін басыңыз</p>
            </div>
            <div v-else class="overflow-x-auto">
              <table class="roster-table">
                <thead>
                  <tr>
                    <th class="w-10">#</th>
                    <th>Аты-жөні</th>
                    <th>Сыныбы</th>
                    <th>Логин</th>
                    <th>Құпиясөз</th>
                    <th class="w-36">Әрекет</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in students" :key="student.id">
                    <td class="text-gray-400">{{ index + 1 }}</td>
                    <td class="font-medium text-gray-900">{{ student.full_name }}</td>
                    <td class="text-gray-500">{{ student.grade_level ? `${student.grade_level} сынып` : '—' }}</td>
                    <td>
                      <span @click="copyToClipboard(student.username, student.id + '_u')" class="copy-badge copy-badge-blue" :title="'Көшіру'">
                        {{ student.username }}
                        <span v-if="copiedId === student.id + '_u'" class="copy-toast">Көшірілді ✓</span>
                      </span>
                    </td>
                    <td>
                      <span v-if="student.password && student.password !== '—'" @click="copyToClipboard(student.password!, student.id + '_p')" class="copy-badge copy-badge-green" :title="'Көшіру'">
                        {{ student.password }}
                        <span v-if="copiedId === student.id + '_p'" class="copy-toast">Көшірілді ✓</span>
                      </span>
                      <span v-else class="text-xs text-gray-400 italic">Тек жасағанда көрінеді</span>
                    </td>
                    <td>
                      <div class="action-btns">
                        <button @click="resetPassword(student)" :disabled="resettingId === student.id" class="action-link action-link-blue">
                          {{ resettingId === student.id ? 'Жасалуда...' : 'Жаңа пароль' }}
                        </button>
                        <button @click="confirmDelete(student)" :disabled="deletingId === student.id" class="action-link action-link-red">
                          {{ deletingId === student.id ? '...' : 'Өшіру' }}
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div class="table-foot">Барлығы {{ students.length }} оқушы</div>
            </div>
          </div>
          <div v-if="resetError" class="error-msg">{{ resetError }}</div>
        </div>
      </template>

      <!-- ===================== БЕЛСЕНДІЛІК ҚҰРАЛДАРЫ (LIVE CLASSROOM) ===================== -->
      <template v-if="activeTab === 'tools'">
        <div class="live-classroom">
          <div class="live-header">
            <h1 class="live-title">ЖАНДЫ СЫНЫП <span class="live-pulse"></span> <span class="help-circle">?</span></h1>
            <p class="live-subtitle" v-if="livePollingActive">Автоматты жаңару: 1 секунд сайын</p>
          </div>

          <div class="stats-row">
            <div class="stat-box">
              <div class="stat-icon-wrapper green-icon">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ liveData.active_count }}</div>
                <div class="stat-label">ҚАЗІР<br>БЕЛСЕНДІ</div>
              </div>
            </div>
            
            <div class="stat-box">
              <div class="stat-icon-wrapper grey-icon">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ liveData.inactive_count }}</div>
                <div class="stat-label">БЕЛСЕНДІ<br>ЕМЕС</div>
              </div>
            </div>
            
            <div class="stat-box">
              <div class="stat-icon-wrapper orange-icon">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ liveData.needs_help_count }}</div>
                <div class="stat-label">КӨМЕК ҚАЖЕТ<br>ЕТУІ МҮМКІН</div>
              </div>
            </div>
            
            <div class="stat-box">
              <div class="stat-icon-wrapper blue-icon">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ liveData.total_students }}</div>
                <div class="stat-label">ЖАЛПЫ<br>ОҚУШЫ</div>
              </div>
            </div>
          </div>

          <div class="activity-wall-container">
            <div class="activity-wall-header">
              <h2 class="activity-wall-title">Қазір тапсырма орындап жатқан оқушылар</h2>
            </div>

            <!-- No active students -->
            <div v-if="liveData.active_count === 0" class="live-empty-state">
              <div class="live-empty-icon">
                <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
              </div>
              <p class="live-empty-text">Қазір тапсырма орындап жатқан оқушы жоқ</p>
              <p class="live-empty-hint">Оқушы тапсырманы бастағанда, бұл жерде автоматты түрде көрінеді</p>
            </div>

            <!-- Active students grid -->
            <div v-else class="activity-grid">
              <div
                class="student-activity-card"
                :class="{ 'needs-help': isNeedsHelp(student) }"
                v-for="student in liveData.students"
                :key="student.student_id"
              >
                <div class="sac-header">
                  <h3 class="sac-name">
                    <span class="sac-pulse"></span>
                    {{ student.full_name }}
                  </h3>
                  <span v-if="isNeedsHelp(student)" class="needs-help-badge">Көмек қажет</span>
                </div>
                <div class="sac-body">
                  <p class="sac-skill">{{ student.skill_name || 'Белгісіз дағды' }}</p>
                  
                  <div class="sac-detail-row">
                    <div class="sac-detail">
                      <span class="sac-detail-label">Сұрақтар</span>
                      <span class="sac-detail-value">{{ student.questions_answered }}</span>
                    </div>
                    <div class="sac-detail">
                      <span class="sac-detail-label">Дұрыс</span>
                      <span class="sac-detail-value sac-correct">{{ student.correct }}</span>
                    </div>
                    <div class="sac-detail">
                      <span class="sac-detail-label">Қате</span>
                      <span class="sac-detail-value sac-wrong">{{ student.wrong }}</span>
                    </div>
                  </div>
                  
                  <div class="sac-stats">
                    <div class="sac-score-label">SmartScore</div>
                    <div class="sac-score" :class="getScoreClass(student.smartscore)">
                      {{ student.smartscore }}
                    </div>
                  </div>
                  <div class="sac-bar-bg">
                    <div class="sac-bar-fill" :class="getScoreClass(student.smartscore) + '-bg'" :style="{ width: Math.min(student.smartscore, 100) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="inactive-students" v-if="liveData.inactive_count > 0">
              <button class="show-inactive-btn" @click="showInactiveStudents = !showInactiveStudents">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                {{ showInactiveStudents ? 'Белсенді емес оқушыларды жасыру' : `${liveData.inactive_count} белсенді емес оқушыны көрсету` }}
                <svg :class="['w-4 h-4 ml-1 transition-transform', { 'rotate-180': showInactiveStudents }]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
              </button>
            </div>

            <div v-if="showInactiveStudents && liveData.inactive_students.length > 0" class="inactive-list">
              <div class="inactive-student-chip" v-for="student in liveData.inactive_students" :key="student.student_id">
                <span class="inactive-dot"></span>
                {{ student.full_name }}
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ===================== КВИЗДЕР ===================== -->
      <template v-if="activeTab === 'quizzes'">
        <div class="quizzes-section">
            <div class="quizzes-top-action">
              <button @click="router.push({ name: 'teacher-quiz-create' })" class="create-quiz-action-btn">
                Жаңа квиз жасау
              </button>
            </div>

            <!-- Error State -->
            <div v-if="quizzesError" class="error-state-wrapper">
              {{ quizzesError }}
            </div>

            <!-- Content Blocks -->
            <div v-else class="quizzes-blocks-container">
              <!-- 1. Active Quizzes Section -->
              <div class="quiz-block-section">
                <h2 class="block-section-title">Белсенді квиздер</h2>
                <div v-if="activeQuizzes.length === 0" class="quiz-block-empty">
                  Белсенді квиздер жоқ.
                </div>
                <div v-else class="quiz-cards-grid">
                  <div v-for="quiz in activeQuizzes" :key="quiz.id" class="quiz-card-item active-quiz">
                    <div class="card-header">
                      <div class="card-title-group">
                        <h3 class="card-title-text">{{ quiz.name }}</h3>
                      </div>
                      
                      <!-- Options Dropdown -->
                      <div class="relative">
                        <button @click.stop="toggleDropdown(quiz.id)" class="options-trigger-btn">
                          <svg class="w-5 h-5 text-gray-400 hover:text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                          </svg>
                        </button>
                        <div v-if="openDropdownId === quiz.id" class="options-dropdown-menu">
                          <button @click.stop="viewQuiz(quiz); closeDropdown()" class="dropdown-menu-item">Көру</button>
                          <button @click.stop="editQuiz(quiz); closeDropdown()" class="dropdown-menu-item">Өңдеу</button>
                          <button @click.stop="confirmDeleteQuiz(quiz); closeDropdown()" class="dropdown-menu-item text-red-600">Өшіру</button>
                        </div>
                      </div>
                    </div>

                    <div class="card-body">
                      <div class="info-row">
                        <span class="info-icon">▦</span>
                        <span class="info-text">Берілді: {{ formatDateShort(quiz.assignments?.[0]?.created_at || quiz.created_at) }}</span>
                      </div>
                      <div class="info-row">
                        <span class="info-icon">◴</span>
                        <span class="info-text">{{ formatEndTime(quiz.assignments?.[0]?.end_at) }}</span>
                      </div>
                      <div class="info-row">
                        <span class="info-icon">#</span>
                        <span class="info-text">{{ quiz.questions?.length || 0 }} сұрақ</span>
                      </div>
                      <div class="info-row">
                        <span class="info-icon">♙</span>
                        <span class="info-text flex-1">
                          {{ formatAssignedStudents(quiz.assignments) }}
                        </span>
                        <span class="completion-badge-count">
                          ✓ {{ getCompletionStats(quiz).completed }} / {{ getCompletionStats(quiz).total }} оқушы
                        </span>
                      </div>

                      <!-- Progress Bar -->
                      <div class="progress-bar-container">
                        <div class="progress-bar-fill" :style="{ width: getCompletionPercent(quiz) + '%' }"></div>
                      </div>
                    </div>

                    <div class="card-footer">
                      <button @click="endQuiz(quiz)" class="end-quiz-btn">
                        Қазір аяқтау
                        <span class="caret-icon">▼</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 2. Drafts Section -->
              <div class="quiz-block-section">
                <h2 class="block-section-title">Квиз черновиктері</h2>
                <div v-if="draftQuizzes.length === 0" class="quiz-block-empty">
                  Сақталған черновиктер жоқ.
                </div>
                <div v-else class="quiz-cards-grid">
                  <div v-for="quiz in draftQuizzes" :key="quiz.id" class="quiz-card-item draft-quiz">
                    <div class="card-header">
                      <h3 class="card-title-text">{{ quiz.name }}</h3>
                      
                      <!-- Options Dropdown -->
                      <div class="relative">
                        <button @click.stop="toggleDropdown(quiz.id)" class="options-trigger-btn">
                          <svg class="w-5 h-5 text-gray-400 hover:text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                          </svg>
                        </button>
                        <div v-if="openDropdownId === quiz.id" class="options-dropdown-menu">
                          <button @click.stop="viewQuiz(quiz); closeDropdown()" class="dropdown-menu-item">Көру</button>
                          <button @click.stop="editQuiz(quiz); closeDropdown()" class="dropdown-menu-item">Өңдеу</button>
                          <button @click.stop="confirmDeleteQuiz(quiz); closeDropdown()" class="dropdown-menu-item text-red-600">Өшіру</button>
                        </div>
                      </div>
                    </div>

                    <div class="card-body">
                      <div class="info-row">
                        <span class="info-icon">#</span>
                        <span class="info-text">{{ quiz.questions.length }} сұрақ қосылды</span>
                      </div>
                      <div class="info-row">
                        <span class="info-icon">♙</span>
                        <span class="info-text">
                          {{ formatAssignedStudents(quiz.assignments) }}
                        </span>
                      </div>
                    </div>

                    <div class="card-footer">
                      <button @click="editQuiz(quiz)" class="keep-adding-btn">
                        Жалғастыру
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 3. Past Quizzes Section -->
              <div class="quiz-block-section">
                <h2 class="block-section-title">Аяқталған квиздер</h2>
                <div v-if="pastQuizzes.length === 0" class="quiz-block-empty">
                  Аяқталған квиздер жоқ.
                </div>
                <div v-else class="past-quizzes-table-card">
                  <table class="past-quizzes-table">
                    <thead>
                      <tr>
                        <th>Атауы</th>
                        <th>Кімге берілді</th>
                        <th>Сұрақтар саны</th>
                        <th>Күндері</th>
                        <th>Орташа ұпай</th>
                        <th class="no-sort"></th>
                        <th class="no-sort w-10"></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="quiz in pastQuizzes" :key="quiz.id">
                        <td class="quiz-name-cell">
                          <button @click="viewQuizReport(quiz)" class="hover:underline text-[#159be8] text-left font-semibold cursor-pointer">
                            {{ quiz.name }}
                          </button>
                        </td>
                        <td>{{ formatAssignedStudents(quiz.assignments) }}</td>
                        <td>{{ quiz.questions?.length || 0 }} сұрақ</td>
                        <td>{{ getPeriodDates(quiz) }}</td>
                        <td class="average-score-cell">{{ getAverageScoreText(quiz) }}</td>
                        <td class="report-action-cell">
                          <button @click="viewQuizReport(quiz)" class="view-report-link-btn">
                            <span class="graph-icon">▥</span>
                            Есепті көру
                          </button>
                        </td>
                        <td>
                          <!-- Options Dropdown for Past Quiz -->
                          <div class="relative">
                            <button @click.stop="toggleDropdown(quiz.id)" class="options-trigger-btn">
                              <svg class="w-4 h-4 text-gray-400 hover:text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                              </svg>
                            </button>
                            <div v-if="openDropdownId === quiz.id" class="options-dropdown-menu">
                              <button @click.stop="viewQuiz(quiz); closeDropdown()" class="dropdown-menu-item">Көру</button>
                              <button @click.stop="confirmDeleteQuiz(quiz); closeDropdown()" class="dropdown-menu-item text-red-600">Өшіру</button>
                            </div>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
        </div>
      </template>

    </main>
    <Footer />

    <!-- Add Student Modal -->
    <Modal :is-open="showAddModal" title="Жаңа оқушы қосу" :show-close="true" @close="showAddModal = false">
      <template #content>
        <form @submit.prevent="submitAddStudent" class="space-y-4">
          <div v-if="createError" class="text-sm text-red-600 bg-red-50 p-2 rounded">{{ createError }}</div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Аты</label>
            <input v-model="form.firstName" type="text" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm border px-3 py-2">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Тегі</label>
            <input v-model="form.lastName" type="text" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm border px-3 py-2">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Сыныбы</label>
            <select v-model="form.gradeId" required class="mt-1 block bg-white w-full rounded-md border-gray-300 shadow-sm focus:border-cyan-500 focus:ring-cyan-500 sm:text-sm border px-3 py-2">
              <option value="" disabled>Таңдаңыз</option>
              <option v-for="grade in grades" :key="grade.number" :value="grade.number">{{ grade.title || `${grade.number} сынып` }}</option>
            </select>
          </div>
        </form>
      </template>
      <template #actions>
        <button @click="submitAddStudent" :disabled="creating" class="add-btn">
          <svg v-if="creating" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
          Қосу
        </button>
        <button @click="showAddModal = false" :disabled="creating" class="cancel-btn">Болдырмау</button>
      </template>
    </Modal>

    <!-- View Quiz Modal -->
    <Modal :is-open="showViewQuizModal" title="Квиз туралы мәлімет" :show-close="true" @close="showViewQuizModal = false">
      <template #content>
        <div v-if="selectedViewQuiz" class="space-y-4">
          <div>
            <h3 class="text-lg font-medium text-gray-900">{{ selectedViewQuiz.name }}</h3>
            <p class="text-sm text-gray-500">Сұрақтар: {{ selectedViewQuiz.questions.length }}</p>
          </div>
          <div class="bg-gray-50 p-4 rounded-md">
            <h4 class="text-sm font-medium text-gray-700 mb-2">Параметрлері:</h4>
            <ul class="text-sm text-gray-600 space-y-1">
              <li>Сұрақтар реті: {{ selectedViewQuiz.question_order === 'FIXED' ? 'Берілген ретпен' : 'Кездейсоқ' }}</li>
              <li>Квизді аяқтау: {{ selectedViewQuiz.end_type === 'MANUAL' ? 'Қолмен аяқтау' : 'Белгіленген уақытта' }}</li>
              <li>Нәтижелерді көрсету: {{ selectedViewQuiz.result_visibility === 'ALWAYS' ? 'Ұпайлар мен дұрыс жауаптарды көрсету' : (selectedViewQuiz.result_visibility === 'SCORE_ONLY' ? 'Тек ұпайларды көрсету' : 'Жасыру') }}</li>
            </ul>
          </div>
          <div v-if="selectedViewQuiz.questions && selectedViewQuiz.questions.length > 0" class="mt-4">
            <h4 class="text-sm font-medium text-gray-700 mb-3">Тапсырмалар:</h4>
            <div class="space-y-3 max-h-64 overflow-y-auto pr-2">
              <div v-for="(q, index) in selectedViewQuiz.questions" :key="q.id" class="p-3 border rounded-md bg-white text-sm">
                <span class="font-medium text-gray-500 mr-2">{{ Number(index) + 1 }}.</span>
                <span v-if="q.question" v-html="q.question.prompt" class="text-gray-800"></span>
                <span v-else class="text-gray-400 italic">Сұрақ мәтіні жүктелмеді</span>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <button @click="showViewQuizModal = false" class="cancel-btn w-full">Жабу</button>
      </template>
    </Modal>

    <!-- Success Modal -->
    <Modal :is-open="showSuccessModal" title="Оқушы сәтті құрылды!" :show-close="false">
      <template #content>
        <div class="space-y-3">
          <p class="text-sm text-gray-600">Бұл мәліметтерді оқушыға беріңіз.</p>
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 font-mono text-sm space-y-2">
            <div class="flex justify-between"><span class="text-gray-500">Аты-жөні:</span><span class="font-bold text-gray-900">{{ createdStudentData?.full_name }}</span></div>
            <div class="flex justify-between border-t border-gray-200 pt-2"><span class="text-gray-500">Логин:</span><span class="font-bold text-cyan-600 select-all">{{ createdStudentData?.username }}</span></div>
            <div class="flex justify-between border-t border-gray-200 pt-2"><span class="text-gray-500">Құпиясөз:</span><span class="font-bold text-green-600 select-all">{{ createdStudentData?.password }}</span></div>
          </div>
        </div>
      </template>
      <template #actions>
        <button @click="closeSuccessModal" class="add-btn">Жабып, жалғастыру</button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import type { QuizResponse, QuizAssignmentResponse } from '@/api/quiz'
import { h } from 'vue'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import Modal from '@/components/ui/Modal.vue'
import { useTeacherStore } from '@/stores/teacher'
import { teacherApi } from '@/api/teacher'
import type { StudentInfo } from '@/api/teacher'
import { useCatalogStore } from '@/stores/catalog'
import { useAuthStore } from '@/stores/auth'
import { useQuizStore } from '@/stores/quiz'

defineOptions({ name: 'TeacherDashboard' })

// Icon components (inline SVGs as render functions)
const EyeIcon = { render: () => h('svg', { class: 'tab-icon', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z' }),
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z' }),
])}
const BoltIcon = { render: () => h('svg', { class: 'tab-icon', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 10V3L4 14h7v7l9-11h-7z' }),
])}
const QuizIcon = { render: () => h('svg', { class: 'tab-icon', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' }),
])}

const tabs = ref([
  {
    key: 'glance_group',
    label: 'Қысқаша шолу',
    icon: EyeIcon,
    dropdown: [
      { key: 'glance', label: 'Жалпы көрініс' },
      { key: 'roster', label: 'Оқушылар тізімі' }
    ]
  },
  { key: 'tools', label: 'Белсенділік құралдары', icon: BoltIcon },
  { key: 'quizzes', label: 'Квиздер', icon: QuizIcon },
])

const activeTab = ref('glance')
const hoverTab = ref<string | null>(null)
const route = useRoute()

// Read tab from URL query (?tab=quizzes)
if (route.query.tab && typeof route.query.tab === 'string') {
  activeTab.value = route.query.tab
}

// Watch for route query changes
watch(() => route.query.tab, (newTab) => {
  if (newTab && typeof newTab === 'string') {
    activeTab.value = newTab
  }
})

const teacherStore = useTeacherStore()
const catalogStore = useCatalogStore()
const authStore = useAuthStore()
const quizStore = useQuizStore()

const { students, loading: loadingStudents, error: studentsError } = storeToRefs(teacherStore)
const { grades } = storeToRefs(catalogStore)
const { quizzes, error: quizzesError } = storeToRefs(quizStore)


// Dashboard analytics data
const loadingData = ref(true)
const selectedStudentId = ref('all')

interface StudentBreakdown {
  student_id: string
  full_name: string
  total_questions: number
  total_time_sec: number
  mastered_count: number
  proficient_count: number
  practicing_count: number
  skills: Array<Record<string, unknown>>
}

const overviewData = ref<{
  total_time_sec: number
  skills_practiced: number
  avg_accuracy_percent: number
  total_questions_answered: number
}>({ total_time_sec: 0, skills_practiced: 0, avg_accuracy_percent: 0, total_questions_answered: 0 })

const showViewQuizModal = ref(false)
const selectedViewQuiz = ref<QuizResponse | null>(null)

const viewQuiz = (quiz: QuizResponse) => {
  selectedViewQuiz.value = quiz
  showViewQuizModal.value = true
}

const editQuiz = (quiz: QuizResponse) => {
  router.push({ name: 'teacher-quiz-edit', params: { quizId: quiz.id } })
}


const router = useRouter()

// Filter and search variables for quizzes
const searchQuery = ref('')
const filterStudent = ref('any')
const openDropdownId = ref<string | null>(null)

const toggleDropdown = (id: string) => {
  if (openDropdownId.value === id) {
    openDropdownId.value = null
  } else {
    openDropdownId.value = id
  }
}

// Close options dropdown
const closeDropdown = () => {
  openDropdownId.value = null
}

const filteredQuizzes = computed(() => {
  let list = quizzes.value || []
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(item => item.name.toLowerCase().includes(q))
  }
  if (filterStudent.value !== 'any') {
    list = list.filter(quiz => 
      (quiz.assignments || []).some(a => a.student_id === filterStudent.value || (!a.student_id && !a.classroom_id))
    )
  }
  return list
})

const activeQuizzes = computed(() => {
  return filteredQuizzes.value.filter(quiz => {
    const assignments = quiz.assignments || []
    if (assignments.length === 0) return false
    return assignments.some(a => !a.end_at || new Date(a.end_at) > new Date())
  })
})

const draftQuizzes = computed(() => {
  return filteredQuizzes.value.filter(quiz => (quiz.assignments || []).length === 0)
})

const pastQuizzes = computed(() => {
  return filteredQuizzes.value.filter(quiz => {
    const assignments = quiz.assignments || []
    if (assignments.length === 0) return false
    return assignments.every(a => a.end_at && new Date(a.end_at) <= new Date())
  })
})

const getCompletionStats = (quiz: QuizResponse) => {
  const assignments = quiz.assignments || []
  const total = assignments.length
  const completed = assignments.filter(a => !!a.completed_at).length
  return { completed, total }
}

const getCompletionPercent = (quiz: QuizResponse) => {
  const { completed, total } = getCompletionStats(quiz)
  if (total === 0) return 0
  return Math.round((completed / total) * 100)
}

const getAverageScoreText = (quiz: QuizResponse) => {
  const { completed, total } = getCompletionStats(quiz)
  if (completed === 0) return '0%'
  const completedAssignments = (quiz.assignments || []).filter(a => !!a.completed_at)
  if (completedAssignments.length === 0) return '0%'
  const sumScore = completedAssignments.reduce((acc, curr) => acc + (curr.score || 0), 0)
  const average = Math.round(sumScore / completedAssignments.length)
  return `${average}% (${completed}/${total} оқушы)`
}

const KAZAKH_MONTHS = [
  'қаңтар', 'ақпан', 'наурыз', 'сәуір', 'мамыр', 'маусым',
  'шілде', 'тамыз', 'қыркүйек', 'қазан', 'қараша', 'желтоқсан'
]

const formatDateShort = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return ''
  const day = date.getDate()
  const month = KAZAKH_MONTHS[date.getMonth()]
  return `${day} ${month}`
}

const formatEndTime = (dateStr?: string | null) => {
  if (!dateStr) return 'Аяқталу уақыты жоқ'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return 'Аяқталу уақыты жоқ'
  const day = date.getDate()
  const month = KAZAKH_MONTHS[date.getMonth()]
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${day} ${month}, ${hours}:${minutes}`
}

const formatAssignedStudents = (assignments?: QuizAssignmentResponse[]) => {
  if (!assignments || assignments.length === 0) return 'Оқушылар таңдалмаған'
  if (students.value.length > 0 && assignments.length === students.value.length) {
    return 'Барлық оқушылар'
  }
  if (assignments.length === 1) {
    const studentId = assignments[0].student_id
    const student = students.value.find(s => s.id === studentId)
    return student ? student.full_name : '1 оқушы'
  }
  return `${assignments.length} оқушы`
}

const getPeriodDates = (quiz: QuizResponse) => {
  const assignments = quiz.assignments || []
  if (!assignments.length) return ''
  const first = assignments[0]
  const start = formatDateShort(first.created_at)
  const end = first.end_at ? formatDateShort(first.end_at) : 'Қазіргі уақыт'
  const date = new Date(first.end_at || first.created_at)
  const year = Number.isNaN(date.getTime()) ? new Date().getFullYear() : date.getFullYear()
  return `${start} - ${end}, ${year}`
}

const endQuiz = async (quiz: QuizResponse) => {
  const assignments = quiz.assignments || []
  const activeAssignments = assignments.filter((a: QuizAssignmentResponse) => !a.end_at || new Date(a.end_at) > new Date())
  if (activeAssignments.length === 0) return
  if (confirm(`"${quiz.name}" квизін қазір аяқтауды растайсыз ба?`)) {
    try {
      await Promise.all(
        activeAssignments.map(a => quizStore.endQuizAssignment(a.id))
      )
      alert('Квиз сәтті аяқталды!')
    } catch (err) {
      console.error(err)
      alert('Квизді аяқтау мүмкін болмады.')
    }
  }
}

const viewQuizReport = (quiz: QuizResponse) => {
  router.push({ name: 'analytics', query: { tab: 'quizzes', quizId: quiz.id } })
}

const confirmDeleteQuiz = async (quiz: QuizResponse) => {
  if (confirm(`"${quiz.name}" квизін өшіруді растайсыз ба?`)) {
    try {
      await quizStore.deleteQuiz(quiz.id);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } }; message?: string }
      alert('Квизді өшіру мүмкін болмады: ' + (err.response?.data?.message || err.message));
    }
  }
}

const studentsBreakdown = ref<StudentBreakdown[]>([])

const teacherName = computed(() => {
  return authStore.user?.full_name || 'Teacher'
})

// Selected student or "all" computed data
const currentTotalQuestions = computed(() => {
  if (selectedStudentId.value === 'all') return overviewData.value.total_questions_answered
  const s = studentsBreakdown.value.find(x => x.student_id === selectedStudentId.value)
  return s?.total_questions || 0
})

const questionsDigits = computed(() => {
  const n = currentTotalQuestions.value
  if (n === 0) return ['0']
  return n.toString().split('')
})

const currentTotalTime = computed(() => {
  if (selectedStudentId.value === 'all') return overviewData.value.total_time_sec
  const s = studentsBreakdown.value.find(x => x.student_id === selectedStudentId.value)
  return s?.total_time_sec || 0
})

const currentTimeFormatted = computed(() => {
  const sec = currentTotalTime.value
  if (sec < 60) return `${sec} сек`
  const min = Math.round(sec / 60)
  if (min < 60) return `${min} мин`
  const hrs = Math.floor(min / 60)
  const remMin = min % 60
  return `${hrs} сағ ${remMin} мин`
})

// Helper: filter skills from a student's skills array
const countSkills = (skills: Array<Record<string, unknown>>, filter: (sk: Record<string, unknown>) => boolean): number => {
  return (skills || []).filter(filter).length
}

const getScoreClass = (score: number) => {
  if (score >= 90) return 'score-gold'
  if (score >= 80) return 'score-green'
  if (score >= 70) return 'score-orange'
  return 'score-blue'
}

const currentMastered = computed(() => {
  const filter = (sk: Record<string, unknown>) => (Number(sk.best_smartscore) || 0) >= 100
  if (selectedStudentId.value === 'all') {
    return studentsBreakdown.value.reduce((sum, s) => sum + countSkills(s.skills, filter), 0)
  }
  const s = studentsBreakdown.value.find(x => x.student_id === selectedStudentId.value)
  return s ? countSkills(s.skills, filter) : 0
})

const currentProficient = computed(() => {
  const filter = (sk: Record<string, unknown>) => {
    const score = Number(sk.best_smartscore) || 0
    return score >= 80 && score < 100
  }
  if (selectedStudentId.value === 'all') {
    return studentsBreakdown.value.reduce((sum, s) => sum + countSkills(s.skills, filter), 0)
  }
  const s = studentsBreakdown.value.find(x => x.student_id === selectedStudentId.value)
  return s ? countSkills(s.skills, filter) : 0
})

const currentSkillsPracticed = computed(() => {
  const filter = (sk: Record<string, unknown>) => {
    const score = Number(sk.best_smartscore) || 0
    const questions = Number(sk.total_questions) || 0
    return questions > 0 && score < 80
  }
  if (selectedStudentId.value === 'all') {
    return studentsBreakdown.value.reduce((sum, s) => sum + countSkills(s.skills, filter), 0)
  }
  const s = studentsBreakdown.value.find(x => x.student_id === selectedStudentId.value)
  return s ? countSkills(s.skills, filter) : 0
})

const currentSkillsPracticedThisWeek = ref(0) // We don't track weekly yet

// Roster functionality
const showAddModal = ref(false)
const showSuccessModal = ref(false)
const creating = ref(false)
const createError = ref('')
const resettingId = ref<string | null>(null)
const resetError = ref('')
const deletingId = ref<string | null>(null)
const copiedId = ref<string | null>(null)

const copyToClipboard = (text: string, id: string) => {
  navigator.clipboard.writeText(text).then(() => {
    copiedId.value = id
    setTimeout(() => { if (copiedId.value === id) copiedId.value = null }, 1500)
  })
}

const form = ref({ firstName: '', lastName: '', gradeId: '' as string | number })
const createdStudentData = ref<{ full_name: string; username: string; password: string } | null>(null)

const fetchAnalyticsData = async (showLoading = false) => {
  if (showLoading) loadingData.value = true
  try {
    const [quickviewResp] = await Promise.all([
      teacherApi.getTeacherQuickviewAnalytics(false),
      grades.value.length === 0 ? catalogStore.getGrades() : Promise.resolve(),
      showLoading ? teacherStore.fetchStudents() : Promise.resolve()
    ])
    const qd = quickviewResp.data?.data as Record<string, unknown> | undefined
    if (qd) {
      const ov = qd.overview as Record<string, unknown> | undefined
      if (ov) {
        overviewData.value = {
          total_time_sec: (ov.total_time_sec as number) || 0,
          skills_practiced: (ov.skills_practiced as number) || 0,
          avg_accuracy_percent: (ov.avg_accuracy_percent as number) || 0,
          total_questions_answered: (ov.total_questions_answered as number) || 0,
        }
      }
      if (Array.isArray(qd.students_breakdown)) {
        studentsBreakdown.value = qd.students_breakdown as StudentBreakdown[]
      }
    }
  } catch (err) {
    console.error('Failed to load teacher dashboard data:', err)
  } finally {
    if (showLoading) loadingData.value = false
  }
}

let glancePollingTimer: ReturnType<typeof setInterval> | null = null

const startGlancePolling = () => {
  if (glancePollingTimer) return
  glancePollingTimer = setInterval(() => fetchAnalyticsData(false), 2000)
}

const stopGlancePolling = () => {
  if (glancePollingTimer) {
    clearInterval(glancePollingTimer)
    glancePollingTimer = null
  }
}

onMounted(async () => {
  await fetchAnalyticsData(true)
})

// ============ LIVE CLASSROOM DATA ============
interface LiveStudent {
  student_id: string
  full_name: string
  skill_name: string
  smartscore: number
  correct: number
  wrong: number
  questions_answered: number
  last_active_seconds_ago: number
}

interface LiveData {
  active_count: number
  inactive_count: number
  needs_help_count: number
  total_students: number
  inactive_students: Array<{
    student_id: string
    full_name: string
  }>
  students: LiveStudent[]
}

const liveData = ref<LiveData>({
  active_count: 0,
  inactive_count: 0,
  needs_help_count: 0,
  total_students: 0,
  inactive_students: [],
  students: [],
})

const livePollingActive = ref(false)
const showInactiveStudents = ref(false)
let livePollingTimer: ReturnType<typeof setInterval> | null = null

const fetchLiveStudents = async () => {
  try {
    const resp = await teacherApi.getLiveStudents()
    const d = resp.data?.data
    if (d) {
      liveData.value = d as LiveData
    }
  } catch (err) {
    console.error('Failed to fetch live students:', err)
  }
}

const startLivePolling = () => {
  if (livePollingTimer) return
  livePollingActive.value = true
  fetchLiveStudents() // initial fetch
  livePollingTimer = setInterval(fetchLiveStudents, 1000)
}

const stopLivePolling = () => {
  livePollingActive.value = false
  if (livePollingTimer) {
    clearInterval(livePollingTimer)
    livePollingTimer = null
  }
}

// Start/stop polling when tools tab is active
watch(activeTab, (tab) => {

  if (tab === 'tools') {
    startLivePolling()
    stopGlancePolling()
  } else if (tab === 'glance') {
    startGlancePolling()
    stopLivePolling()
  } else if (tab === 'quizzes') {
    quizStore.fetchQuizzes()
    stopLivePolling()
    stopGlancePolling()
  } else {
    stopLivePolling()
    stopGlancePolling()
  }
}, { immediate: true })

onUnmounted(() => {
  stopLivePolling()
  stopGlancePolling()
})

const isNeedsHelp = (student: LiveStudent) => {
  return student.smartscore < 30 && student.wrong > 3
}

const submitAddStudent = async () => {
  if (!form.value.firstName || !form.value.lastName || form.value.gradeId === '') {
    createError.value = 'Барлық өрістерді толтырыңыз.'
    return
  }
  createError.value = ''
  creating.value = true
  try {
    const res = await teacherStore.createStudent({ first_name: form.value.firstName, last_name: form.value.lastName, grade_id: Number(form.value.gradeId) })
    createdStudentData.value = res
    showAddModal.value = false
    showSuccessModal.value = true
    form.value = { firstName: '', lastName: '', gradeId: '' }
  } catch (err: unknown) {
    const error = err as { response?: { data?: { message?: string } }; message?: string }
    createError.value = error.response?.data?.message || error.message || 'Қате шықты'
  } finally {
    creating.value = false
  }
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
  createdStudentData.value = null
  teacherStore.fetchStudents()
}

const resetPassword = async (student: StudentInfo) => {
  resettingId.value = student.id
  resetError.value = ''
  try {
    const resp = await teacherApi.resetStudentPassword(student.id)
    const newPass = resp.data.data.password
    const found = students.value.find(s => s.id === student.id)
    if (found) (found as StudentInfo & { password?: string }).password = newPass
  } catch (err: unknown) {
    const e = err as { response?: { data?: { message?: string } }; message?: string }
    resetError.value = e.response?.data?.message || e.message || 'Қате шықты'
  } finally {
    resettingId.value = null
  }
}

const confirmDelete = async (student: StudentInfo) => {
  if (!window.confirm(`"${student.full_name}" оқушысын өшіруді растайсыз ба?`)) return
  deletingId.value = student.id
  resetError.value = ''
  try {
    await teacherApi.deleteStudent(student.id)
    teacherStore.students = students.value.filter(s => s.id !== student.id)
  } catch (err: unknown) {
    const e = err as { response?: { data?: { message?: string } }; message?: string }
    resetError.value = e.response?.data?.message || e.message || 'Жою кезінде қате шықты'
  } finally {
    deletingId.value = null
  }
}
</script>

<style scoped>
/* ============ BASE ============ */
.teacher-dashboard {
  min-height: 100vh;
  background: #e8f4f8;
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
}

/* ============ TABS BAR ============ */
.tabs-bar {
  background: linear-gradient(135deg, #00BCD4 0%, #00ACC1 100%);
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  width: 100%;
}
.tabs-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 0;
  padding: 0;
  overflow: visible; /* Fix: allow dropdowns to be visible outside the bar */
}
.tabs-inner::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}
.tab-item-group {
  position: relative;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  height: 100%;
}
.tab-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}
.tab-btn.active {
  color: white;
  background: rgba(255, 255, 255, 0.15);
  border-bottom-color: white;
  font-weight: 600;
}
.tab-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.tab-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  min-width: 220px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  border-radius: 0 0 8px 8px;
  z-index: 50;
  overflow: hidden;
  padding: 8px 0;
}

.dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 12px 24px;
  border: none;
  background: white;
  color: #4a5568;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: #f7fafc;
  color: #00BCD4;
}

.dropdown-item.active {
  background-color: #e6fffa;
  color: #00BCD4;
  font-weight: 600;
  border-left: 3px solid #00BCD4;
  padding-left: 21px;
}

/* ============ MAIN ============ */
.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 16px;
}

/* ============ WELCOME ============ */
.welcome-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.welcome-title {
  font-size: 30px;
  font-weight: 300;
  color: #3f454a;
  line-height: 1.2;
}
.student-selector {
  position: relative;
}
.student-select {
  appearance: none;
  background: #e8edef;
  border: none;
  border-radius: 20px;
  padding: 6px 32px 6px 16px;
  font-size: 14px;
  font-weight: 500;
  color: #3f454a;
  cursor: pointer;
  outline: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236b7c85' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3e%3cpath d='M6 9l6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  transition: background-color 0.2s;
}
.student-select:hover {
  background-color: #dce3e7;
}

/* ============ INFO BANNER ============ */
.info-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(90deg, #eef9fb 0%, #f0faf4 100%);
  border: 1px solid #d2eef3;
  border-radius: 12px;
  padding: 14px 20px;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
}
.info-banner-icon {
  font-size: 28px;
  flex-shrink: 0;
}
.info-banner p {
  font-size: 14px;
  color: #3f454a;
  margin: 0;
  flex: 1;
}
.info-link {
  color: #00838f;
  font-weight: 600;
  text-decoration: none;
}
.info-link:hover {
  text-decoration: underline;
}
.info-banner-star {
  font-size: 32px;
  flex-shrink: 0;
  opacity: 0.7;
}

/* ============ BLUE STRIP ============ */
.blue-strip {
  background: linear-gradient(135deg, #00acc1 0%, #00838f 100%);
  border-radius: 14px 14px 0 0;
  padding: 28px 20px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 131, 143, 0.3);
}
.blue-strip-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}
@media (max-width: 640px) {
  .blue-strip { padding: 20px 10px; }
  .blue-strip-inner { gap: 8px; }
  .blue-strip-label { font-size: 11px; letter-spacing: 1px; }
}
.blue-strip-label {
  color: rgba(255,255,255,0.95);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
}
.digit-row {
  display: flex;
  gap: 4px;
}
.digit-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 52px;
  background: rgba(255,255,255,0.18);
  border: 2px solid rgba(255,255,255,0.35);
  border-radius: 8px;
  color: white;
  font-size: 32px;
  font-weight: 800;
  text-shadow: 0 2px 4px rgba(0,0,0,0.15);
}
@media (max-width: 640px) {
  .digit-box {
    width: 32px;
    height: 40px;
    font-size: 24px;
  }
}

/* ============ DASHBOARD CARDS ============ */
.dashboard-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: white;
  border-radius: 0 0 14px 14px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  overflow: hidden;
  border: 1px solid #e0e8ec;
  border-top: none;
}
@media (max-width: 768px) {
  .dashboard-cards { grid-template-columns: 1fr; }
}
.card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 24px 0;
}
.card:first-child {
  border-right: 1px solid #e8eff2;
}
@media (max-width: 768px) {
  .card:first-child {
    border-right: none;
    border-bottom: 1px solid #e8eff2;
  }
}
.card-title {
  font-size: 20px;
  font-weight: 400;
  color: #5a6a72;
  margin-bottom: 24px;
  text-align: center;
}

/* Mountain area */
.mountain-area {
  width: 100%;
  position: relative;
  margin-bottom: 12px;
}
.mountain-svg {
  width: 100%;
  height: auto;
  border-radius: 8px;
}
.mountain-stats {
  position: absolute;
  left: 10px;
  top: 15%;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
@media (max-width: 480px) {
  .mountain-stats { gap: 8px; top: 10%; }
  .stat-number { font-size: 20px; }
  .stat-line { width: 20px; }
  .stat-label { font-size: 8px; }
}
.stat-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.stat-number {
  font-size: 28px;
  font-weight: 800;
  color: #3f454a;
  min-width: 28px;
  text-align: right;
  text-shadow: 0 1px 2px rgba(255,255,255,0.8);
}
.stat-line {
  width: 32px;
  height: 2px;
  background: #8aa0ab;
}
.stat-label {
  font-size: 9px;
  font-weight: 700;
  color: #6b7c85;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

/* Donut area */
.donut-area {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  margin-bottom: 24px;
  width: 100%;
  min-height: 180px;
}
@media (max-width: 480px) {
  .donut-area { flex-direction: column; gap: 16px; min-height: auto; }
}
.donut-wrapper {
  position: relative;
  width: 160px;
  height: 160px;
}
.donut-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}
.donut-arc {
  transition: stroke-dasharray 1s ease-out;
}
.donut-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.donut-value {
  font-size: 28px;
  font-weight: 300;
  color: #3f454a;
}
.donut-sub {
  font-size: 10px;
  font-weight: 600;
  color: #8aa0ab;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-top: 2px;
}
.donut-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #6b7c85;
  letter-spacing: 1px;
  text-transform: uppercase;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Card footers */
.card-footer {
  width: 100%;
  border-top: 1px solid #e8eff2;
  padding: 14px 0;
  text-align: center;
  margin-top: auto;
}
.card-footer-link {
  color: #00838f;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}
.card-footer-link:hover {
  text-decoration: underline;
  color: #006064;
}

/* Achievement footer */
.achievement-footer {
  background: #f0f8fa;
  border: 1px solid #d2eef3;
  border-top: none;
  border-radius: 0 0 14px 14px;
  padding: 14px;
  text-align: center;
}
.achievement-link {
  color: #00838f;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
}
.achievement-link:hover {
  text-decoration: underline;
}

/* ============ LOADING ============ */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #6b7c85;
}
.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e0e8ec;
  border-top-color: #00acc1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============ TOOLS TAB ============ */
.tools-section {
  animation: fadeIn 0.3s ease;
}
.tools-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.tools-title {
  font-size: 24px;
  font-weight: 600;
  color: #3f454a;
}
.tools-subtitle {
  font-size: 13px;
  color: #8aa0ab;
  margin-top: 2px;
}
.add-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #00acc1;
  color: white;
  font-size: 14px;
  font-weight: 600;
  padding: 8px 18px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}
.add-btn:hover {
  background: #00838f;
}
.cancel-btn {
  display: inline-flex;
  align-items: center;
  background: #e8edef;
  color: #3f454a;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 18px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  margin-left: 8px;
  transition: background 0.2s;
}
.cancel-btn:hover {
  background: #dce3e7;
}

/* Table */
.table-card {
  background: white;
  border: 1px solid #e0e8ec;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.table-loading {
  display: flex;
  justify-content: center;
  padding: 48px;
}
.table-error {
  padding: 24px;
  color: #c62828;
  background: #fbe9e7;
}
.table-empty {
  padding: 64px 24px;
  text-align: center;
}
.roster-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.roster-table thead tr {
  background: #00acc1;
  color: white;
}
.roster-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
}
.roster-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f4f5;
}
.roster-table tbody tr:hover {
  background: #f0f8fa;
}
.table-foot {
  padding: 10px 16px;
  font-size: 12px;
  color: #8aa0ab;
  background: #f8fafb;
  border-top: 1px solid #e8eff2;
}
.copy-badge {
  font-family: 'SF Mono', 'Menlo', monospace;
  font-size: 13px;
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
  user-select: all;
}
.copy-badge-blue {
  color: #00838f;
  background: #e0f7fa;
}
.copy-badge-blue:hover { background: #b2ebf2; }
.copy-badge-green {
  color: #2e7d32;
  background: #e8f5e9;
}
.copy-badge-green:hover { background: #c8e6c9; }
.copy-toast {
  position: absolute;
  top: -28px;
  left: 50%;
  transform: translateX(-50%);
  background: #37474f;
  color: white;
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
  z-index: 10;
  pointer-events: none;
}
.action-btns {
  display: flex;
  align-items: center;
  gap: 12px;
}
.action-link {
  font-size: 12px;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
  padding: 0;
}
.action-link:disabled { opacity: 0.5; }
.action-link-blue {
  color: #00838f;
}
.action-link-blue:hover { color: #006064; text-decoration: underline; }
.action-link-red {
  color: #c62828;
}
.action-link-red:hover { color: #b71c1c; text-decoration: underline; }
.error-msg {
  margin-top: 12px;
  font-size: 13px;
  color: #c62828;
  background: #fbe9e7;
  border: 1px solid #ffcdd2;
  border-radius: 8px;
  padding: 8px 16px;
}

/* ============ EMPTY TAB ============ */
.empty-tab {
  background: white;
  border: 1px solid #e0e8ec;
  border-radius: 14px;
  padding: 80px 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  animation: fadeIn 0.3s ease;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.empty-tab h2 {
  font-size: 22px;
  font-weight: 400;
  color: #5a6a72;
  margin-bottom: 8px;
}
.empty-tab p {
  font-size: 14px;
  color: #8aa0ab;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ============ LIVE CLASSROOM ============ */
.live-classroom {
  animation: fadeIn 0.3s ease;
  padding: 0 0 40px 0;
}

.live-header {
  margin-bottom: 24px;
}
.live-title {
  font-family: Georgia, 'Times New Roman', Times, serif;
  font-size: 28px;
  color: #5a6a72;
  font-weight: 400;
  display: flex;
  align-items: center;
  gap: 8px;
}
.help-circle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid #b1c1c9;
  color: #b1c1c9;
  font-size: 11px;
  font-family: sans-serif;
  cursor: pointer;
}

.stats-row {
  display: flex;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  margin-bottom: 30px;
  overflow: hidden;
  border: 1px solid #e0e8ec;
}
.stat-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 10px;
  border-right: 1px solid #f0f4f5;
  text-align: center;
  gap: 8px;
}
.stat-box:last-child {
  border-right: none;
}
.stat-icon-wrapper {
  margin-bottom: 4px;
}
.stat-icon-wrapper.blue-icon { color: #2196f3; }
.stat-icon-wrapper.grey-icon { color: #b1c1c9; }
.stat-icon-wrapper.orange-icon { color: #ff9800; }
.stat-icon-wrapper.yellow-icon { color: #ffeb3b; }
.stat-icon-wrapper.green-icon { color: #4caf50; }

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.stat-number {
  font-size: 28px;
  font-weight: 300;
  color: #2196f3;
  line-height: 1;
  margin-bottom: 4px;
}
.stat-icon-wrapper.grey-icon + .stat-content .stat-number { color: #b1c1c9; }
.stat-icon-wrapper.orange-icon + .stat-content .stat-number { color: #ff9800; }
.stat-icon-wrapper.yellow-icon + .stat-content .stat-number { color: #ffb300; }
.stat-icon-wrapper.green-icon + .stat-content .stat-number { color: #4caf50; }

.stat-label {
  font-size: 11px;
  font-weight: 600;
  color: #6b7c85;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  line-height: 1.3;
}

.activity-wall-container {
  margin-top: 10px;
}
.activity-wall-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #c9dfdb;
  padding-bottom: 12px;
  margin-bottom: 20px;
}
.activity-wall-title {
  font-size: 22px;
  font-weight: 400;
  color: #5a6a72;
  display: flex;
  align-items: center;
  gap: 8px;
}
.send-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  background: #e8f4f8;
  color: #2196f3;
  cursor: pointer;
}

.activity-controls {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 14px;
  color: #5a6a72;
}
.sort-control {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.group-control {
  display: flex;
  align-items: center;
  gap: 8px;
}
.toggle-switch {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #cfd8dc;
  border-radius: 20px;
  width: 44px;
  height: 22px;
  position: relative;
  cursor: pointer;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}
.toggle-knob {
  width: 18px;
  height: 18px;
  background: white;
  border: 1px solid #cfd8dc;
  border-radius: 50%;
  position: absolute;
  left: 2px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.toggle-label {
  font-size: 10px;
  font-weight: 600;
  color: #b0bec5;
  position: absolute;
  right: 6px;
  text-transform: uppercase;
}

.activity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.student-activity-card {
  background: white;
  border-radius: 6px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.06);
  padding: 16px;
  border-top: 4px solid #2196f3;
}
.sac-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.sac-name {
  font-size: 16px;
  font-weight: 600;
  color: #3f454a;
  display: flex;
  align-items: center;
  gap: 8px;
}
.send-icon-small {
  color: #2196f3;
  opacity: 0.8;
}

.sac-skill {
  font-size: 12px;
  color: #6b7c85;
  margin-bottom: 24px;
  min-height: 36px; /* for 2 lines */
}

.sac-stats {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 6px;
}
.sac-questions {
  font-size: 11px;
  color: #8aa0ab;
}
.sac-score {
  font-size: 26px;
  font-weight: 300;
  line-height: 1;
}

.score-blue { color: #2196f3; }
.score-gold { color: #ffb300; }
.score-green { color: #4caf50; }
.score-orange { color: #ff9800; }

.sac-bar-bg {
  width: 100%;
  height: 4px;
  background: #eef2f4;
  border-radius: 2px;
  overflow: hidden;
}
.sac-bar-fill {
  height: 100%;
  border-radius: 2px;
}
.score-blue-bg { background-color: #2196f3; }
.score-gold-bg { background-color: #ffb300; }
.score-green-bg { background-color: #4caf50; }
.score-orange-bg { background-color: #ff9800; }

.inactive-students {
  display: flex;
  justify-content: center;
  padding: 20px 0;
  border-top: 1px solid rgba(0,0,0,0.05);
}
.show-inactive-btn {
  display: inline-flex;
  align-items: center;
  background: none;
  border: none;
  color: #6b7c85;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}
.show-inactive-btn:hover {
  color: #4a5568;
}

/* ============ LIVE CLASSROOM ENHANCEMENTS ============ */
.live-pulse {
  display: inline-block;
  width: 10px;
  height: 10px;
  background: #4caf50;
  border-radius: 50%;
  animation: livePulse 2s ease-in-out infinite;
}
@keyframes livePulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.5); }
  50% { box-shadow: 0 0 0 8px rgba(76, 175, 80, 0); }
}

.live-subtitle {
  font-size: 12px;
  color: #8aa0ab;
  margin-top: 4px;
  font-weight: 400;
}

.live-empty-state {
  background: white;
  border: 2px dashed #d2eef3;
  border-radius: 16px;
  padding: 60px 24px;
  text-align: center;
  animation: fadeIn 0.3s ease;
}
.live-empty-icon {
  color: #b1c1c9;
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
}
.live-empty-text {
  font-size: 18px;
  color: #5a6a72;
  font-weight: 500;
  margin-bottom: 8px;
}
.live-empty-hint {
  font-size: 14px;
  color: #8aa0ab;
}

/* Active student card enhancements */
.student-activity-card.needs-help {
  border-top-color: #ff9800;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.15);
}

.sac-pulse {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #4caf50;
  border-radius: 50%;
  margin-right: 6px;
  flex-shrink: 0;
  animation: livePulse 2s ease-in-out infinite;
}

.needs-help-badge {
  font-size: 10px;
  font-weight: 600;
  color: #e65100;
  background: #fff3e0;
  border: 1px solid #ffcc80;
  border-radius: 12px;
  padding: 2px 10px;
  white-space: nowrap;
}

.sac-detail-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}
.sac-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}
.sac-detail-label {
  font-size: 10px;
  font-weight: 600;
  color: #8aa0ab;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}
.sac-detail-value {
  font-size: 20px;
  font-weight: 300;
  color: #3f454a;
  line-height: 1;
}
.sac-correct {
  color: #4caf50;
}
.sac-wrong {
  color: #f44336;
}

.sac-score-label {
  font-size: 11px;
  color: #8aa0ab;
  font-weight: 500;
}

/* Inactive students list */
.inactive-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 16px 0;
  animation: fadeIn 0.3s ease;
}
.inactive-student-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f5f7f8;
  border: 1px solid #e0e8ec;
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 13px;
  color: #6b7c85;
  font-weight: 500;
}
.inactive-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: #cfd8dc;
  border-radius: 50%;
}

.rotate-180 {
  transform: rotate(180deg);
}
.transition-transform {
  transition: transform 0.2s ease;
}

/* Quizzes Main Styles */
.quizzes-section {
  max-width: 1280px;
  margin: 0 auto;
  padding: 22px 0 56px;
}
.quizzes-top-action {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}
.create-quiz-action-btn {
  background: #00a99d;
  color: white;
  font-weight: 700;
  font-size: 14px;
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  box-shadow: 0 2px 5px rgba(0, 169, 157, 0.22);
}
.create-quiz-action-btn:hover {
  background: #009287;
  box-shadow: 0 4px 10px rgba(0, 169, 157, 0.28);
}

/* Filters */
.quizzes-filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  background: transparent;
  padding: 8px 0;
  border-radius: 0;
  border: none;
  box-shadow: none;
  flex-wrap: wrap;
}
.filter-student-group {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #475569;
}
.filter-student-select {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px 12px;
  background: #f8fafc;
  font-weight: 500;
  color: #334155;
  outline: none;
}
.filter-student-select:focus {
  border-color: #38b000;
  box-shadow: 0 0 0 2px rgba(56, 176, 0, 0.1);
}
.search-quiz-group {
  position: relative;
  width: 100%;
  max-width: 320px;
}
.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #94a3b8;
}
.search-quiz-input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #f8fafc;
  font-size: 14px;
  color: #334155;
  outline: none;
}
.search-quiz-input:focus {
  border-color: #38b000;
  box-shadow: 0 0 0 2px rgba(56, 176, 0, 0.1);
}

/* Loading & State wrappers */
.loading-state-wrapper,
.error-state-wrapper,
.empty-state-wrapper {
  background: white;
  padding: 48px;
  text-align: center;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  color: #64748b;
  margin-bottom: 24px;
}
.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #334155;
  margin-top: 8px;
}
.empty-sub {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

/* Blocks container */
.quizzes-blocks-container {
  display: flex;
  flex-direction: column;
  gap: 50px;
  margin-bottom: 48px;
}
.quiz-block-section {
  display: flex;
  flex-direction: column;
}
.block-section-title {
  font-size: 29px;
  line-height: 1.15;
  font-weight: 600;
  color: #555;
  margin-bottom: 16px;
  padding-bottom: 0;
  border-bottom: none;
}
.quiz-block-empty {
  font-size: 14px;
  color: #94a3b8;
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  text-align: center;
}

/* Grid layout */
.quiz-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.quiz-cards-column {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 18px;
}

/* Cards */
.quiz-card-item {
  background: white;
  border: 1px solid #e5eef2;
  border-radius: 8px;
  box-shadow: 0 2px 7px rgba(33, 77, 88, 0.08);
  position: relative;
  overflow: visible;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.2s ease;
  width: 100%;
  max-width: 346px;
  min-height: 190px;
}
.quiz-card-item:hover {
  box-shadow: 0 4px 12px rgba(33, 77, 88, 0.12);
}
.card-header {
  padding: 15px 14px 10px;
  border-bottom: 1px solid #c7dfe9;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.card-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.chart-mini-icon {
  font-size: 16px;
}
.card-title-text {
  font-size: 16px;
  font-weight: 800;
  color: #555;
}
.options-trigger-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}
.options-trigger-btn:hover {
  background: #f1f5f9;
}
.options-dropdown-menu {
  position: absolute;
  right: 0;
  margin-top: 4px;
  width: 128px;
  background: white;
  border: 1px solid #e2e8f0;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  padding: 4px 0;
  z-index: 9999;
}
.dropdown-menu-item {
  width: 100%;
  text-align: left;
  padding: 8px 12px;
  font-size: 13px;
  color: #334155;
  background: none;
  border: none;
  cursor: pointer;
}
.dropdown-menu-item:hover {
  background: #f8fafc;
}

.card-body {
  padding: 13px 14px 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.info-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  color: #555;
}
.info-icon {
  width: 16px;
  display: inline-flex;
  justify-content: center;
  color: #8fc7d4;
  font-size: 18px;
  line-height: 1;
}
.info-text {
  font-weight: 600;
}
.completion-badge-count {
  font-size: 14px;
  font-weight: 700;
  color: #159be8;
  background: transparent;
  padding: 0;
  border-radius: 0;
}

/* Progress bar */
.progress-bar-container {
  height: 12px;
  background: #e7fbff;
  border: 1px solid #77cdf7;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 4px;
}
.progress-bar-fill {
  height: 100%;
  background: #26b5f4;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.card-footer {
  padding: 10px 14px 14px;
  border-top: none;
  background: white;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  display: flex;
  justify-content: center;
}

.end-quiz-btn {
  display: inline-flex;
  align-items: center;
  gap: 0;
  background: white;
  border: 1px solid #20aef2;
  color: #1aa7ea;
  font-weight: 500;
  font-size: 16px;
  padding: 7px 13px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.end-quiz-btn:hover {
  background: #eefaff;
  border-color: #159be8;
}
.caret-icon {
  font-size: 10px;
  color: #159be8;
  border-left: 1px solid #20aef2;
  padding-left: 11px;
  margin-left: 12px;
}

.keep-adding-btn {
  display: inline-block;
  background: #00a99d;
  color: white;
  font-weight: 700;
  font-size: 16px;
  padding: 9px 38px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: center;
}
.keep-adding-btn:hover {
  background: #009287;
}

/* Past Quizzes Table */
.past-quizzes-table-card {
  background: white;
  border: none;
  border-radius: 4px;
  overflow: visible;
  box-shadow: 0 1px 3px rgba(33, 77, 88, 0.06);
  width: 100%;
}
.past-quizzes-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 14px;
}
.past-quizzes-table th {
  background: transparent;
  color: #0878c9;
  font-weight: 700;
  font-size: 13px;
  text-transform: none;
  padding: 10px 16px;
  border-bottom: 2px solid #149fee;
  cursor: pointer;
  white-space: nowrap;
}
.past-quizzes-table th::after {
  content: ' ↕';
  font-size: 10px;
  color: #b0bec5;
}
.past-quizzes-table td {
  padding: 10px 16px;
  border-bottom: none;
  color: #555;
  vertical-align: middle;
}
.past-quizzes-table tr:hover td {
  background: #f7fcff;
}
.past-quizzes-table th.no-sort::after {
  content: '';
}
.past-quizzes-table th.no-sort {
  cursor: default;
}
.quiz-name-cell {
  font-weight: 600;
  color: #555;
}
.average-score-cell {
  font-weight: 600;
  color: #555;
}
.report-action-cell {
  white-space: nowrap;
}
.view-report-link-btn {
  background: none;
  border: none;
  color: #159be8;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.15s;
}
.view-report-link-btn:hover {
  background: #eefaff;
}
.graph-icon {
  font-size: 16px;
}

</style>
