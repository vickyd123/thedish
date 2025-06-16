<template>
  <section class="bvp-card">
    <h2 class="bvp-title">
      <span>Batter vs Pitcher <small>(Since 2020)</small></span>
    </h2>
    <div class="bvp-search">
      <input
        v-model="batter"
        class="bvp-input"
        placeholder="Batter name (e.g., Heliot Ramos)"
        autocomplete="off"
      />
      <input
        v-model="pitcher"
        class="bvp-input"
        placeholder="Pitcher name (e.g., Bryan Woo)"
        autocomplete="off"
      />
      <button @click.prevent="fetchStats" class="bvp-btn">
        <i class="fa fa-search"></i> Lookup Stats
      </button>
    </div>
    <div v-if="loading" class="bvp-loading">
      <span class="spinner"></span> Loading matchup stats...
    </div>
    <div v-if="error" class="bvp-error">
      <i class="fa fa-exclamation-triangle"></i> {{ error }}
    </div>
    <div v-if="stats && stats.stats" class="bvp-results">
      <div class="bvp-players">
        <div class="bvp-player">
          <img :src="getPlayerImage(stats.batter)" class="bvp-img" alt="Batter" />
          <div>{{ stats.batter }}</div>
        </div>
        <div class="bvp-vs">vs</div>
        <div class="bvp-player">
          <img :src="getPlayerImage(stats.pitcher)" class="bvp-img" alt="Pitcher" />
          <div>{{ stats.pitcher }}</div>
        </div>
      </div>
      <table class="bvp-table">
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
            <td :class="{'highlight': stats.stats.H > 2}">{{ stats.stats.H }}</td>
            <td>{{ stats.stats.BB }}</td>
            <td>{{ stats.stats.HBP }}</td>
            <td :class="{'highlight': stats.stats.AVG > 0.3}">{{ stats.stats.AVG }}</td>
            <td>{{ stats.stats.OBP }}</td>
            <td>{{ stats.stats.SLG }}</td>
            <td :class="{'highlight': stats.stats.OPS > 1.0}">{{ stats.stats.OPS }}</td>
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
      batter: "",
      pitcher: "",
      stats: null,
      error: null,
      loading: false
    };
  },
  methods: {
    async fetchStats() {
      this.stats = null;
      this.error = null;
      this.loading = true;
      try {
        const response = await fetch(
          `/api/batter-vs-pitcher?batter=${encodeURIComponent(this.batter)}&pitcher=${encodeURIComponent(this.pitcher)}`
        );
        const data = await response.json();
        if (data.error) {
          this.error = data.error;
        } else {
          this.stats = data;
        }
      } catch (err) {
        this.error = err.message || "Failed to fetch stats";
      } finally {
        this.loading = false;
      }
    },
    getPlayerImage(name) {
      // Optionally replace with actual player images or team logos
      return "https://ui-avatars.com/api/?name=" + encodeURIComponent(name) + "&background=0D8ABC&color=fff";
    }
  }
};
</script>

<style scoped>
.bvp-card {
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  padding: 2rem 1rem;
  max-width: 1000px;
  margin: 2rem auto;
  border: 1px solid var(--card-border);
}
.bvp-title {
  font-size: 2.2rem;
  color: #1dcfcc;
  text-align: center;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5em;
}
.bvp-title small {
  font-size: 1rem;
  color: var(--subtext);
}
.moon-icon {
  font-size: 1.5rem;
}
.bvp-search {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.bvp-input {
  padding: 12px 16px;
  font-size: 1rem;
  border-radius: 8px;
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text);
  min-width: 250px;
}
.bvp-btn {
  background: var(--highlight);
  color: var(--highlight-text);
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  align-items: center;
  gap: 0.5em;
}
.bvp-btn:hover {
  background: var(--highlight-hover);
}
.bvp-loading {
  text-align: center;
  color: var(--highlight);
  margin-bottom: 1rem;
}
.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid var(--highlight);
  border-top: 2px solid var(--card-bg);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 0.5em;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.bvp-error {
  background: var(--error-bg);
  color: var(--error-text);
  border-radius: 8px;
  text-align: center;
  margin-bottom: 1rem;
  padding: 1em;
}
.bvp-results {
  background: var(--results-bg);
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.bvp-players {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2em;
  margin-bottom: 1.5rem;
}
.bvp-player {
  text-align: center;
}
.bvp-img {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  margin-bottom: 0.5em;
  background: var(--input-bg);
  object-fit: cover;
}
.bvp-vs {
  font-size: 1.5rem;
  color: var(--highlight);
  font-weight: bold;
}
.bvp-table {
  width: 100%;
  border-collapse: collapse;
  margin: 0 auto;
  background: var(--table-bg);
}
.bvp-table th, .bvp-table td {
  padding: 0.75rem;
  border: 1px solid var(--table-border);
  text-align: center;
  font-size: 1.1rem;
}
.bvp-table th {
  background: var(--table-header-bg);
  color: var(--highlight);
  font-weight: bold;
}
.bvp-table td.highlight {
  background: var(--highlight);
  color: var(--highlight-text);
  font-weight: bold;
  border-radius: 4px;
}
</style>
