(function () {
  const dataElement = document.getElementById('sim-quiz-data');
  if (!dataElement) return;

  const data = JSON.parse(dataElement.textContent);
  const questions = data.questions || [];
  let currentQuestion = 0;
  const answers = [];

  const questionText = document.getElementById('quiz-question-text');
  const optionsEl = document.getElementById('quiz-options');
  const feedbackPanel = document.getElementById('quiz-feedback-panel');
  const feedbackLabel = document.getElementById('quiz-feedback-label');
  const feedbackText = document.getElementById('quiz-feedback-text');
  const nextBtn = document.getElementById('quiz-next-btn');
  const progressFill = document.getElementById('quiz-progress-fill');
  const progressLabel = document.getElementById('quiz-progress-label');
  const questionPanel = document.getElementById('quiz-question-panel');
  const summaryPanel = document.getElementById('quiz-summary-panel');
  const finalScore = document.getElementById('quiz-final-score');
  const pointsEarned = document.getElementById('quiz-points-earned');
  const summaryFeedback = document.getElementById('quiz-summary-feedback');

  function updateProgress() {
    const total = questions.length || 1;
    const current = Math.min(currentQuestion + 1, total);
    progressFill.style.width = `${(current / total) * 100}%`;
    progressLabel.textContent = `${current} / ${total}`;
  }

  function renderQuestion() {
    const question = questions[currentQuestion];
    if (!question) return submitQuiz();

    feedbackPanel.classList.add('hidden');
    optionsEl.innerHTML = '';
    questionText.textContent = question.question;
    updateProgress();

    question.options.forEach((option, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'sim-quiz-option';
      button.textContent = `${String.fromCharCode(65 + index)}. ${option}`;
      button.addEventListener('click', () => handleAnswer(question, index, button));
      optionsEl.appendChild(button);
    });
  }

  function handleAnswer(question, selectedIndex, button) {
    optionsEl.querySelectorAll('button').forEach((btn) => { btn.disabled = true; });
    answers[currentQuestion] = selectedIndex;

    const isCorrect = selectedIndex === question.correct;
    if (isCorrect) {
      button.classList.add('correct');
      feedbackLabel.textContent = 'Correct';
      feedbackPanel.classList.add('is-success');
      feedbackPanel.classList.remove('is-error');
    } else {
      button.classList.add('incorrect');
      optionsEl.children[question.correct]?.classList.add('correct');
      feedbackLabel.textContent = 'Incorrect';
      feedbackPanel.classList.add('is-error');
      feedbackPanel.classList.remove('is-success');
    }

    feedbackText.textContent = question.explanation;
    feedbackPanel.classList.remove('hidden');
  }

  nextBtn.addEventListener('click', () => {
    currentQuestion += 1;
    if (currentQuestion >= questions.length) {
      submitQuiz();
    } else {
      renderQuestion();
    }
  });

  async function submitQuiz() {
    nextBtn.disabled = true;
    questionText.textContent = 'Submitting quiz...';

    try {
      const response = await fetch(data.submit_url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error('Quiz submit failed');
      showSummary(payload);
    } catch (error) {
      alert('Could not submit quiz. Please try again.');
      nextBtn.disabled = false;
      renderQuestion();
    }
  }

  function showSummary(payload) {
    questionPanel.classList.add('hidden');
    summaryPanel.classList.remove('hidden');
    finalScore.textContent = `${payload.score}%`;
    pointsEarned.textContent = `+${payload.points_earned} bonus points earned`;
    summaryFeedback.innerHTML = '';

    (payload.feedback || []).forEach((item, index) => {
      const card = document.createElement('div');
      card.className = `sim-panel ${item.correct ? 'is-success' : 'is-error'}`;
      card.innerHTML = `
        <div class="text-xs font-bold uppercase tracking-[0.18em] ${item.correct ? 'text-emerald-200' : 'text-rose-200'}">
          Question ${index + 1} ${item.correct ? '— Correct' : '— Incorrect'}
        </div>
        <p class="mt-2 font-semibold text-white">${item.question}</p>
        <p class="mt-2 text-sm text-slate-300">${item.explanation}</p>
      `;
      summaryFeedback.appendChild(card);
    });
  }

  renderQuestion();
})();
