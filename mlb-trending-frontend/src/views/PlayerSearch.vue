<template>
  <section class="card search-section">
    <h2>Search Player</h2>
    <div class="search-container">
      <input
        v-model="searchName"
        @input="searchPlayers"
        class="search-input"
        placeholder="Type player name..."
        autocomplete="off"
        aria-label="Search player by name"
      />
    </div>
    <ul v-if="searchResults.length" class="search-results">
      <li
        v-for="player in searchResults"
        :key="player.player_id"
        @click="goToPlayer(player.player_id)"
        class="search-result-item"
      >
        {{ player.player_name }}
        <span class="search-team">({{ player.team }})</span>
      </li>
    </ul>
    <p v-else-if="searchName.length > 1 && !searchResults.length" class="no-results">
      No players found.
    </p>
  </section>
</template>

<script>
export default {
  name: 'PlayerSearch',
  data() {
    return {
      searchName: '',
      searchResults: [],
      searchTimeout: null,
    }
  },
  methods: {
    searchPlayers() {
      clearTimeout(this.searchTimeout);
      if (this.searchName.length < 2) {
        this.searchResults = [];
        return;
      }
      this.searchTimeout = setTimeout(async () => {
        try {
          const res = await fetch(`/api/search_player?name=${encodeURIComponent(this.searchName)}`);
          this.searchResults = await res.json();
        } catch {
          this.searchResults = [];
        }
      }, 300);
    },
    goToPlayer(player_id) {
      this.$router.push({ name: 'PlayerProfile', params: { player_id } });
    }
  }
}
</script>

<style scoped>
/* CSS Custom Properties for better theme handling */
.search-section {
  --search-bg: #fff;
  --search-text: #1e293b;
  --search-border: #e2e8f0;
  --search-focus-border: #2563eb;
  --search-focus-shadow: rgba(37, 99, 235, 0.2);
  --search-hover-bg: #f1f5f9;
  --search-team-color: #64748b;
  --search-title-color: #4169e1;
}

@media (prefers-color-scheme: dark) {
  .search-section {
    --search-bg: #232946;
    --search-text: #f9f9fc;
    --search-border: #334155;
    --search-focus-border: #7bbef9;
    --search-focus-shadow: rgba(123, 190, 249, 0.3);
    --search-hover-bg: #334155;
    --search-team-color: #b6c6e3;
    --search-title-color: #60a5fa;
  }
}

.search-section h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  letter-spacing: 0.01em;
  color: var(--search-title-color);
}

.search-container {
  margin-bottom: 16px;
}

.search-input {
  box-sizing: border-box;
  width: 100%;
  max-width: 100%;
  padding: 12px 16px;
  font-size: 1rem;
  border: 1px solid var(--search-border);
  border-radius: 8px;
  background: var(--search-bg) !important;
  color: var(--search-text) !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  transition: border-color 0.15s, box-shadow 0.15s;
}

.search-input:focus {
  outline: none;
  border-color: var(--search-focus-border);
  box-shadow: 0 0 0 2px var(--search-focus-shadow);
}

.search-input::placeholder {
  color: var(--search-team-color);
  opacity: 0.7;
}

.search-results {
  list-style: none;
  padding: 0;
  margin: 0;
}

.search-result-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--search-border);
  cursor: pointer;
  transition: background 0.15s;
  color: var(--search-text);
}

.search-result-item:hover {
  background: var(--search-hover-bg);
}

.search-team {
  color: var(--search-team-color);
}

.no-results {
  color: var(--search-team-color);
  font-style: italic;
}</style>