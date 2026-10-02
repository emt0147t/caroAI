const BOARD_SIZE = 15;
let boardState = Array(BOARD_SIZE).fill(null).map(() => Array(BOARD_SIZE).fill(""));
let currentPlayer = "X";
let isGameOver = false;
let gameMode = "PvP";
let lastMoveCell = null;

const boardElement = document.getElementById("board");
const currentPlayerElement = document.getElementById("currentPlayer");
const gameStatusElement = document.getElementById("gameStatus");
const loadingBox = document.getElementById("loadingBox");
const turnBox = document.getElementById("turnBox");
const gameModeSelect = document.getElementById("gameMode");
const restartBtn = document.getElementById("restartBtn");

function createBoard() {
    boardElement.innerHTML = "";
    for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE; c++) {
            const cell = document.createElement("div");
            cell.classList.add("cell");
            cell.dataset.row = r;
            cell.dataset.col = c;
            cell.addEventListener("click", () => handleCellClick(r, c, cell));
            boardElement.appendChild(cell);
        }
    }
}

function handleCellClick(row, col, cellElement) {
    if (isGameOver || boardState[row][col] !== "") return;

    makeMove(row, col, cellElement, currentPlayer);

    if (gameMode === "PvAI" && !isGameOver && currentPlayer === "O") {
        triggerAIMove();
    }
}

function makeMove(row, col, cellElement, player) {
    boardState[row][col] = player;
    cellElement.textContent = player;
    cellElement.classList.add(player.toLowerCase());

    if (lastMoveCell) lastMoveCell.classList.remove("last-move");
    cellElement.classList.add("last-move");
    lastMoveCell = cellElement;

    currentPlayer = currentPlayer === "X" ? "O" : "X";
    updateTurnUI();
}

function updateTurnUI() {
    currentPlayerElement.textContent = currentPlayer;
    currentPlayerElement.className = `tag tag-${currentPlayer.toLowerCase()}`;
}

function triggerAIMove() {
    turnBox.classList.add("hidden");
    loadingBox.classList.remove("hidden");
    
    setTimeout(() => {
        loadingBox.classList.add("hidden");
        turnBox.classList.remove("hidden");
        
        let emptyCells = [];
        for (let r = 0; r < BOARD_SIZE; r++) {
            for (let c = 0; c < BOARD_SIZE; c++) {
                if (boardState[r][c] === "") emptyCells.push({r, c});
            }
        }

        if (emptyCells.length > 0 && !isGameOver) {
            const randomMove = emptyCells[Math.floor(Math.random() * emptyCells.length)];
            const cellElement = document.querySelector(`[data-row='${randomMove.r}'][data-col='${randomMove.c}']`);
            makeMove(randomMove.r, randomMove.c, cellElement, "O");
        }
    }, 500);
}

function resetGame() {
    boardState = Array(BOARD_SIZE).fill(null).map(() => Array(BOARD_SIZE).fill(""));
    currentPlayer = "X";
    isGameOver = false;
    lastMoveCell = null;
    gameStatusElement.textContent = "";
    loadingBox.classList.add("hidden");
    turnBox.classList.remove("hidden");
    updateTurnUI();
    createBoard();
}

gameModeSelect.addEventListener("change", (e) => {
    gameMode = e.target.value;
    resetGame();
});

restartBtn.addEventListener("click", resetGame);

createBoard();