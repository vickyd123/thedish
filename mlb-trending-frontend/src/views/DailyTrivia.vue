<template>
  <section class="card trivia-section" aria-live="polite">
    <h2>Daily Trivia</h2>
    <div v-if="questionLoading" class="loading-spinner">
      <div class="spinner"></div>
    </div>
    <div v-else-if="error">
      <em class="error">{{ error }}</em>
    </div>
    <div v-else-if="triviaQuestion">
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
    <div v-else>
      <em>No trivia available yet.</em>
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
      questionLoading: false,
    };
  },
  computed: {
    storageKey() {
      return this.triviaQuestion
        ? "trivia-answer-revealed-" + this.triviaQuestion.question
        : "";
    },
  },
  methods: {
    async fetchDailyTrivia() {
  this.questionLoading = true;
  
  // Format as YYYY-MM-DD in PDT
  const options = { timeZone: 'America/Los_Angeles', year: 'numeric', month: '2-digit', day: '2-digit' };
  const todayStr = new Date().toLocaleDateString('en-CA', options).replace(/-/g, '-');
  const cacheKey = `trivia-question-${todayStr}`;

  // Try to get cached question for today
  const cached = localStorage.getItem(cacheKey);
  if (cached) {
    this.triviaQuestion = JSON.parse(cached);
    if (this.storageKey)
      this.showAnswer = localStorage.getItem(this.storageKey) === "true";
    this.questionLoading = false;
    return;
  }

  try {
    const response = await fetch(`/api/daily_trivia?ts=${Date.now()}`);
    if (!response.ok) throw new Error("Failed to fetch trivia");
    this.triviaQuestion = await response.json();
    // Cache the question for today
    localStorage.setItem(cacheKey, JSON.stringify(this.triviaQuestion));
    // Check answer reveal state
    if (this.storageKey)
      this.showAnswer = localStorage.getItem(this.storageKey) === "true";
    this.questionLoading = false;
  } catch (err) {
    this.error = "Error loading trivia. Try again later.";
    this.questionLoading = false;
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
    this.fetchDailyTrivia();
  },
  watch: {
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
  background: #f8fafc;
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  padding: 2.5rem 1.5rem 2rem 1.5rem;
  max-width: 700px;
  margin: 2.5rem auto;
  border: 1px solid #e5e7eb;
  transition: background 0.3s, color 0.3s;
  width: 96%;
}
.trivia-section h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  letter-spacing: 0.01em;
  color: #32cd32;
  transition: color 0.3s;
}
@media (prefers-color-scheme: dark) {
  .trivia-section {
    background: #232b3b;
    color: #e0e6ed;
    border: 1px solid #2d3748;
    box-shadow: 0 4px 32px rgba(0, 0, 0, 0.28);
  }
  .trivia-section h2 {
    color: #32cd32;
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
.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100px;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color, #32cd32);
  animation: spin 1s ease-in-out infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
@media (prefers-color-scheme: dark) {
  .error {
    color: #ff7675;
  }
}
@media (max-width: 600px) {
  .trivia-section {
    padding: 1.5rem 1rem;
    margin: 1.5rem auto;
    width: 96%;
  }
  .trivia-section h2 {
    font-size: 1.6rem;
  }
  .blurred-answer {
    min-width: auto;
    width: 90%;
    padding: 0.8em;
    font-size: 1rem;
  }
  .answer-row {
    margin-top: 1.5rem;
  }
}
</style>
