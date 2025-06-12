<template>
  <section class="card batter-pitcher-card">
    <h2 class="card-title">Batter vs Pitcher (Since 2020) </h2>
    <div class="search-container">
      <input
        v-model="batter"
        class="search-input"
        placeholder="Batter name (e.g., Heliot Ramos)"
        autocomplete="off"
        aria-label="Batter name"
      />
      <input
        v-model="pitcher"
        class="search-input"
        placeholder="Pitcher name (e.g., Bryan Woo)"
        autocomplete="off"
        aria-label="Pitcher name"
      />
      <button @click.prevent="fetchStats" class="btn-primary">
        Lookup Stats
      </button>
    </div>
    <div v-if="loading" class="loading-indicator">
      <span>Loading matchup stats...</span>
    </div>
    <div v-if="error" class="error-message">
      <span>{{ error }}</span>
    </div>
    <div v-if="stats && stats.message" class="info-message">
      <span>{{ stats.message }}</span>
    </div>
    <div v-if="stats && stats.stats" class="results-card">
      <h3 class="results-title">
        Stats for {{ stats.batter }} vs {{ stats.pitcher }}
      </h3>
      <table class="stats-table">
        <thead>
          <tr>
            <th>PA</th>
            <th>AB</th>
            <th>H</th>
            <th>BB</th>
            <th>HBP</th>
            <th>AVG</th>
            <th>OBP</th>
            <th>SLG</th>
            <th>OPS</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{{ stats.stats.PA }}</td>
            <td>{{ stats.stats.AB }}</td>
            <td>{{ stats.stats.H }}</td>
            <td>{{ stats.stats.BB }}</td>
            <td>{{ stats.stats.HBP }}</td>
            <td>{{ stats.stats.AVG }}</td>
            <td>{{ stats.stats.OBP }}</td>
            <td>{{ stats.stats.SLG }}</td>
            <td>{{ stats.stats.OPS }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script>
export default {
  data() {
    return {
      batter: '',
      pitcher: '',
      stats: null,
      error: null,
      loading: false
    }
  },
  methods: {
    async fetchStats() {
      this.stats = null;
      this.error = null;
      this.loading = true;
      const timestamp = Date.now();
      try {
        const response = await fetch(
          `/api/batter-vs-pitcher?batter=${encodeURIComponent(this.batter)}&pitcher=${encodeURIComponent(this.pitcher)}&_=${timestamp}`,
          {
            headers: {
              'Cache-Control': 'no-cache, no-store, must-revalidate',
              'Pragma': 'no-cache',
              'Expires': '0'
            }
          }
        );
        const data = await response.json();
        if (data.error) {
          this.error = data.error;
        } else {
          this.stats = data;
        }
      } catch (err) {
        this.error = err.message || 'Failed to fetch stats';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.batter-pitcher-card {
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
  .batter-pitcher-card {
    padding: 2rem;
  }
}
.card-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  letter-spacing: 0.01em;
  color: #ffd700; /* Gold for light mode */
  text-align: center;
}
@media (prefers-color-scheme: dark) {
  .card-title {
    color: #ffd700; /* Gold for dark mode */
  }
}
.search-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
@media (min-width: 600px) {
  .search-container {
    flex-direction: row;
    align-items: flex-end;
    max-width: 800px;
    margin: 0 auto 1.5rem;
  }
  .search-input {
    flex: 1;
  }
}
.search-input {
  box-sizing: border-box;
  width: 100%;
  padding: 12px 16px;
  font-size: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--input-bg);
  color: var(--text-color);
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}
.btn-primary {
  padding: 12px 24px;
  background: var(--primary-color);
  color: var(--text-color);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: background 0.15s;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.btn-primary:hover {
  background: var(--primary-hover);
}
.loading-indicator,
.error-message,
.info-message {
  margin: 1rem 0;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}
.loading-indicator {
  background: var(--loading-bg);
  color: var(--loading-text);
}
.error-message {
  background: var(--error-bg);
  color: var(--error-text);
}
.info-message {
  background: var(--info-bg);
  color: var(--info-text);
}
.results-card {
  background: var(--card-bg);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  padding: 1.5rem;
  margin: 2rem auto;
  border: 1px solid var(--border-color);
  max-width: 800px;
}
.results-title {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--title-color);
  text-align: center;
}
.stats-table {
  width: 100%;
  border-collapse: collapse;
  margin: 0 auto;
  background: var(--table-bg);
}
.stats-table th, .stats-table td {
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  text-align: center;
}
.stats-table th {
  background: var(--th-bg);
  font-weight: bold;
}
.stats-table tr:nth-child(even) {
  background: var(--table-row-even);
}
.stats-table tr:hover {
  background: var(--table-row-hover);
}
</style>
