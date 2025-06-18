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
/* Default light mode styles */
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

/* Dark mode styles */
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
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  transition: border-color 0.15s, box-shadow 0.15s;
  
  /* Remove all browser styling */
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  -webkit-background-clip: padding-box;
  background-clip: padding-box;
  
  /* Force light mode colors by default */
  background-color: #fff !important;
  color: #1e293b !important;
  -webkit-text-fill-color: #1e293b !important;
  -webkit-opacity: 1 !important;
}

/* Explicitly override for dark mode */
@media (prefers-color-scheme: dark) {
  .search-input {
    background-color: #232946 !important;
    color: #f9f9fc !important;
    -webkit-text-fill-color: #f9f9fc !important;
    border-color: #334155 !important;
  }
}

/* Light mode explicit override for mobile */
@media (prefers-color-scheme: light), (prefers-color-scheme: no-preference) {
  .search-input {
    background-color: #fff !important;
    color: #1e293b !important;
    -webkit-text-fill-color: #1e293b !important;
    border-color: #e2e8f0 !important;
  }
}

.search-input:focus {
  outline: none;
  box-shadow: 0 0 0 2px var(--search-focus-shadow);
}

/* Focus states for explicit theme modes */
@media (prefers-color-scheme: light), (prefers-color-scheme: no-preference) {
  .search-input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
  }
}

@media (prefers-color-scheme: dark) {
  .search-input:focus {
    border-color: #7bbef9 !important;
    box-shadow: 0 0 0 2px rgba(123, 190, 249, 0.3);
  }
}

.search-input::placeholder {
  opacity: 0.7;
}

/* Explicit placeholder colors for each theme */
@media (prefers-color-scheme: light), (prefers-color-scheme: no-preference) {
  .search-input::placeholder {
    color: #64748b !important;
  }
}

@media (prefers-color-scheme: dark) {
  .search-input::placeholder {
    color: #b6c6e3 !important;
  }
}

/* Enhanced mobile overrides with explicit colors */
@media screen and (max-width: 768px) {
  .search-input {
    font-size: 16px; /* Prevents zoom on iOS */
  }
  
  /* Light mode mobile */
  @media (prefers-color-scheme: light), (prefers-color-scheme: no-preference) {
    .search-input {
      background-color: #fff !important;
      color: #1e293b !important;
      -webkit-text-fill-color: #1e293b !important;
      border-color: #e2e8f0 !important;
    }
  }
  
  /* Dark mode mobile */
  @media (prefers-color-scheme: dark) {
    .search-input {
      background-color: #232946 !important;
      color: #f9f9fc !important;
      -webkit-text-fill-color: #f9f9fc !important;
      border-color: #334155 !important;
    }
  }
}

/* iOS Safari specific fixes */
@supports (-webkit-touch-callout: none) {
  .search-input {
    background-color: var(--search-bg) !important;
    color: var(--search-text) !important;
    -webkit-text-fill-color: var(--search-text) !important;
  }
}

/* Android Chrome specific fixes */
@media screen and (-webkit-min-device-pixel-ratio: 0) {
  .search-input {
    background-color: var(--search-bg) !important;
    color: var(--search-text) !important;
  }
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
}
</style>