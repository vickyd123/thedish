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
.search-section h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  letter-spacing: 0.01em;
  color: #4169e1; /* Royal Blue for light mode */
}
@media (prefers-color-scheme: dark) {
  .search-section h2 {
    color: #60a5fa; /* Sky Blue for dark mode */
  }
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
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  color: #1e293b;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.search-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}
.search-results {
  list-style: none;
  padding: 0;
  margin: 0;
}
.search-result-item {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  cursor: pointer;
  transition: background 0.15s;
}
.search-result-item:hover {
  background: #f1f5f9;
}
.search-team {
  color: #64748b;
}
.no-results {
  color: #64748b;
  font-style: italic;
}
/* Dark mode overrides (if not handled globally) */
@media (prefers-color-scheme: dark) {
  .search-input {
    background: #232946;
    color: #f9f9fc;
    border-color: #334155;
  }
  .search-input:focus {
    border-color: #7bbef9;
    box-shadow: 0 0 0 2px rgba(123, 190, 249, 0.3);
  }
  .search-result-item:hover {
    background: #334155;
  }
  .search-team {
    color: #b6c6e3;
  }
  .no-results {
    color: #b6c6e3;
  }
}
</style>
