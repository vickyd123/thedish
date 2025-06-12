<template>
  <div>
    <button
      class="theme-toggle"
      @click="toggleTheme"
      :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
    >
      <span v-if="theme === 'dark'">🌙</span>
      <span v-else>☀️</span>
    </button>
    <router-view />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'App',
  setup() {
    const theme = ref(localStorage.getItem('theme') || 'light')

    const applyTheme = () => {
      document.body.classList.toggle('dark', theme.value === 'dark')
      document.body.classList.toggle('light', theme.value === 'light')
    }

    const toggleTheme = () => {
      theme.value = theme.value === 'dark' ? 'light' : 'dark'
      localStorage.setItem('theme', theme.value)
      applyTheme()
    }

    onMounted(() => {
      applyTheme()
    })

    return { theme, toggleTheme }
  }
}
</script>

<style>
/* Theme Toggle Button */
.theme-toggle {
  position: fixed;
  top: 24px;
  right: 24px;
  left: auto;
  z-index: 1000;
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  padding: 0.2em 0.4em;
  transition: background 0.2s;
}
.theme-toggle:focus {
  outline: 2px solid #2563eb;
}

/* Light Mode */
body.light {
  background: #f9f9fc;
  color: #1e293b;
}

/* DARK MODE: Unified Dark Blue Theme */
body.dark {
  background: #232946 !important;
  color: #f9f9fc !important;
}

/* Main containers and cards */
body.dark .card,
body.dark .profile-card,
body.dark .main-header,
body.dark .sidebar,
body.dark .main-content,
body.dark .search-section,
body.dark .hot-section {
  background: #232946 !important;
  color: #f9f9fc !important;
  box-shadow: 0 2px 12px rgba(0,0,0,0.18);
}

/* Sidebar and buttons */
body.dark .sidebar {
  background: #232946 !important;
  color: #f9f9fc !important;
}
body.dark .sidebar button {
  background: none !important;
  color: #f9f9fc !important;
}
body.dark .sidebar button.active,
body.dark .sidebar button:hover {
  background: #2563eb !important;
  color: #fff !important;
}

/* Inputs and selects */
body.dark .search-input,
body.dark select {
  background: #232946 !important;
  color: #f9f9fc !important;
  border-color: #334155 !important;
}
body.dark .search-input:focus {
  border-color: #7bbef9 !important;
  box-shadow: 0 0 0 2px rgba(123, 190, 249, 0.3) !important;
}

/* Lists and results */
body.dark .search-results,
body.dark .search-result-item,
body.dark .hot-item {
  background: #232946 !important;
  color: #f9f9fc !important;
}
body.dark .search-result-item:hover,
body.dark .search-result-item:focus {
  background: #334155 !important;
}

/* Buttons and controls */
body.dark .hot-controls button {
  background: #232946 !important;
  color: #7bbef9 !important;
  border-color: #334155 !important;
}
body.dark .hot-controls button.active,
body.dark .hot-controls button:hover {
  background: #7bbef9 !important;
  color: #232946 !important;
}

/* Headings and highlights */
body.dark .main-header h1,
body.dark .player-title,
body.dark .search-section h2,
body.dark .hot-section h2 {
  color: #7bbef9 !important;
}

/* Miscellaneous */
body.dark .no-results,
body.dark .no-stats {
  color: #b6c6e3 !important;
}
body.dark .team-logo-mini,
body.dark .team-logo {
  background: #232946 !important;
}
body.dark .hot-team,
body.dark .hot-league-div {
  color: #b6c6e3 !important;
}
body.dark .hot-name {
  color: #f9f9fc !important;
}
body.dark .hot-name:hover {
  color: #7bbef9 !important;
}

/* Responsive containers and tables (unchanged, but include for completeness) */
.profile-container,
.profile-card {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  box-sizing: border-box;
}
.splits-table-horizontal {
  width: 100%;
  overflow-x: auto;
  margin-top: 28px;
}
.splits-table-horizontal table {
  width: 100%;
  min-width: 500px;
  border-collapse: collapse;
}
.splits-table-horizontal th,
.splits-table-horizontal td {
  padding: 12px 16px;
  text-align: center;
  font-size: 1.13rem;
  box-sizing: border-box;
}
.splits-table-horizontal th {
  background: #e0e7ff;
  color: #2563eb;
  font-weight: 700;
  font-size: 1.15rem;
  letter-spacing: 0.5px;
}
.splits-table-horizontal tr:nth-child(even) td {
  background: #f3f6fb;
}
.stat-label {
  font-weight: 600;
  color: #2563eb;
  text-align: left;
}
.stat-value {
  font-family: 'Menlo', 'Monaco', monospace;
  color: #0f172a;
}

/* Responsive adjustments */
@media (max-width: 1100px) {
  .profile-container,
  .profile-card {
    max-width: 98vw;
    padding: 8px;
  }
  .splits-table-horizontal table {
    min-width: 400px;
    font-size: 0.98rem;
  }
}
@media (max-width: 700px) {
  .splits-table-horizontal th,
  .splits-table-horizontal td {
    padding: 8px 6px;
    font-size: 0.95rem;
  }
}
</style>
