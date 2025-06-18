<template>
  <section class="card standings-section">
    <h2 class="card-title">Live Division Standings</h2>
    <div v-if="loading" class="loading-message">Loading standings...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
      <div v-for="league in leagues" :key="league.id" class="league-section">
        <h3>{{ league.name }}</h3>
        <!-- Division Standings -->
        <div v-for="division in league.divisions" :key="division.id" class="division-section">
          <h4 class="division-name">{{ division.name }}</h4>
          
          <!-- Desktop Table -->
          <table class="standings-table desktop-table">
            <thead>
              <tr>
                <th class="team-col">Team</th>
                <th class="stat-col">W</th>
                <th class="stat-col">L</th>
                <th class="stat-col">Pct</th>
                <th class="stat-col">GB</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="team in division.teams" :key="team.id">
                <td class="team-col">
                  <div class="team-with-logo">
                    <img
                      :src="`https://www.mlbstatic.com/team-logos/${team.id}.svg`"
                      class="team-logo"
                      :alt="team.name"
                    />
                    <span class="team-name">{{ team.name }}</span>
                  </div>
                </td>
                <td class="stat-col">{{ team.wins }}</td>
                <td class="stat-col">{{ team.losses }}</td>
                <td class="stat-col">{{ (Number(team.pct) || 0).toFixed(3) }}</td>
                <td class="stat-col">{{ team.gb === '0.0' ? '-' : team.gb }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Mobile Cards -->
          <div class="mobile-cards">
            <div v-for="team in division.teams" :key="team.id" class="team-card">
              <div class="team-header">
                <img
                  :src="`https://www.mlbstatic.com/team-logos/${team.id}.svg`"
                  class="team-logo-mobile"
                  :alt="team.name"
                />
                <span class="team-name-mobile">{{ team.name }}</span>
              </div>
              <div class="team-stats">
                <div class="stat-item">
                  <span class="stat-label">W</span>
                  <span class="stat-value">{{ team.wins }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">L</span>
                  <span class="stat-value">{{ team.losses }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Pct</span>
                  <span class="stat-value">{{ (Number(team.pct) || 0).toFixed(3) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">GB</span>
                  <span class="stat-value">{{ team.gb === '0.0' ? '-' : team.gb }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Wild Card Standings -->
        <div v-if="league.wildCardTeams && league.wildCardTeams.length > 0" class="division-section">
          <h4 class="division-name">Wild Card</h4>
          
          <!-- Desktop Wild Card Table -->
          <table class="standings-table desktop-table">
            <thead>
              <tr>
                <th class="team-col">Team</th>
                <th class="stat-col">W</th>
                <th class="stat-col">L</th>
                <th class="stat-col">Pct</th>
                <th class="stat-col">GB</th>
              </tr>
            </thead>
            <tbody>
              <!-- Top 3 wild card teams -->
              <tr v-for="(team, index) in league.wildCardTeams.slice(0, 3)" :key="team.id">
                <td class="team-col">
                  <div class="team-with-logo">
                    <img
                      :src="`https://www.mlbstatic.com/team-logos/${team.id}.svg`"
                      class="team-logo"
                      :alt="team.name"
                    />
                    <span class="team-name">{{ team.name }}</span>
                  </div>
                </td>
                <td class="stat-col">{{ team.wins }}</td>
                <td class="stat-col">{{ team.losses }}</td>
                <td class="stat-col">{{ (Number(team.pct) || 0).toFixed(3) }}</td>
                <td class="stat-col">
                  {{
                    index === 2
                      ? '-'
                      : team.wildCardGB !== undefined
                        ? '+' + Math.abs(team.wildCardGB).toFixed(1)
                        : team.gb === '0.0'
                          ? '-'
                          : team.gb
                  }}
                </td>
              </tr>
              <!-- Divider after the third row -->
              <tr class="divider-row">
                <td colspan="5"><hr /></td>
              </tr>
              <!-- Remaining wild card teams (teams 4 and 5) -->
              <tr v-for="team in league.wildCardTeams.slice(3)" :key="team.id">
                <td class="team-col">
                  <div class="team-with-logo">
                    <img
                      :src="`https://www.mlbstatic.com/team-logos/${team.id}.svg`"
                      class="team-logo"
                      :alt="team.name"
                    />
                    <span class="team-name">{{ team.name }}</span>
                  </div>
                </td>
                <td class="stat-col">{{ team.wins }}</td>
                <td class="stat-col">{{ team.losses }}</td>
                <td class="stat-col">{{ (Number(team.pct) || 0).toFixed(3) }}</td>
                <td class="stat-col">
                  {{
                    team.wildCardGB !== undefined
                      ? team.wildCardGB.toFixed(1)
                      : team.gb === '0.0'
                        ? '-'
                        : team.gb
                  }}
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Mobile Wild Card Cards -->
          <div class="mobile-cards">
            <!-- Top 3 wild card teams -->
            <div v-for="(team, index) in league.wildCardTeams.slice(0, 3)" :key="team.id" class="team-card playoff-spot">
              <div class="team-header">
                <img
                  :src="`https://www.mlbstatic.com/team-logos/${team.id}.svg`"
                  class="team-logo-mobile"
                  :alt="team.name"
                />
                <span class="team-name-mobile">{{ team.name }}</span>
              </div>
              <div class="team-stats">
                <div class="stat-item">
                  <span class="stat-label">W</span>
                  <span class="stat-value">{{ team.wins }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">L</span>
                  <span class="stat-value">{{ team.losses }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Pct</span>
                  <span class="stat-value">{{ (Number(team.pct) || 0).toFixed(3) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">GB</span>
                  <span class="stat-value">
                    {{
                      index === 2
                        ? '-'
                        : team.wildCardGB !== undefined
                          ? '+' + Math.abs(team.wildCardGB).toFixed(1)
                          : team.gb === '0.0'
                            ? '-'
                            : team.gb
                    }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Playoff line divider -->
            <div class="playoff-line">
              <hr class="playoff-divider" />
              <span class="playoff-text">Playoff Line</span>
            </div>
            
            <!-- Remaining wild card teams -->
            <div v-for="team in league.wildCardTeams.slice(3)" :key="team.id" class="team-card">
              <div class="team-header">
                <img
                  :src="`https://www.mlbstatic.com/team-logos/${team.id}.svg`"
                  class="team-logo-mobile"
                  :alt="team.name"
                />
                <span class="team-name-mobile">{{ team.name }}</span>
              </div>
              <div class="team-stats">
                <div class="stat-item">
                  <span class="stat-label">W</span>
                  <span class="stat-value">{{ team.wins }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">L</span>
                  <span class="stat-value">{{ team.losses }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Pct</span>
                  <span class="stat-value">{{ (Number(team.pct) || 0).toFixed(3) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">GB</span>
                  <span class="stat-value">
                    {{
                      team.wildCardGB !== undefined
                        ? team.wildCardGB.toFixed(1)
                        : team.gb === '0.0'
                          ? '-'
                          : team.gb
                    }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
const DIVISION_NAMES = {
  201: "AL East",
  202: "AL Central",
  200: "AL West",
  204: "NL East",
  205: "NL Central",
  203: "NL West"
};

export default {
  data() {
    return {
      leagues: [],
      loading: true,
      error: null,
      leagueIds: [103, 104],
    };
  },
  async mounted() {
    try {
      const results = await Promise.all(
        this.leagueIds.map(id =>
          fetch(`https://statsapi.mlb.com/api/v1/standings?leagueId=${id}`)
            .then(res => res.json())
        )
      );
      this.leagues = results.map((data, idx) => {
        const leagueName = idx === 0 ? "American League" : "National League";
        const divisions = data.records.map(division => ({
          id: division.division.id,
          name: DIVISION_NAMES[division.division.id] || division.division.name,
          teams: division.teamRecords.map(team => ({
            id: team.team.id,
            name: team.team.name,
            wins: team.wins,
            losses: team.losses,
            pct: team.winningPercentage,
            gb: team.gamesBack
          }))
        }));

        // Collect all non-division-leading teams (wild card candidates)
        const wildCardCandidates = data.records.flatMap(
          division => division.teamRecords
            .filter(team => {
              const rank = team.divisionRank;
              return rank !== 1 && rank !== "1" && rank !== undefined;
            })
            .map(team => ({
              id: team.team.id,
              name: team.team.name,
              wins: team.wins,
              losses: team.losses,
              pct: team.winningPercentage,
              gb: team.gamesBack
            }))
        );

        // Sort by win percentage and take top 5
        const wildCardTeams = wildCardCandidates
          .sort((a, b) => (Number(b.pct) || 0) - (Number(a.pct) || 0))
          .slice(0, 5);

        // Calculate wild card games back (using third team as reference)
        if (wildCardTeams.length > 2) {
          const thirdTeamWins = wildCardTeams[2].wins;
          const thirdTeamLosses = wildCardTeams[2].losses;
          wildCardTeams.forEach((team) => {
            const winsDiff = thirdTeamWins - team.wins;
            const lossesDiff = team.losses - thirdTeamLosses;
            team.wildCardGB = (winsDiff + lossesDiff) / 2;
          });
        }

        return {
          id: this.leagueIds[idx],
          name: leagueName,
          divisions,
          wildCardTeams
        };
      });
    } catch (err) {
      this.error = err.message || "Failed to load standings";
    } finally {
      this.loading = false;
    }
  },
};
</script>

<style scoped>
.standings-section {
  background: var(--card-bg);
  border-radius: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 1rem;
  width: 100%;
  max-width: none;
  margin: 0;
  border-bottom: 1px solid var(--border-color);
  border-top: 1px solid var(--border-color);
  margin-bottom: 2rem;
}

@media (min-width: 768px) {
  .standings-section {
    padding: 2rem;
  }
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  letter-spacing: 0.01em;
  color: #ebcd54;
  text-align: center;
}

@media (min-width: 768px) {
  .card-title {
    font-size: 2rem;
  }
}

@media (prefers-color-scheme: dark) {
  .card-title {
    color: #d8bfd8;
  }
}

.loading-message {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  color: var(--text-color);
}

.league-section {
  margin-bottom: 2rem;
}

.league-section h3 {
  text-align: center;
  margin-bottom: 1rem;
  color: var(--title-color);
  font-size: 1.3rem;
}

@media (min-width: 768px) {
  .league-section h3 {
    font-size: 1.5rem;
  }
}

.division-section {
  margin-bottom: 2rem;
}

.division-name {
  text-align: center;
  margin: 1.2em 0 0.8em 0;
  font-size: 1.1rem;
  font-weight: bold;
  color: #2563eb;
  letter-spacing: 0.03em;
}

@media (min-width: 768px) {
  .division-name {
    font-size: 1.2rem;
  }
}

@media (prefers-color-scheme: dark) {
  .division-name {
    color: #93c5fd;
  }
}

/* Desktop Table Styles */
.desktop-table {
  display: none;
}

@media (min-width: 768px) {
  .desktop-table {
    display: table;
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
    border-collapse: collapse;
    background: var(--table-bg);
    table-layout: fixed;
  }
}

.standings-table th, .standings-table td {
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  text-align: center;
}

.team-col {
  width: 50%;
  text-align: left;
  padding-left: 1rem;
}

.team-with-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.team-logo {
  width: 24px;
  height: 24px;
  object-fit: contain;
  flex-shrink: 0;
}

.team-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-col {
  width: 12.5%;
}

.standings-table th {
  background: var(--th-bg);
  font-weight: bold;
}

.standings-table tr:nth-child(even) {
  background: var(--table-row-even);
}

.standings-table tr:hover {
  background: var(--table-row-hover);
}

.divider-row td {
  padding: 0;
  border: none;
}

.divider-row hr {
  margin: 0.5rem 0;
  border: 0;
  border-top: 2px dotted #888;
}

/* Mobile Card Styles */
.mobile-cards {
  display: block;
}

@media (min-width: 768px) {
  .mobile-cards {
    display: none;
  }
}

.team-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 0.75rem;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  min-height: 120px;
}

.team-card.playoff-spot {
  border-left: 4px solid #22c55e;
}

.team-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  min-height: 40px;
  flex-shrink: 0;
}

.team-logo-mobile {
  width: 32px;
  height: 32px;
  object-fit: contain;
  flex-shrink: 0;
}

.team-name-mobile {
  font-weight: 600;
  font-size: 1rem;
  color: var(--text-color);
  line-height: 1.2;
  word-wrap: break-word;
  hyphens: auto;
}

.team-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  flex: 1;
  align-content: start;
}

.stat-item {
  text-align: center;
  padding: 0.5rem;
  background: var(--table-row-even);
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 60px;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #666;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

@media (prefers-color-scheme: dark) {
  .stat-label {
    color: #999;
  }
}

.stat-value {
  display: block;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-color);
}

.playoff-line {
  position: relative;
  margin: 1rem 0;
  text-align: center;
}

.playoff-divider {
  border: 0;
  border-top: 2px dashed #ef4444;
  margin: 0;
}

.playoff-text {
  background: var(--card-bg);
  color: #ef4444;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0 0.5rem;
  position: absolute;
  top: -0.5rem;
  left: 50%;
  transform: translateX(-50%);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.error-message {
  color: #c0392b;
  font-weight: bold;
  text-align: center;
  padding: 2rem;
  background: #fef2f2;
  border-radius: 8px;
  border: 1px solid #fecaca;
}

@media (prefers-color-scheme: dark) {
  .error-message {
    background: #450a0a;
    border-color: #7f1d1d;
    color: #fca5a5;
  }
}

/* Improve touch targets for mobile */
@media (max-width: 767px) {
  .team-card {
    min-height: 44px;
    touch-action: manipulation;
  }
  
  .team-header {
    min-height: 32px;
  }
  
  .stat-item {
    min-height: 44px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
}

/* Handle very small screens */
@media (max-width: 320px) {
  .standings-section {
    padding: 0.75rem;
  }
  
  .card-title {
    font-size: 1.25rem;
  }
  
  .team-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }
  
  .stat-item {
    padding: 0.75rem 0.5rem;
  }
  
  .team-name-mobile {
    font-size: 0.9rem;
  }
}</style>