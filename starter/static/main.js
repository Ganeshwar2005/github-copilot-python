// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let hintsUsed = 0;
const SCOREBOARD_KEY = 'sudokuTopScores';
let currentDifficulty = 'medium';
let gameCompleted = false;

function getScores() {
  try {
    const scores = JSON.parse(localStorage.getItem(SCOREBOARD_KEY) || '[]');
    return Array.isArray(scores) ? scores : [];
  } catch (error) {
    return [];
  }
}

function saveScore() {
  const name = window.prompt('Congratulations! Enter your name for the Top 10:');
  if (!name || !name.trim()) return;

  const scores = [
    ...getScores(),
    {
      name: name.trim(),
      time: elapsedSeconds,
      difficulty: currentDifficulty,
      hints: hintsUsed,
    },
  ]
    .sort((first, second) => first.time - second.time)
    .slice(0, 10);
  localStorage.setItem(SCOREBOARD_KEY, JSON.stringify(scores));
  renderScoreboard();
}

function formatScoreTime(seconds) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
  const remainingSeconds = (seconds % 60).toString().padStart(2, '0');
  return `${minutes}:${remainingSeconds}`;
}

function renderScoreboard() {
  const scoreboard = document.getElementById('scoreboard');
  const scores = getScores();
  scoreboard.innerHTML = '';

  if (scores.length === 0) {
    scoreboard.innerText = 'No scores yet. Solve a puzzle to make the list.';
    return;
  }

  const table = document.createElement('table');
  table.innerHTML = '<thead><tr><th>#</th><th>Name</th><th>Time</th><th>Difficulty</th><th>Hints</th></tr></thead>';
  const body = document.createElement('tbody');
  scores.forEach((score, index) => {
    const row = document.createElement('tr');
    [index + 1, score.name, formatScoreTime(score.time), score.difficulty, score.hints].forEach((value) => {
      const cell = document.createElement('td');
      cell.innerText = value;
      row.appendChild(cell);
    });
    body.appendChild(row);
  });
  table.appendChild(body);
  scoreboard.appendChild(table);
}

function updateTimer() {
  const minutes = Math.floor(elapsedSeconds / 60).toString().padStart(2, '0');
  const seconds = (elapsedSeconds % 60).toString().padStart(2, '0');
  document.getElementById('timer').innerText = `${minutes}:${seconds}`;
}

function startTimer() {
  clearInterval(timerInterval);
  elapsedSeconds = 0;
  updateTimer();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimer();
  }, 1000);
}

function readBoard() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const value = inputs[i * SIZE + j].value;
      board[i][j] = value ? parseInt(value, 10) : 0;
    }
  }
  return board;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        e.target.classList.remove('incorrect');
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  currentDifficulty = difficulty;
  gameCompleted = false;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  hintsUsed = 0;
  document.getElementById('hints-used').innerText = 'Hints: 0';
  document.getElementById('message').innerText = '';
  startTimer();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = readBoard();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  const isComplete = board.every(row => row.every(value => value !== 0));
  if (isComplete && incorrect.size === 0) {
    msg.style.color = '#388e3c';
    msg.innerText = `Congratulations! You solved it in ${document.getElementById('timer').innerText}!`;
    clearInterval(timerInterval);
    if (!gameCompleted) {
      gameCompleted = true;
      saveScore();
    }
  } else if (!isComplete) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Fill in all cells to complete the puzzle.';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function requestHint() {
  const res = await fetch('/hint', {method: 'POST'});
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const index = data.row * SIZE + data.col;
  const input = document.getElementById('sudoku-board').getElementsByTagName('input')[index];
  input.value = data.value;
  input.disabled = true;
  input.className = 'sudoku-cell hint';
  hintsUsed = data.hints_used;
  document.getElementById('hints-used').innerText = `Hints: ${hintsUsed}`;
  msg.style.color = '#3949ab';
  msg.innerText = 'A correct cell has been filled in.';
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('get-hint').addEventListener('click', requestHint);
  renderScoreboard();
  // initialize
  newGame();
});