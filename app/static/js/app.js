const toastEl = document.getElementById('app-toast');
const toastMessage = document.getElementById('toast-message');

function showToast(message, type = 'dark') {
  const toast = bootstrap.Toast.getOrCreateInstance(toastEl);
  toastEl.className = `toast align-items-center text-bg-${type} border-0`;
  toastMessage.textContent = message;
  toast.show();
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail || 'Request failed.';
    throw new Error(detail);
  }
  return data;
}

function setLoading(button, isLoading) {
  const spinner = button.querySelector('.spinner-border');
  const label = button.querySelector('.button-text');
  if (!spinner || !label) return;
  spinner.classList.toggle('d-none', !isLoading);
  label.style.opacity = isLoading ? '0.7' : '1';
  button.disabled = isLoading;
}

function renderTaskList(tasks, compact = false) {
  const container = document.getElementById('task-list') || document.getElementById('dashboard-task-list');
  if (!container) return;

  if (!tasks.length) {
    container.innerHTML = `
      <div class="empty-state">
        <i class="bi bi-list-task fs-1 text-muted"></i>
        <p class="mt-3 mb-0">No tasks match this filter.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = tasks.map((task) => `
    <div class="task-item ${compact ? 'compact' : ''}">
      <div class="task-header">
        <h4>${task.title}</h4>
        <span class="badge-status ${task.status}">${task.status}</span>
      </div>
      <p class="mb-2 text-secondary">${task.description}</p>
      <div class="task-meta">
        ${task.due_date ? `<span>Due: ${task.due_date}</span>` : '<span>No due date</span>'}
      </div>
      <div class="task-actions">
        ${task.status !== 'completed' ? `<button class="btn btn-sm btn-success complete-task" data-id="${task.id}">Complete</button>` : ''}
        <button class="btn btn-sm btn-outline-danger delete-task" data-id="${task.id}">Delete</button>
      </div>
    </div>
  `).join('');
}

async function loadTasks(filter = 'all') {
  const tasks = await apiRequest(`/api/tasks?status=${filter}`);
  renderTaskList(tasks, !document.getElementById('dashboard-task-list'));
  if (document.getElementById('dashboard-task-list')) {
    const pending = tasks.filter((task) => task.status === 'pending').length;
    const completed = tasks.filter((task) => task.status === 'completed').length;
    document.getElementById('stat-total-tasks').textContent = tasks.length;
    document.getElementById('stat-pending-tasks').textContent = pending;
    document.getElementById('stat-completed-tasks').textContent = completed;
  }
}

async function loadPlans() {
  const plans = await apiRequest('/api/plans');
  const count = plans.length;
  const statNode = document.getElementById('stat-saved-plans');
  if (statNode) statNode.textContent = count;

  const dashboardList = document.getElementById('dashboard-plan-list');
  if (dashboardList) {
    if (!plans.length) {
      dashboardList.innerHTML = '<div class="empty-state"><p class="mb-0">No saved plans yet.</p></div>';
      return;
    }
    dashboardList.innerHTML = plans.slice(0, 3).map((plan) => `
      <div class="list-group-item px-0 py-2 border-0">
        <h6 class="mb-1">${plan.subject}</h6>
        <small class="text-muted">${plan.days} days • ${plan.daily_minutes} min/day</small>
      </div>
    `).join('');
  }

  const savedPlansList = document.getElementById('saved-plans-list');
  if (savedPlansList) {
    if (!plans.length) {
      savedPlansList.innerHTML = '<div class="col-12 empty-state"><p class="mb-0">No saved study plans yet.</p></div>';
      return;
    }

    savedPlansList.innerHTML = plans.map((plan) => `
      <div class="col-md-6">
        <div class="plan-card">
          <h5>${plan.subject}</h5>
          <p class="text-muted mb-2">${plan.days} days • ${plan.level} • ${plan.daily_minutes} min daily</p>
          <div>
            ${plan.plan.map((day) => `
              <div class="plan-day">
                <h6>Day ${day.day}: ${day.focus}</h6>
                <ul class="mb-0 ps-3">
                  ${day.tasks.map((task) => `<li>${task}</li>`).join('')}
                </ul>
                <small class="text-muted">${day.minutes} minutes</small>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `).join('');
  }
}

async function initDashboard() {
  const tasks = await apiRequest('/api/tasks');
  renderTaskList(tasks.slice(0, 4), true);
  const pending = tasks.filter((task) => task.status === 'pending').length;
  const completed = tasks.filter((task) => task.status === 'completed').length;
  document.getElementById('stat-total-tasks').textContent = tasks.length;
  document.getElementById('stat-pending-tasks').textContent = pending;
  document.getElementById('stat-completed-tasks').textContent = completed;
  const plans = await apiRequest('/api/plans');
  document.getElementById('stat-saved-plans').textContent = plans.length;
  const dashboardPlanList = document.getElementById('dashboard-plan-list');
  if (dashboardPlanList) {
    if (!plans.length) {
      dashboardPlanList.innerHTML = '<div class="empty-state"><p class="mb-0">No saved plans yet.</p></div>';
      return;
    }
    dashboardPlanList.innerHTML = plans.slice(0, 3).map((plan) => `
      <div class="list-group-item px-0 py-2 border-0">
        <h6 class="mb-1">${plan.subject}</h6>
        <small class="text-muted">${plan.days} days • ${plan.daily_minutes} min/day</small>
      </div>
    `).join('');
  }
}

async function initPlansPage() {
  const form = document.getElementById('plan-form');
  const output = document.getElementById('plan-output');
  const saveBtn = document.getElementById('save-plan-btn');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    const payload = {
      subject: document.getElementById('plan-subject').value,
      days: Number(document.getElementById('plan-days').value),
      level: document.getElementById('plan-level').value,
      daily_minutes: Number(document.getElementById('plan-minutes').value),
      notes: document.getElementById('plan-notes').value,
    };

    setLoading(button, true);
    try {
      const plan = await apiRequest('/api/plans/generate', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      currentPlan = plan;
      output.classList.remove('empty-state');
      output.innerHTML = `
        <div class="w-100">
          <h4>${plan.subject}</h4>
          <p class="text-muted">${plan.days} days • ${plan.level} • ${plan.daily_minutes} minutes/day</p>
          ${plan.plan.map((day) => `
            <div class="plan-day">
              <h5>Day ${day.day}: ${day.focus}</h5>
              <ul class="ps-3 mb-2">
                ${day.tasks.map((task) => `<li>${task}</li>`).join('')}
              </ul>
              <small class="text-muted">${day.minutes} minutes</small>
            </div>
          `).join('')}
        </div>
      `;
      saveBtn.classList.remove('d-none');
      showToast('Study plan generated successfully.', 'success');
    } catch (error) {
      showToast(error.message, 'danger');
      output.classList.add('empty-state');
      output.innerHTML = '<i class="bi bi-exclamation-circle fs-1 text-muted"></i><p class="mt-3 mb-0">Unable to generate a study plan right now.</p>';
    } finally {
      setLoading(button, false);
    }
  });

  saveBtn.addEventListener('click', async () => {
    if (!window.currentPlan) {
      showToast('Generate a plan before saving it.', 'warning');
      return;
    }
    try {
      await apiRequest('/api/plans', {
        method: 'POST',
        body: JSON.stringify(window.currentPlan),
      });
      showToast('Plan saved to your library.', 'success');
      await loadPlans();
    } catch (error) {
      showToast(error.message, 'danger');
    }
  });

  loadPlans();
}

