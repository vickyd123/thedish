<template>
  <div class="profile-container">
    <button class="back-btn" @click="$router.back()">← Back</button>
    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
    </div>
    <div v-else-if="splits.season && splits.last7 && splits.last30" class="profile-card">
      <div class="profile-header">
        <img
          v-if="teamLogoUrl"
          :src="teamLogoUrl"
          :alt="splits.season.team"
          class="team-logo"
        />
        <h2 class="player-title">
          {{ splits.season.player_name }}
        </h2>
      </div>
      <div class="splits-table-horizontal">
        <table>
          <thead>
            <tr>
              <th>Stat</th>
              <th v-for="key in splitKeys" :key="key">{{ splitLabels[key] }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stat in statRows" :key="stat.key">
              <td class="stat-label">{{ stat.label }}</td>
              <td v-for="key in splitKeys" :key="key" class="stat-value">
                {{ splits[key][stat.key] }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else-if="!loading && (!splits.season || !splits.last7 || !splits.last30)" class="no-stats">
      <p>No stats found for this player.</p>
    </div>
  </div>
</template>

<script>
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

export default {
  name: 'PlayerProfile',
  props: ['player_id'],
  data() {
    return {
      splits: {
        last7: null,
        last30: null,
        season: null
      },
      splitLabels: {
        last7: 'Last 7 Days',
        last30: 'Last 30 Days',
        season: 'This Season'
      },
      splitKeys: ['last7', 'last30', 'season'],
      statRows: [
        { key: 'avg', label: 'AVG' },
        { key: 'obp', label: 'OBP' },
        { key: 'hits', label: 'Hits' },
        { key: 'at_bats', label: 'At Bats' },
        { key: 'home_runs', label: 'Home Runs' },
        { key: 'rbi', label: 'RBI' },
        { key: 'walks', label: 'Walks' }
      ],
      loading: true, // Add loading state
      playerCache: {} // Add cache for player splits
    }
  },
  computed: {
    teamLogoUrl() {
      const teamId = TEAM_ID_MAP[this.splits.season?.team];
      return teamId
        ? `https://www.mlbstatic.com/team-logos/team-cap-on-light/${teamId}.svg`
        : null;
    }
  },
  methods: {
    async fetchAllSplits() {
      // Check cache first
      if (this.playerCache[this.player_id]) {
        this.splits = this.playerCache[this.player_id];
        this.loading = false;
        return;
      }
      this.loading = true;
      try {
        const [last7, last30, season] = await Promise.all([
          fetch(`/api/player_stats/${this.player_id}?days=7`).then(r => r.json()),
          fetch(`/api/player_stats/${this.player_id}?days=30`).then(r => r.json()),
          fetch(`/api/player_stats/${this.player_id}?days=season`).then(r => r.json())
        ]);
        this.splits = { last7, last30, season };
        this.playerCache[this.player_id] = this.splits; // Cache results
      } catch (err) {
        console.error('Error fetching player splits:', err);
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.fetchAllSplits();
  }
}
</script>

<style scoped>
.profile-container {
  max-width: 900px;
  margin: 32px auto;
  padding: 32px;
  background: #f9f9fc;
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.07), 0 1.5px 6px rgba(0,0,0,0.03);
  font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
}

.back-btn {
  background: #eee;
  border: none;
  padding: 10px 22px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  margin-bottom: 16px;
  transition: background 0.2s;
}
.back-btn:hover {
  background: #dbeafe;
}

.profile-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  width: 100%;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 20px;
}

.team-logo {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  background: #f1f5f9;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

.player-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1e293b;
  letter-spacing: 0.5px;
  margin: 0;
}

.splits-table-horizontal {
  margin-top: 28px;
  overflow-x: auto;
}

.splits-table-horizontal table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.splits-table-horizontal th,
.splits-table-horizontal td {
  padding: 12px 16px;
  text-align: center;
  font-size: 1.13rem;
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

.no-stats {
  text-align: center;
  color: #888;
  margin-top: 40px;
  font-size: 1.1rem;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0,0,0,0.1);
  border-radius: 50%;
  border-top-color: #2563eb;
  animation: spin 1s ease-in-out infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 900px) {
  .profile-card {
    padding: 14px;
  }
  .profile-header {
    flex-direction: column;
    gap: 12px;
  }
  .splits-table-horizontal table {
    min-width: 400px;
    font-size: 0.98rem;
  }
}
</style>
