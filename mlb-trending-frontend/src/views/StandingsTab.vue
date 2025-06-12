<template>
  <section class="card standings-section">
    <h2 class="card-title">Live Division Standings</h2>
    <div v-if="loading">Loading standings...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
      <div v-for="league in leagues" :key="league.id" class="league-section">
        <h3>{{ league.name }}</h3>
        <!-- Division Standings -->
        <div v-for="division in league.divisions" :key="division.id" class="division-section">
          <h4 class="division-name">{{ division.name }}</h4>
          <table class="standings-table">
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
                <td class="team-col">{{ team.name }}</td>
                <td class="stat-col">{{ team.wins }}</td>
                <td class="stat-col">{{ team.losses }}</td>
                <td class="stat-col">{{ (Number(team.pct) || 0).toFixed(3) }}</td>
                <td class="stat-col">{{ team.gb === '0.0' ? '-' : team.gb }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- Wild Card Standings -->
        <div v-if="league.wildCardTeams.length > 0" class="division-section">
          <h4 class="division-name">Wild Card</h4>
          <table class="standings-table">
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
    <td class="team-col">{{ team.name }}</td>
    <td class="stat-col">{{ team.wins }}</td>
    <td class="stat-col">{{ team.losses }}</td>
    <td class="stat-col">{{ (Number(team.pct) || 0).toFixed(3) }}</td>
    <td class="stat-col">
      {{ index === 2
          ? '-'
          : (team.wildCardGB !== undefined
              ? '+' + Math.abs(team.wildCardGB).toFixed(1)
              : team.gb === '0.0' ? '-' : team.gb)
      }}
    </td>
  </tr>
  <!-- Divider after the third row -->
  <tr class="divider-row">
    <td colspan="5"><hr></td>
  </tr>
  <!-- Remaining wild card teams (teams 4 and 5) -->
  <tr v-for="(team) in league.wildCardTeams.slice(3)" :key="team.id">
    <td class="team-col">{{ team.name }}</td>
    <td class="stat-col">{{ team.wins }}</td>
    <td class="stat-col">{{ team.losses }}</td>
    <td class="stat-col">{{ (Number(team.pct) || 0).toFixed(3) }}</td>
    <td class="stat-col">
      {{ team.wildCardGB !== undefined ? team.wildCardGB.toFixed(1) : team.gb === '0.0' ? '-' : team.gb }}
    </td>
  </tr>
</tbody>

          </table>
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
        const leagueName = idx === 0 ? 'American League' : 'National League';
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
              return rank !== 1 && rank !== '1' && rank !== undefined;
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
      this.error = err.message || 'Failed to load standings';
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
  padding: 2rem 1rem;
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
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  letter-spacing: 0.01em;
  color: #800080;
  text-align: center;
}
@media (prefers-color-scheme: dark) {
  .card-title {
    color: #d8bfd8;
  }
}
.league-section {
  margin-bottom: 2rem;
}
.league-section h3 {
  text-align: center;
  margin-bottom: 1rem;
  color: var(--title-color);
}
.division-section {
  margin-bottom: 2rem;
}
.division-name {
  text-align: center;
  margin: 1.2em 0 0.5em 0;
  font-size: 1.2em;
  font-weight: bold;
  color: #2563eb;
  letter-spacing: 0.03em;
}
@media (prefers-color-scheme: dark) {
  .division-name {
    color: #93c5fd;
  }
}
.standings-table {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  border-collapse: collapse;
  background: var(--table-bg);
  table-layout: fixed;
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

.error-message {
  color: #c0392b;
  font-weight: bold;
  text-align: center;
}
</style>