async function initSummarizerPage() {
  const form = document.getElementById('summary-form');
  const output = document.getElementById('summary-output');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    const payload = {
      text: document.getElementById('summary-text').value,
      style: document.getElementById('summary-style').value,
    };

    setLoading(button, true);
    try {
      const response = await apiRequest('/api/summaries/generate', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      output.classList.remove('empty-state');
      output.innerHTML = `<div class="summary-box">${response.summary.replace(/\n/g, '<br>')}</div>`;
      showToast('Summary generated successfully.', 'success');
    } catch (error) {
      showToast(error.message, 'danger');
      output.classList.add('empty-state');
      output.innerHTML = '<i class="bi bi-exclamation-circle fs-1 text-muted"></i><p class="mt-3 mb-0">The summary could not be generated.</p>';
    } finally {
      setLoading(button, false);
    }
  });
}

async function initQuizPage() {
  const form = document.getElementById('quiz-form');
  const output = document.getElementById('quiz-output');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    const payload = {
      material: document.getElementById('quiz-material').value,
      question_count: Number(document.getElementById('quiz-count').value),
    };

    setLoading(button, true);
    try {
      const response = await apiRequest('/api/quizzes/generate', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      output.innerHTML = '';
      response.questions.forEach((question, index) => {
        const questionCard = document.createElement('div');
        questionCard.className = 'quiz-card';
        questionCard.innerHTML = `
          <h5>Question ${index + 1}</h5>
          <p>${question.question}</p>
          <div class="options-group">
            ${question.options.map((option) => `
              <button type="button" class="option-btn" data-question-index="${index}" data-option="${option}">${option}</button>
            `).join('')}
          </div>
          <div class="mt-3 d-none answer-review">
            <strong>Correct answer:</strong> ${question.correct_answer}<br>
            <small>${question.explanation}</small>
          </div>
        `;
        output.appendChild(questionCard);
      });

      const submitButton = document.createElement('button');
      submitButton.type = 'button';
      submitButton.className = 'btn btn-primary mt-3';
      submitButton.textContent = 'Submit answers';
      submitButton.addEventListener('click', () => {
        const cards = [...document.querySelectorAll('.quiz-card')];
        cards.forEach((card, cardIndex) => {
          const selected = card.querySelector('.option-btn.selected');
          const correct = response.questions[cardIndex].correct_answer;
          card.querySelectorAll('.option-btn').forEach((button) => {
            button.disabled = true;
            if (button.dataset.option === correct) button.classList.add('correct');
            if (selected && button.dataset.option === selected.dataset.option && selected.dataset.option !== correct) {
              button.classList.add('incorrect');
            }
          });
          const reviewBox = card.querySelector('.answer-review');
          reviewBox.classList.remove('d-none');
        });

        const total = response.questions.length;
        const correctCount = response.questions.filter((question, index) => {
          const selected = document.querySelector(`.option-btn.selected[data-question-index="${index}"]`);
          return selected && selected.dataset.option === question.correct_answer;
        }).length;

        const scoreBox = document.createElement('div');
        scoreBox.className = 'alert alert-info mt-3';
        scoreBox.innerHTML = `<strong>Your score:</strong> ${correctCount}/${total}`;
        output.appendChild(scoreBox);
      });
      output.appendChild(submitButton);

      document.querySelectorAll('.option-btn').forEach((button) => {
        button.addEventListener('click', () => {
          const card = button.closest('.quiz-card');
          const allButtons = card.querySelectorAll('.option-btn');
          allButtons.forEach((item) => item.classList.remove('selected'));
          button.classList.add('selected');
        });
      });
      showToast('Quiz generated successfully.', 'success');
    } catch (error) {
      showToast(error.message, 'danger');
      output.innerHTML = '<div class="empty-state"><i class="bi bi-exclamation-circle fs-1 text-muted"></i><p class="mt-3 mb-0">The quiz could not be generated.</p></div>';
    } finally {
      setLoading(button, false);
    }
  });
}

