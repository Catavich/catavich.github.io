let words = [];
let currentWordIndex = 0;
let score = { correct: 0, skipped: 0, stolen: 0 };
let timerInterval;
let timeLeft = 60;
let isPaused = false;
let isTimeUp = false;

const screens = {
    menu: document.getElementById('menu-screen'),
    game: document.getElementById('game-screen'),
    score: document.getElementById('score-screen')
};

function showScreen(screenName) {
    Object.values(screens).forEach(s => s.classList.remove('active'));
    screens[screenName].classList.add('active');
}

async function loadWords() {
    try {
        const response = await fetch('words.json');
        const data = await response.json();
        words = [];
        
        // Flatten the JSON structure into a single array
        for (const category in data) {
            for (const difficulty in data[category]) {
                words = words.concat(data[category][difficulty]);
            }
        }
    } catch (error) {
        document.getElementById('current-word').textContent = 'שגיאה בטעינת הקובץ';
    }
}

function shuffleWords() {
    for (let i = words.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [words[i], words[j]] = [words[j], words[i]];
    }
}

function startGame() {
    if (words.length === 0) return;
    
    shuffleWords();
    score = { correct: 0, skipped: 0, stolen: 0 };
    currentWordIndex = 0;
    timeLeft = 60;
    isTimeUp = false;
    isPaused = false;
    
    document.getElementById('btn-stolen').classList.add('hidden');
    document.getElementById('btn-pause').textContent = 'השהה';
    document.getElementById('btn-pause').classList.remove('hidden');
    updateTimerDisplay();
    
    showScreen('game');
    nextWord();
    
    clearInterval(timerInterval);
    timerInterval = setInterval(updateTimer, 1000);
}

function nextWord() {
    if (currentWordIndex < words.length) {
        document.getElementById('current-word').textContent = words[currentWordIndex];
        currentWordIndex++;
    } else {
        endGame();
    }
}

function updateTimer() {
    if (isPaused || isTimeUp) return;
    
    timeLeft--;
    updateTimerDisplay();
    
    if (timeLeft <= 0) {
        handleTimeUp();
    }
}

function updateTimerDisplay() {
    const minutes = Math.floor(timeLeft / 60).toString().padStart(2, '0');
    const seconds = (timeLeft % 60).toString().padStart(2, '0');
    document.getElementById('timer').textContent = `${minutes}:${seconds}`;
}

function handleTimeUp() {
    isTimeUp = true;
    clearInterval(timerInterval);
    document.getElementById('timer').textContent = "00:00";
    document.getElementById('btn-pause').classList.add('hidden');
    document.getElementById('btn-stolen').classList.remove('hidden');
}

function togglePause() {
    if (isTimeUp) return;
    isPaused = !isPaused;
    document.getElementById('btn-pause').textContent = isPaused ? 'המשך' : 'השהה';
}

function handleAction(actionType) {
    if (actionType === 'correct') score.correct++;
    if (actionType === 'skip') score.skipped++;
    if (actionType === 'stolen') score.stolen++;

    if (isTimeUp) {
        endGame();
    } else {
        nextWord();
    }
}

function endGame() {
    clearInterval(timerInterval);
    showScreen('score');
    document.getElementById('score-correct').textContent = score.correct;
    document.getElementById('score-skipped').textContent = score.skipped;
    document.getElementById('score-total').textContent = score.correct - score.skipped;
    document.getElementById('score-stolen').textContent = score.stolen;
}

// Event Listeners
document.getElementById('btn-start').addEventListener('click', startGame);
document.getElementById('btn-restart').addEventListener('click', startGame);
document.getElementById('btn-pause').addEventListener('click', togglePause);
document.getElementById('btn-correct').addEventListener('click', () => handleAction('correct'));
document.getElementById('btn-skip').addEventListener('click', () => handleAction('skip'));
document.getElementById('btn-stolen').addEventListener('click', () => handleAction('stolen'));

// Initialize
loadWords();