const BOARD_SIZE = 15;
let isBoardLocked = false; // Biến khóa bàn cờ khi đang chờ API hoặc lượt AI
let lastMoveCell = null;

// Lấy game_id được lưu khi bấm nút Start ở welcome.html
const gameId = sessionStorage.getItem('game_id') || "test_game"; 
const BASE_URL = 'http://localhost:8000/api/games'; // Đường dẫn Backend của nhóm

const boardElement = document.getElementById("board");
const currentPlayerElement = document.getElementById("currentPlayer");
const gameStatusElement = document.getElementById("gameStatus");
const loadingBox = document.getElementById("loadingBox");
const turnBox = document.getElementById("turnBox");
const restartBtn = document.getElementById("restartBtn");

function createBoard() {
    boardElement.innerHTML = "";
    for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE; c++) {
            const cell = document.createElement("div");
            cell.classList.add("cell");
            cell.dataset.row = r;
            cell.dataset.col = c;
            cell.addEventListener("click", () => handleCellClick(r, c));
            boardElement.appendChild(cell);
        }
    }
}

// Hàm khóa/mở khóa giao diện bàn cờ để tránh spam click và quản lý turn lock
function setBoardLock(locked, message = "") {
    isBoardLocked = locked;
    if (boardElement) {
        if (locked) {
            boardElement.style.pointerEvents = "none";
            boardElement.style.opacity = "0.7";
        } else {
            boardElement.style.pointerEvents = "auto";
            boardElement.style.opacity = "1";
        }
    }
    if (gameStatusElement && message) {
        gameStatusElement.textContent = message;
    }
}

// 1. Khi người chơi đánh (Human Move)
async function handleCellClick(row, col) {
    if (isBoardLocked) return;

    // Khóa bàn cờ ngay lập tức sau khi người chơi bấm
    setBoardLock(true, "Đang gửi nước đi...");

    try {
        const response = await fetch(`${BASE_URL}/${gameId}/moves`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ row, col })
        });

        if (!response.ok) throw new Error("Nước đi không hợp lệ!");

        const gameData = await response.json();

        // Render lại bàn cờ hoàn toàn dựa vào response từ Backend
        renderBoardState(gameData.board);

        // Kiểm tra xem trận đấu đã kết thúc chưa
        if (checkGameEnd(gameData)) return;

        // Nếu chưa kết thúc, kích hoạt lượt đi của AI qua API thật
        await triggerAIMove();

    } catch (error) {
        handleApiError("Lỗi kết nối hoặc nước đi sai", () => handleCellClick(row, col));
    }
}

// 2. Gọi API yêu cầu AI đi nước đi tiếp theo (Thay thế hoàn toàn fake AI random cũ)
async function triggerAIMove() {
    turnBox.classList.add("hidden");
    loadingBox.classList.remove("hidden");
    setBoardLock(true, "AI đang suy nghĩ...");

    try {
        const response = await fetch(`${BASE_URL}/${gameId}/ai-move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error("AI không phản hồi!");

        const gameData = await response.json();

        // Render bàn cờ với nước đi mới của AI do Backend trả về
        renderBoardState(gameData.board);

        loadingBox.classList.add("hidden");
        turnBox.classList.remove("hidden");

        // Kiểm tra kết thúc trận đấu sau nước đi của AI
        if (checkGameEnd(gameData)) return;

        // Mở khóa bàn cờ cho người chơi tiếp tục
        setBoardLock(false, "Đến lượt bạn!");

    } catch (error) {
        loadingBox.classList.add("hidden");
        turnBox.classList.remove("hidden");
        handleApiError("AI gặp sự cố", () => triggerAIMove());
    }
}

// Hàm render lại toàn bộ mảng board từ Server trả về
function renderBoardState(boardArray) {
    for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE; c++) {
            const cellValue = boardArray[r][c]; // "X", "O", hoặc ""
            const cellElement = document.querySelector(`[data-row='${r}'][data-col='${c}']:not(script)`);
            if (!cellElement) continue;

            cellElement.textContent = cellValue;
            cellElement.classList.remove("x", "o");
            if (cellValue) {
                cellElement.classList.add(cellValue.toLowerCase());
            }
        }
    }
}

// 3. Xử lý trạng thái kết thúc trận đấu chuyển trang
function checkGameEnd(gameData) {
    if (gameData.status === 'FINISHED' || gameData.is_over) {
        setBoardLock(true, "Trận đấu kết thúc!");
        
        setTimeout(() => {
            if (gameData.winner === 'X') {
                window.location.href = '../ket_qua/win.html';
            } else if (gameData.winner === 'O') {
                window.location.href = '../ket_qua/lose.html';
            } else {
                window.location.href = '../ket_qua/draw.html';
            }
        }, 1000);
        return true;
    }
    return false;
}

// 4. Xử lý Error / Retry khi có lỗi API mạng
function handleApiError(message, retryCallback) {
    const isRetry = confirm(`${message}. Bạn có muốn thử lại không?`);
    if (isRetry) {
        retryCallback();
    } else {
        setBoardLock(false, "Đã hủy thao tác. Hãy thử lại!");
    }
}

function resetGame() {
    // Có thể gọi API reset hoặc reload lại welcome
    window.location.href = '../welcome.html';
}

if (restartBtn) {
    restartBtn.addEventListener("click", resetGame);
}

// Khởi tạo bàn cờ lần đầu
createBoard();
setBoardLock(false, "Đến lượt bạn!");
