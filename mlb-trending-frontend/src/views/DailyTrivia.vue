<template>
  <section class="card trivia-section" aria-live="polite">
    <h2>Daily Trivia</h2>
    <div v-if="triviaQuestion">
      <p>{{ triviaQuestion.question }}</p>
      <div class="answer-row">
        <span
          class="blurred-answer"
          :class="{ revealed: showAnswer }"
          @click="revealAnswer"
          tabindex="0"
          @keyup.enter="revealAnswer"
          title="Click to reveal the answer"
        >
          <template v-if="showAnswer">
            {{ triviaQuestion.answer }}
          </template>
          <template v-else>
            <span class="placeholder">
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            </span>
          </template>
        </span>
      </div>
      <small v-if="!showAnswer" class="hint">(Click to reveal the answer)</small>
    </div>
    <div v-else-if="error">
      <em class="error">{{ error }}</em>
    </div>
    <div v-else>
      <em>Loading question...</em>
    </div>
  </section>
</template>

<script>
export default {
  name: "DailyTrivia",
  data() {
    return {
      triviaQuestion: null,
      showAnswer: false,
      error: null,
    };
  },
  computed: {
    storageKey() {
      // Use a unique key per question (by question text, or use a question ID if available)
      return this.triviaQuestion
        ? "trivia-answer-revealed-" + this.triviaQuestion.question
        : "";
    },
  },
  methods: {
    async fetchDailyTrivia() {
      // Use a key based on the current date (resets daily)
      const today = new Date().toISOString().split('T')[0];
      const cacheKey = `trivia-question-${today}`;

      // Try to get cached question for today
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        this.triviaQuestion = JSON.parse(cached);
        if (this.storageKey)
          this.showAnswer = localStorage.getItem(this.storageKey) === "true";
        return;
      }

      try {
        const response = await fetch("/api/daily_trivia");
        if (!response.ok) throw new Error("Failed to fetch trivia");
        this.triviaQuestion = await response.json();
        // Cache the question for today
        localStorage.setItem(cacheKey, JSON.stringify(this.triviaQuestion));
        // Check answer reveal state
        if (this.storageKey)
          this.showAnswer = localStorage.getItem(this.storageKey) === "true";
      } catch (err) {
        this.error = "Error loading trivia. Try again later.";
        console.error(err);
      }
    },
    revealAnswer() {
      if (!this.showAnswer && this.storageKey) {
        this.showAnswer = true;
        localStorage.setItem(this.storageKey, "true");
      }
    },
  },
  mounted() {
  const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
  console.log(yesterday)
  localStorage.removeItem(`trivia-question-${yesterday}`);
  this.fetchDailyTrivia();
  },
  watch: {
    // If the question changes, re-check localStorage
    triviaQuestion() {
      if (this.storageKey)
        this.showAnswer = localStorage.getItem(this.storageKey) === "true";
    },
  },
};
</script>

<style scoped>
.trivia-section {
  text-align: center;
}
.trivia-section h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  letter-spacing: 0.01em;
  color: #32cd32; /* Bright green */
  transition: color 0.3s;
}
@media (prefers-color-scheme: dark) {
  .trivia-section h2 {
    color: #32cd32; /* Brighter green for dark mode */
  }
}
.answer-row {
  margin-top: 2rem;
  margin-bottom: 0.5rem;
}
.blurred-answer {
  display: inline-block;
  min-width: 220px;
  height: 1.6em;
  filter: blur(8px);
  cursor: pointer;
  user-select: none;
  transition: filter 0.3s, background-color 0.3s;
  color: #0b3d0b;
  background: #d0f0d0;
  padding: 0.3em 1em;
  border-radius: 6px;
  font-weight: bold;
  outline: none;
  font-size: 1.2em;
  letter-spacing: 0.03em;
  text-align: center;
  vertical-align: middle;
}
.blurred-answer:focus {
  outline: 2px solid #1976d2;
}
.blurred-answer.revealed {
  filter: none;
  cursor: default;
  user-select: text;
  background: #a8d5a8;
  color: #004d00;
}
.placeholder {
  display: inline-block;
  width: 100%;
  height: 1.2em;
}
.hint {
  color: #888;
  font-size: 0.95em;
  display: block;
  margin-top: 0.3em;
}
.error {
  color: #c0392b;
  font-weight: bold;
}
</style>
