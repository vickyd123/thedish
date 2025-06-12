<template>
  <section class="card digest-section">
    <h2>Daily Digest</h2>
    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
    </div>
    <div v-else-if="error">
      <em class="error">{{ error }}</em>
    </div>
    <div v-else-if="digest" v-html="formattedDigest"></div>
    <div v-else>
      <em>No digest available yet.</em>
    </div>
  </section>
</template>

<script>
export default {
  name: "DailyDigest",
  data() {
    return {
      digest: "",
      loading: true,
      error: "",
    };
  },
  computed: {
    formattedDigest() {
      if (!this.digest) return "";
      // Escape HTML to prevent XSS
      let escaped = this.digest
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
      // Bold section headers
      escaped = escaped.replace(
        /American League Highlights:/g,
        "<strong>American League Highlights:</strong>"
      );
      escaped = escaped.replace(
        /National League Highlights:/g,
        "<strong>National League Highlights:</strong>"
      );
      // Insert divider before National League section
      escaped = escaped.replace(
        /<strong>National League Highlights:<\/strong>/,
        "<hr class='digest-divider'><strong>National League Highlights:</strong>"
      );
      // Split by single newline for each line/game
      const lines = escaped.split('\n');
      // Wrap each non-empty line in <p> for spacing
      return lines
        .map(line => {
          if (!line.trim()) return '';
          return `<p>${line.trim()}</p>`;
        })
        .join('');
    }
  },
  methods: {
    async fetchDigest() {
      // Use a key based on the current date (resets daily)
      const today = new Date().toISOString().split('T')[0];
      const cacheKey = `daily-digest-${today}`;

      // Try to get cached digest for today
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        this.digest = cached;
        this.loading = false;
        return;
      }

      // Otherwise, fetch from API
      this.loading = true;
      try {
        const response = await fetch("/api/daily_digest");
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.digest || "Failed to load daily digest.");
        }
        const data = await response.json();
        this.digest = data.digest;
        // Cache the digest for today
        localStorage.setItem(cacheKey, data.digest);
        this.loading = false;
      } catch (err) {
        this.error = err.message;
        this.loading = false;
      }
    },
  },
  mounted() {
    this.fetchDigest();
  },
};
</script>

<style scoped>
.digest-section {
  text-align: center;
  margin: 2.5rem auto;
  max-width: 700px;
  background: #f8fafc;
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  padding: 2.5rem 1.5rem 2rem 1.5rem;
  color: #1e293b;
  border: 1px solid #e5e7eb;
  transition: background 0.3s, color 0.3s;
}
.digest-section h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  letter-spacing: 0.01em;
  color: #e53935 !important;
  transition: color 0.3s;
}
.digest-section p {
  margin: 0.9em 0;
  text-align: left;
  color: inherit;
}
.digest-section strong {
  font-size: 1.08em;
  color: #2563eb;
  letter-spacing: 0.01em;
  transition: color 0.3s;
}
.digest-divider {
  border: none;
  border-top: 2px solid #bcd;
  margin: 2em 0 1.5em 0;
  width: 70%;
  opacity: 0.6;
  transition: border-color 0.3s;
}
.error {
  color: #c0392b;
  font-weight: bold;
}
.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100px;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0,0,0,0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
@media (prefers-color-scheme: dark) {
  body {
    background: #1a2232;
  }
  .digest-section {
    background: #232b3b;
    color: #e0e6ed;
    border: 1px solid #2d3748;
    box-shadow: 0 4px 32px rgba(0,0,0,0.28);
  }
  .digest-section h2 {
    color: #e53935 !important;
  }
  .digest-section p {
    color: #e0e6ed;
  }
  .digest-section strong {
    color: #60a5fa;
  }
  .digest-divider {
    border-top: 2px solid #334155;
  }
  .error {
    color: #ff7675;
  }
}
</style>
