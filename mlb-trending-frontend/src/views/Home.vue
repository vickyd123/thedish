<template>
  <div class="home-container">
    <!-- Mobile Menu Button -->
    <button 
      class="mobile-menu-toggle"
      @click="mobileMenuOpen = !mobileMenuOpen"
      :aria-expanded="mobileMenuOpen"
      aria-label="Toggle navigation menu"
    >
      <span class="hamburger-line" :class="{ active: mobileMenuOpen }"></span>
      <span class="hamburger-line" :class="{ active: mobileMenuOpen }"></span>
      <span class="hamburger-line" :class="{ active: mobileMenuOpen }"></span>
    </button>

    <!-- Sidebar -->
    <div class="sidebar" :class="{ 'mobile-open': mobileMenuOpen }">
      <div class="sidebar-header">
        <h2>Navigation</h2>
        <button 
          class="mobile-close-btn"
          @click="mobileMenuOpen = false"
          aria-label="Close navigation menu"
        >×</button>
      </div>
      <button
        :class="{ active: activeTab === 'trivia' }"
        @click="setActiveTab('trivia')"
      >Daily Trivia</button>
      <button
        :class="{ active: activeTab === 'digest' }"
        @click="setActiveTab('digest')"
      >Daily Digest</button>
      <button
        :class="{ active: activeTab === 'playerSearch' }"
        @click="setActiveTab('playerSearch')"
      >Player Search</button>
      <button
        :class="{ active: activeTab === 'batterPitcher' }"
        @click="setActiveTab('batterPitcher')"
      >Batter vs Pitcher</button>
      <button
        :class="{ active: activeTab === 'standingsTab' }"
        @click="setActiveTab('standingsTab')"
      >Standings</button>
    </div>

    <!-- Mobile Overlay -->
    <div 
      class="mobile-overlay" 
      :class="{ active: mobileMenuOpen }"
      @click="mobileMenuOpen = false"
    ></div>

    <!-- Main Content Area -->
    <div class="main-content">
      <header class="main-header">
        <h1>thedish.io</h1>
      </header>

      <DailyTrivia v-if="activeTab === 'trivia'" />
      <DailyDigest v-if="activeTab === 'digest'" />
      <PlayerSearch v-if="activeTab === 'playerSearch'" />
      <BatterPitcher v-if="activeTab === 'batterPitcher'" />
      <StandingsTab v-if="activeTab === 'standingsTab'" />

      <!-- Who's Hot -->
      <section class="card hot-section">
        <div class="hot-header">
          <h2>Who's Hot?</h2>
          <div class="hot-controls" role="group" aria-label="Filter hot players by days">
            <button
              :class="{ active: hotDays === 7 }"
              @click="getWhosHot(7)"
            >Last 7 Days</button>
            <button
              :class="{ active: hotDays === 30 }"
              @click="getWhosHot(30)"
            >Last 30 Days</button>
          </div>
        </div>

        <!-- League & Division Filters -->
        <div class="hot-filters" role="group" aria-label="Filter hot players by league and division">
          <label>
            League:
            <select v-model="selectedLeague" aria-label="Select league filter">
              <option value="">All</option>
              <option value="AL">American League</option>
              <option value="NL">National League</option>
            </select>
          </label>
          <label>
            Division:
            <select v-model="selectedDivision" aria-label="Select division filter">
              <option value="">All</option>
              <option value="East">East</option>
              <option value="Central">Central</option>
              <option value="West">West</option>
            </select>
          </label>
        </div>

        <!-- Sortable Stats Table -->
        <div v-if="filteredHotPlayers.length" class="hot-table-container">
          <table class="hot-table">
            <thead>
              <tr>
                <th class="player-header">Player</th>
                <th 
                  class="stat-header sortable" 
                  @click="sortBy('avg')"
                  :class="{ 'sorted-asc': sortField === 'avg' && sortDirection === 'asc', 'sorted-desc': sortField === 'avg' && sortDirection === 'desc' }"
                >
                  AVG
                  <span class="sort-arrow">{{ getSortArrow('avg') }}</span>
                </th>
                <th 
                  class="stat-header sortable" 
                  @click="sortBy('home_runs')"
                  :class="{ 'sorted-asc': sortField === 'home_runs' && sortDirection === 'asc', 'sorted-desc': sortField === 'home_runs' && sortDirection === 'desc' }"
                >
                  HR
                  <span class="sort-arrow">{{ getSortArrow('home_runs') }}</span>
                </th>
                <th 
                  class="stat-header sortable" 
                  @click="sortBy('rbi')"
                  :class="{ 'sorted-asc': sortField === 'rbi' && sortDirection === 'asc', 'sorted-desc': sortField === 'rbi' && sortDirection === 'desc' }"
                >
                  RBI
                  <span class="sort-arrow">{{ getSortArrow('rbi') }}</span>
                </th>
                <th 
                  class="stat-header sortable" 
                  @click="sortBy('hits')"
                  :class="{ 'sorted-asc': sortField === 'hits' && sortDirection === 'asc', 'sorted-desc': sortField === 'hits' && sortDirection === 'desc' }"
                >
                  H
                  <span class="sort-arrow">{{ getSortArrow('hits') }}</span>
                </th>
                <th 
                  class="stat-header sortable" 
                  @click="sortBy('at_bats')"
                  :class="{ 'sorted-asc': sortField === 'at_bats' && sortDirection === 'asc', 'sorted-desc': sortField === 'at_bats' && sortDirection === 'desc' }"
                >
                  AB
                  <span class="sort-arrow">{{ getSortArrow('at_bats') }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="player in sortedHotPlayers" 
                :key="player.player_id"
                class="hot-row"
              >
                <td class="player-cell">
                  <div class="player-info">
                    <img
                      v-if="getTeamLogoUrl(player.team)"
                      :src="getTeamLogoUrl(player.team)"
                      :alt="player.team + ' logo'"
                      class="team-logo-mini"
                      loading="lazy"
                    />
                    <div class="player-details">
                      <span 
                        class="player-name" 
                        @click="goToPlayer(player.player_id)" 
                        tabindex="0" 
                        role="button" 
                        @keydown.enter="goToPlayer(player.player_id)"
                      >
                        {{ player.player_name }}
                      </span>
                      <div class="team-info">
                        <span class="team-name">{{ player.team }}</span>
                        <span class="league-div" v-if="TEAM_INFO[player.team]">
                          {{ TEAM_INFO[player.team].league }}, {{ TEAM_INFO[player.team].division }}
                        </span>
                      </div>
                    </div>
                  </div>
                </td>
                <td class="stat-cell">{{ player.avg }}</td>
                <td class="stat-cell">{{ player.home_runs }}</td>
                <td class="stat-cell">{{ player.rbi }}</td>
                <td class="stat-cell">{{ player.hits }}</td>
                <td class="stat-cell">{{ player.at_bats }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="no-results">No trending players to display.</p>
      </section>
    </div>
  </div>
</template>

<script>
import DailyTrivia from './DailyTrivia.vue'
import DailyDigest from './DailyDigest.vue'
import PlayerSearch from './PlayerSearch.vue'
import BatterPitcher from './BatterPitcher.vue'
import StandingsTab from './StandingsTab.vue'

// Replace with your actual team info and ID map
const TEAM_ID_MAP = {
  "Arizona Diamondbacks": 109,
  "Atlanta Braves": 144,
  "Baltimore Orioles": 110,
  "Boston Red Sox": 111,
  "Chicago White Sox": 145,
  "Chicago Cubs": 112,
  "Cincinnati Reds": 113,
  "Cleveland Guardians": 114,
  "Colorado Rockies": 115,
  "Detroit Tigers": 116,
  "Houston Astros": 117,
  "Kansas City Royals": 118,
  "Los Angeles Angels": 108,
  "Los Angeles Dodgers": 119,
  "Miami Marlins": 146,
  "Milwaukee Brewers": 158,
  "Minnesota Twins": 142,
  "New York Yankees": 147,
  "New York Mets": 121,
  "Athletics": 133,
  "Philadelphia Phillies": 143,
  "Pittsburgh Pirates": 134,
  "San Diego Padres": 135,
  "San Francisco Giants": 137,
  "Seattle Mariners": 136,
  "St. Louis Cardinals": 138,
  "Tampa Bay Rays": 139,
  "Texas Rangers": 140,
  "Toronto Blue Jays": 141,
  "Washington Nationals": 120
};
const TEAM_INFO = {
  "Arizona Diamondbacks": { league: "NL", division: "West" },
  "Atlanta Braves": { league: "NL", division: "East" },
  "Baltimore Orioles": { league: "AL", division: "East" },
  "Boston Red Sox": { league: "AL", division: "East" },
  "Chicago White Sox": { league: "AL", division: "Central" },
  "Chicago Cubs": { league: "NL", division: "Central" },
  "Cincinnati Reds": { league: "NL", division: "Central" },
  "Cleveland Guardians": { league: "AL", division: "Central" },
  "Colorado Rockies": { league: "NL", division: "West" },
  "Detroit Tigers": { league: "AL", division: "Central" },
  "Houston Astros": { league: "AL", division: "West" },
  "Kansas City Royals": { league: "AL", division: "Central" },
  "Los Angeles Angels": { league: "AL", division: "West" },
  "Los Angeles Dodgers": { league: "NL", division: "West" },
  "Miami Marlins": { league: "NL", division: "East" },
  "Milwaukee Brewers": { league: "NL", division: "Central" },
  "Minnesota Twins": { league: "AL", division: "Central" },
  "New York Yankees": { league: "AL", division: "East" },
  "New York Mets": { league: "NL", division: "East" },
  "Oakland Athletics": { league: "AL", division: "West" },
  "Athletics": { league: "AL", division: "West" },
  "Philadelphia Phillies": { league: "NL", division: "East" },
  "Pittsburgh Pirates": { league: "NL", division: "Central" },
  "San Diego Padres": { league: "NL", division: "West" },
  "San Francisco Giants": { league: "NL", division: "West" },
  "Seattle Mariners": { league: "AL", division: "West" },
  "St. Louis Cardinals": { league: "NL", division: "Central" },
  "Tampa Bay Rays": { league: "AL", division: "East" },
  "Texas Rangers": { league: "AL", division: "West" },
  "Toronto Blue Jays": { league: "AL", division: "East" },
  "Washington Nationals": { league: "NL", division: "East" }
};

export default {
  name: 'HomePage',
  components: {
    DailyTrivia,
    DailyDigest,
    PlayerSearch,
    BatterPitcher,
    StandingsTab
  },
  data() {
  return {
    hotPlayers: [],
    hotDays: 7,
    selectedLeague: '',
    selectedDivision: '',
    activeTab: 'trivia',
    sortField: 'avg',  // This stays the same
    sortDirection: 'desc',
    mobileMenuOpen: false
  }
},
  computed: {
  filteredHotPlayers() {
    const filtered = this.hotPlayers.filter(player => {
      const info = TEAM_INFO[player.team];
      if (!info) return false;
      const leagueMatch = this.selectedLeague ? info.league === this.selectedLeague : true;
      const divisionMatch = this.selectedDivision ? info.division === this.selectedDivision : true;
      return leagueMatch && divisionMatch;
    });
    return filtered;
  },
  sortedHotPlayers() {
    // Since backend is now handling the sorting, just return filtered results
    // The backend already sorted them correctly based on sortField
    return this.filteredHotPlayers.slice(0, 10);
  },
  TEAM_INFO() {
    return TEAM_INFO;
  }
},
  methods: {
  getTeamLogoUrl(teamName) {
    const teamId = TEAM_ID_MAP[teamName];
    return teamId
      ? `https://www.mlbstatic.com/team-logos/team-cap-on-light/${teamId}.svg`
      : null;
  },
  async getWhosHot(days) {
    this.hotDays = days;
    try {
      // Always pass the current sort field to backend
      const res = await fetch(`/api/whos_hot/${days}?sort=${this.sortField}`);
      this.hotPlayers = await res.json();
    } catch {
      this.hotPlayers = [];
    }
  },
  goToPlayer(player_id) {
    this.$router.push({ name: 'PlayerProfile', params: { player_id } });
  },
  async sortBy(field) {
    if (this.sortField === field) {
      // Toggle direction if same field
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      // New field, default to descending for stats
      this.sortField = field;
      this.sortDirection = 'desc';
    }
    
    // Re-fetch data from backend with new sort parameter
    try {
      const res = await fetch(`/api/whos_hot/${this.hotDays}?sort=${this.sortField}`);
      this.hotPlayers = await res.json();
    } catch {
      this.hotPlayers = [];
    }
  },
  getSortArrow(field) {
    if (this.sortField !== field) return '';
    return this.sortDirection === 'asc' ? '↑' : '↓';
  },
  setActiveTab(tab) {
    this.activeTab = tab;
    this.mobileMenuOpen = false;
  }
},

mounted() {
  // This will now call the backend with ?sort=avg by default
  this.getWhosHot(7);
}
}
</script>

<style scoped>
.home-container {
  display: flex;
  min-height: 100vh;
  background: #f8fafc;
}

/* Mobile Menu Toggle Button */
.mobile-menu-toggle {
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 1001;
  background: #2563eb;
  border: none;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  display: none;
  flex-direction: column;
  gap: 3px;
  width: 44px;
  height: 44px;
  justify-content: center;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.hamburger-line {
  width: 20px;
  height: 2px;
  background: #fff;
  transition: all 0.3s ease;
  transform-origin: center;
}

.hamburger-line.active:nth-child(1) {
  transform: rotate(45deg) translate(4px, 4px);
}

.hamburger-line.active:nth-child(2) {
  opacity: 0;
}

.hamburger-line.active:nth-child(3) {
  transform: rotate(-45deg) translate(4px, -4px);
}

/* Mobile Overlay */
.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.mobile-overlay.active {
  opacity: 1;
  visibility: visible;
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 180px;
  background: #f1f5f9;
  padding: 24px 16px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 2px 0 8px rgba(0,0,0,0.04);
  z-index: 1000;
  transition: transform 0.3s ease;
}

.sidebar-header {
  display: none;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.sidebar-header h2 {
  margin: 0;
  color: #334155;
  font-size: 1.2rem;
}

.mobile-close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mobile-close-btn:hover {
  background: #e2e8f0;
}

.sidebar button {
  background: none;
  border: none;
  font-size: 1.1rem;
  color: #334155;
  padding: 12px 16px;
  border-radius: 8px;
  text-align: left;
  cursor: pointer;
  transition: background 0.18s, color 0.18s;
}

.sidebar button.active,
.sidebar button:hover {
  background: #2563eb;
  color: #fff;
}

.main-content {
  margin-left: 180px;
  padding: 24px;
  width: calc(100% - 180px);
  min-height: 100vh;
}

.main-header {
  background: transparent !important;
  padding: 0 !important;
  margin: 24px auto !important; /* Center it */
  box-shadow: none !important;
  border: none !important;
  outline: none !important;
  border-radius: 0 !important;
  
  /* Make the header only as wide as its content */
  display: inline-block !important;
  width: auto !important;
  max-width: none !important;
  
  /* Center the header container */
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}

.main-header h1 {
  color: #1e293b;
  background: transparent !important;
  padding: 0 !important;
  margin: 0 !important;
  font-size: 1.8rem;
  font-weight: 600;
  text-align: center;
  
  /* Remove ALL possible box-creating properties */
  border: none !important;
  border: 0 !important;
  outline: none !important;
  outline: 0 !important;
  box-shadow: none !important;
  text-decoration: none !important;
  border-radius: 0 !important;
  box-sizing: border-box;
  
  /* Remove any pseudo-elements that might create boxes */
  position: relative;
}


/* Also ensure dark mode doesn't add any boxes */
.dark .main-header h1 {
  color: #7bbef9;
  background: transparent !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  text-decoration: none !important;
  border-radius: 0 !important;
}

.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  padding: 24px;
  margin-bottom: 24px;
}

.hot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.hot-controls {
  display: flex;
  gap: 8px;
}

.hot-controls button {
  background: #e2e8f0;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.18s;
  font-size: 0.9rem;
  white-space: nowrap;
}

.hot-controls button.active {
  background: #2563eb;
  color: #fff;
}

.hot-filters {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.hot-filters label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
}

.hot-filters select {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  font-size: 0.9rem;
}

/* Table Styles */
.hot-table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  -webkit-overflow-scrolling: touch;
}

.hot-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  min-width: 600px;
}

.hot-table th,
.hot-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.hot-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
  position: sticky;
  top: 0;
  z-index: 10;
}

