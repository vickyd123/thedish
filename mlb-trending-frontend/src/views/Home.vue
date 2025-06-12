<template>
  <div class="home-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <button
        :class="{ active: activeTab === 'trivia' }"
        @click="activeTab = 'trivia'"
      >Daily Trivia</button>
      <button
        :class="{ active: activeTab === 'digest' }"
        @click="activeTab = 'digest'"
      >Daily Digest</button>
      <button
        :class="{ active: activeTab === 'playerSearch' }"
        @click="activeTab = 'playerSearch'"
      >Player Search</button>
      <button
        :class="{ active: activeTab === 'batterPitcher' }"
        @click="activeTab = 'batterPitcher'"
      >Batter vs Pitcher</button>
      <button
        :class="{ active: activeTab === 'standingsTab' }"
        @click="activeTab = 'standingsTab'"
      >Standings</button>
    </div>

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

        <ul v-if="filteredHotPlayers.length" class="hot-list">
          <li
            v-for="player in filteredHotPlayers"
            :key="player.player_id"
            class="hot-item"
          >
            <div class="hot-row">
              <img
                v-if="getTeamLogoUrl(player.team)"
                :src="getTeamLogoUrl(player.team)"
                :alt="player.team + ' logo'"
                class="team-logo-mini"
                loading="lazy"
              />
              <span class="hot-name" @click="goToPlayer(player.player_id)" tabindex="0" role="button" @keydown.enter="goToPlayer(player.player_id)">
                {{ player.player_name }}
              </span>
              <span class="hot-team">( {{ player.team }} )</span>
              <span class="hot-league-div" v-if="TEAM_INFO[player.team]">
                - {{ TEAM_INFO[player.team].league }}, {{ TEAM_INFO[player.team].division }}
              </span>
            </div>
            <div class="hot-stats">
              AVG: <b>{{ player.avg }}</b> | HR: <b>{{ player.home_runs }}</b> | RBI: <b>{{ player.rbi }}</b> | Hits: <b>{{ player.hits }}</b> | AB: <b>{{ player.at_bats }}</b>
            </div>
          </li>
        </ul>
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
      return filtered.slice(0, 10);
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
        const res = await fetch(`/api/whos_hot/${days}`);
        this.hotPlayers = await res.json();
      } catch {
        this.hotPlayers = [];
      }
    },
    goToPlayer(player_id) {
      this.$router.push({ name: 'PlayerProfile', params: { player_id } });
    },
  },
  mounted() {
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
  z-index: 100;
}
.sidebar button {
  background: none;
  border: none;
  font-size: 1.1rem;
  color: #334155;
  padding: 10px 16px;
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
  margin-bottom: 24px;
  background: transparent;
  box-shadow: none;
  padding: 0;
}
.main-header h1 {
  color: #1e293b; /* Or your preferred light mode text color */
  background: transparent;
  padding: 0;
  margin: 0 0 0 24px;
}

/* Dark mode overrides */
body.dark .main-header {
  background: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin-bottom: 24px !important;
}
body.dark .main-header h1 {
  color: #7bbef9 !important;
  background: transparent !important;
  padding: 0 !important;
  margin: 0 0 0 24px !important;
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
}
.hot-controls button.active {
  background: #2563eb;
  color: #fff;
}
.hot-filters {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}
.hot-filters label {
  display: flex;
  align-items: center;
  gap: 8px;
}
.hot-filters select {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
}
.hot-list {
  list-style: none;
  padding: 0;
}
.hot-item {
  padding: 12px 0;
  border-bottom: 1px solid #e2e8f0;
}
.hot-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}
.team-logo-mini {
  width: 24px;
  height: 24px;
  object-fit: contain;
}
.hot-name {
  font-weight: 600;
  cursor: pointer;
}
.hot-name:hover {
  color: #2563eb;
}
.hot-team {
  color: #64748b;
}
.hot-league-div {
  color: #94a3b8;
  font-size: 0.9rem;
}
.hot-stats {
  font-size: 0.9rem;
  color: #64748b;
}
.no-results {
  color: #64748b;
  font-style: italic;
  text-align: center;
  margin: 16px 0;
}

/* ===== DARK MODE OVERRIDES ===== */
body.dark .home-container,
body.dark .card,
body.dark .hot-section,
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
body.dark .hot-item {
  border-bottom-color: #334155 !important;
}
body.dark .hot-name {
  color: #7bbef9 !important;
}
body.dark .hot-name:hover {
  color: #a7d2ff !important;
}
body.dark .hot-team,
body.dark .hot-league-div {
  color: #b6c6e3 !important;
}
body.dark .hot-stats {
  color: #e0eaff !important; /* Light blue-gray, easy to read */
}
body.dark .no-results {
  color: #b6c6e3 !important;
}
</style>
