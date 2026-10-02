const BOARD_SIZE = 15;
const API_BASE_URL = window.CAROAI_API_BASE_URL || "";
const params = new URLSearchParams(window.location.search);
const state = { gameId: params.get("game_id"), game: null, loading: false, lastMove: null };

const boardElement = document.getElementById("board");
const currentPlayerElement = document.getElementById("currentPlayer");
const gameStatusElement = document.getElementById("gameStatus");
const loadingBox = document.getElementById("loadingBox");
const turnBox = document.getElementById("turnBox");
const gameModeSelect = document.getElementById("gameMode");
const newGameBtn = document.getElementById("newGameBtn");
const errorBox = document.getElementById("errorBox");
const errorMessage = document.getElementById("errorMessage");
const retryBtn = document.getElementById("retryBtn");

if (params.get("mode")) {
  gameModeSelect.value = params.get("mode");
}

function setLoading(value, message = "Đang xử lý...") {
  state.loading = value;
  loadingBox.classList.toggle("hidden", !value);
  loadingBox.lastChild.textContent = " " + message;
  boardElement.classList.toggle("is-loading", value);
  newGameBtn.disabled = value;
  gameModeSelect.disabled = value;
}

function setError(message = "") {
  errorBox.classList.toggle("hidden", !message);
  errorMessage.textContent = message;
}

async function apiRequest(path, options = {}) {
  const response = await fetch(API_BASE_URL + path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) }
  });
  let payload = null;
  try { payload = await response.json(); } catch (_) {}
  if (!response.ok) {
    const error = new Error(payload?.detail || ("HTTP " + response.status));
    error.status = response.status;
    throw error;
  }
  return payload;
}

function render() {
  const game = state.game;
  turnBox.classList.toggle("hidden", !game);
  if (!game) { boardElement.innerHTML = ""; return; }

  currentPlayerElement.textContent = game.current_player || "-";
  currentPlayerElement.className = "tag tag-" + String(game.current_player || "x").toLowerCase();

  const labels = { IN_PROGRESS: "", X_WON: "X thắng!", O_WON: "O thắng!", DRAW: "Hòa!" };
  gameStatusElement.textContent = labels[game.status] || "";
  gameStatusElement.className = "game-alert " + String(game.status).toLowerCase();

  boardElement.innerHTML = "";
  for (let row = 0; row < BOARD_SIZE; row++) {
    for (let col = 0; col < BOARD_SIZE; col++) {
      const cell = document.createElement("button");
      const value = game.board[row]?.[col] || "EMPTY";
      const player = value === "X" || value === "O" ? value : "";
      cell.type = "button";
      cell.className = "cell " + (player ? player.toLowerCase() : "") +
        (state.lastMove?.row === row && state.lastMove?.col === col ? " last-move" : "");
      cell.textContent = player;
      cell.disabled = state.loading || game.status !== "IN_PROGRESS" || Boolean(player);
      cell.addEventListener("click", () => makeMove(row, col));
      boardElement.appendChild(cell);
    }
  }
}

function friendlyError(error) {
  if (error?.name === "TypeError") return "Không kết nối được tới backend. Hãy kiểm tra server.";
  if (error?.status === 400) return "Nước đi không hợp lệ: " + error.message;
  if (error?.status === 404) return "Không tìm thấy ván đấu. Hãy tạo một ván mới.";
  if (error?.status === 422) return "Dữ liệu gửi lên không hợp lệ.";
  return error?.message || "Máy chủ đang gặp sự cố.";
}

async function createGame(mode) {
  setError(); setLoading(true, "Đang tạo ván...");
  try {
    state.game = await apiRequest("/api/games", { method: "POST", body: JSON.stringify({ mode }) });
    state.lastMove = null;
    state.gameId = state.game.id;
    history.replaceState({}, "", window.location.pathname + "?game_id=" + encodeURIComponent(state.gameId));
  } catch (error) { state.game = null; setError(friendlyError(error)); }
  finally { setLoading(false); render(); }
}

async function loadGame(gameId) {
  if (!gameId) return createGame(gameModeSelect.value);
  setError(); setLoading(true, "Đang tải ván...");
  try {
    state.game = await apiRequest("/api/games/" + encodeURIComponent(gameId));
    state.lastMove = null;
    gameModeSelect.value = state.game.mode;
  } catch (error) { state.game = null; setError(friendlyError(error)); }
  finally { setLoading(false); render(); }
}

async function makeMove(row, col) {
  if (!state.gameId || !state.game || state.loading) return;
  setError(); setLoading(true, "Đang gửi nước đi...");
  try {
    const result = await apiRequest("/api/games/" + encodeURIComponent(state.gameId) + "/moves", {
      method: "POST", body: JSON.stringify({ row, col })
    });
    state.game = result.game;
    state.lastMove = result.move || null;
  } catch (error) { setError(friendlyError(error)); }
  finally { setLoading(false); render(); }
}

gameModeSelect.addEventListener("change", () => createGame(gameModeSelect.value));
newGameBtn.addEventListener("click", () => createGame(gameModeSelect.value));
retryBtn.addEventListener("click", () => state.gameId ? loadGame(state.gameId) : createGame(gameModeSelect.value));
render();
loadGame(state.gameId);