.stat-header.sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.15s;
  position: relative;
}

.stat-header.sortable:hover {
  background: #e2e8f0;
}

.stat-header.sorted-asc,
.stat-header.sorted-desc {
  background: #dbeafe;
  color: #1e40af;
}

.sort-arrow {
  margin-left: 4px;
  font-size: 12px;
  opacity: 0.7;
}

.player-header {
  min-width: 200px;
}

.stat-header {
  min-width: 60px;
  text-align: center;
}

.player-cell {
  min-width: 200px;
}

.stat-cell {
  text-align: center;
  font-weight: 500;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.team-logo-mini {
  width: 24px;
  height: 24px;
  object-fit: contain;
  flex-shrink: 0;
}

.player-details {
  min-width: 0;
}

.player-name {
  font-weight: 600;
  cursor: pointer;
  color: #1e293b;
  display: block;
  margin-bottom: 2px;
}

.player-name:hover {
  color: #2563eb;
}

.team-info {
  font-size: 0.85rem;
  color: #64748b;
}

.team-name {
  font-weight: 500;
}

.league-div {
  margin-left: 4px;
  color: #94a3b8;
}

.hot-row:hover {
  background: #f8fafc;
}

.no-results {
  color: #64748b;
  font-style: italic;
  text-align: center;
  margin: 16px 0;
}

/* ===== MOBILE RESPONSIVE STYLES ===== */
@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: flex;
  }

  .sidebar {
    transform: translateX(-100%);
    width: 280px;
    padding: 80px 24px 24px;
  }

  .sidebar.mobile-open {
    transform: translateX(0);
  }

  .sidebar-header {
    display: flex;
  }

  .main-content {
    margin-left: 0;
    width: 100%;
    padding: 80px 16px 24px;
  }

  .card {
    padding: 16px;
    margin-bottom: 16px;
  }

  .hot-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .hot-header h2 {
    text-align: center;
    margin-bottom: 0;
  }

  .hot-controls {
    justify-content: center;
    flex-wrap: wrap;
  }

  .hot-controls button {
    flex: 1;
    min-width: 120px;
  }

  .hot-filters {
    flex-direction: column;
    gap: 12px;
  }

  .hot-filters label {
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
  }

  .hot-filters select {
    padding: 10px;
    font-size: 1rem;
  }

  .hot-table {
    min-width: 500px;
  }

  .hot-table th,
  .hot-table td {
    padding: 8px 6px;
    font-size: 0.85rem;
  }

  .player-header {
    min-width: 160px;
  }

  .stat-header {
    min-width: 50px;
  }

  .player-cell {
    min-width: 160px;
  }

  .team-logo-mini {
    width: 20px;
    height: 20px;
  }

  .player-info {
    gap: 8px;
  }

  .player-name {
    font-size: 0.9rem;
  }

  .team-info {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 80px 8px 16px;
  }

  .card {
    padding: 12px;
  }

  .hot-controls button {
    padding: 10px 12px;
    font-size: 0.85rem;
  }

  .hot-table th,
  .hot-table td {
    padding: 6px 4px;
    font-size: 0.8rem;
  }

  .player-header {
    min-width: 140px;
  }

  .player-cell {
    min-width: 140px;
  }

  .stat-header {
    min-width: 40px;
  }

  .team-logo-mini {
    width: 18px;
    height: 18px;
  }

  .player-name {
    font-size: 0.85rem;
  }

  .team-info {
    font-size: 0.7rem;
  }
}