async function initTasksPage() {
  const form = document.getElementById('task-form');
  const taskList = document.getElementById('task-list');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = {
      title: document.getElementById('task-title').value,
      description: document.getElementById('task-description').value,
      due_date: document.getElementById('task-due-date').value || null,
    };

    try {
      await apiRequest('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      form.reset();
      showToast('Task created successfully.', 'success');
      await loadTasks(currentFilter);
    } catch (error) {
      showToast(error.message, 'danger');
    }
  });

  document.querySelectorAll('[data-status]').forEach((button) => {
    button.addEventListener('click', async () => {
      currentFilter = button.dataset.status;
      document.querySelectorAll('[data-status]').forEach((item) => item.classList.toggle('active', item === button));
      await loadTasks(currentFilter);
    });
  });

  taskList.addEventListener('click', async (event) => {
    const target = event.target;
    const id = Number(target.dataset.id);
    if (!id) return;

    if (target.classList.contains('complete-task')) {
      try {
        await apiRequest(`/api/tasks/${id}/complete`, { method: 'PATCH' });
        showToast('Task marked complete.', 'success');
        await loadTasks(currentFilter);
      } catch (error) {
        showToast(error.message, 'danger');
      }
    }

    if (target.classList.contains('delete-task')) {
      try {
        await apiRequest(`/api/tasks/${id}`, { method: 'DELETE' });
        showToast('Task deleted.', 'success');
        await loadTasks(currentFilter);
      } catch (error) {
        showToast(error.message, 'danger');
      }
    }
  });

  let currentFilter = 'all';
  loadTasks(currentFilter);
}

async function initChatPage() {
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const messages = document.getElementById('chat-messages');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const content = input.value.trim();
    if (!content) return;

    appendMessage('user', content);
    input.value = '';

    try {
      const response = await apiRequest('/api/chat/agent', {
        method: 'POST',
        body: JSON.stringify({ message: content }),
      });
      appendMessage('bot', response.answer);
    } catch (error) {
      appendMessage('bot', `I could not complete that request: ${error.message}`);
    }
  });

  function appendMessage(sender, text) {
    const message = document.createElement('div');
    message.className = `message ${sender}`;
    message.innerHTML = `<div class="message-bubble">${text}</div>`;
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const page = document.body.dataset.page;
  if (page === 'dashboard') initDashboard();
  if (page === 'plans') initPlansPage();
  if (page === 'summarizer') initSummarizerPage();
  if (page === 'quiz') initQuizPage();
  if (page === 'tasks') initTasksPage();
  if (page === 'chat') initChatPage();
});