/* ===== DARK MODE OVERRIDES ===== */
body.dark .home-container,
body.dark .card,
body.dark .hot-section,
body.dark .sidebar {
  background: #232946 !important;
  color: #f9f9fc !important;
}

body.dark .mobile-menu-toggle {
  background: #7bbef9 !important;
}

body.dark .mobile-overlay {
  background: rgba(0, 0, 0, 0.7) !important;
}

body.dark .sidebar-header {
  border-bottom-color: #334155 !important;
}

body.dark .sidebar-header h2 {
  color: #f9f9fc !important;
}

body.dark .mobile-close-btn {
  color: #f9f9fc !important;
}

body.dark .mobile-close-btn:hover {
  background: #334155 !important;
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

body.dark .hot-filters select {
  background: #232946 !important;
  color: #f9f9fc !important;
  border-color: #334155 !important;
}

/* Dark Mode Table Styles */
body.dark .hot-table-container {
  border-color: #334155 !important;
}

body.dark .hot-table {
  background: #232946 !important;
}

body.dark .hot-table th {
  background: #1a1d3a !important;
  color: #f9f9fc !important;
  border-bottom-color: #334155 !important;
}

body.dark .hot-table td {
  border-bottom-color: #334155 !important;
  color: #f9f9fc !important;
}

body.dark .stat-header.sortable:hover {
  background: #2a2e4a !important;
}

body.dark .stat-header.sorted-asc,
body.dark .stat-header.sorted-desc {
  background: #2563eb !important;
  color: #fff !important;
}

body.dark .player-name {
  color: #7bbef9 !important;
}

body.dark .player-name:hover {
  color: #a7d2ff !important;
}

body.dark .team-info,
body.dark .team-name {
  color: #b6c6e3 !important;
}

body.dark .league-div {
  color: #8b9cc7 !important;
}

body.dark .hot-row:hover {
  background: #2a2e4a !important;
}

body.dark .no-results {
  color: #b6c6e3 !important;
}
a
@media (prefers-color-scheme: dark) {
  .main-header h1 {
    color: #7bbef9;
    background: transparent !important;
    padding: 0 !important;
    margin: 24px 0 24px 24px !important; /* Keep margin consistent */
  }
}


@media (max-width: 768px) {
  .main-header h1 {
    margin-left: 0 !important;
    margin-right: 0 !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
  }
}
</style>