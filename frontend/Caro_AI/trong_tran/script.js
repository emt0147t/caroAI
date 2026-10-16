const N = 15;
const API = String(window.CAROAI_API_BASE_URL || "").replace(/\/$/, "");
const qs = new URLSearchParams(location.search);
const s = { id: qs.get("game_id"), game: null, busy: false, lastMove: null,
  difficulty: ["easy","medium","hard"].includes(qs.get("difficulty")) ? qs.get("difficulty") : "medium",
  retry: null };
const $ = id => document.getElementById(id);
const board = $("board"), current = $("currentPlayer"), status = $("gameStatus"),
  loading = $("loadingBox"), turn = $("turnBox"), mode = $("gameMode"),
  newBtn = $("newGameBtn"), errorBox = $("errorBox"), errorMsg = $("errorMessage"),
  retryBtn = $("retryBtn"), difficulty = $("aiDifficulty"), difficultyGroup = $("difficultyGroup");

function setBusy(value, message = "Đang xử lý...") {
  s.busy = value; loading.classList.toggle("hidden", !value);
  loading.lastChild.textContent = " " + message;
  board.classList.toggle("is-loading", value); newBtn.disabled = value; mode.disabled = value;
  if (difficulty) difficulty.disabled = value;
}
function setError(message = "", retry = null) {
  s.retry = retry; errorBox.classList.toggle("hidden", !message); errorMsg.textContent = message;
  retryBtn.classList.toggle("hidden", !retry);
  retryBtn.textContent = retry === "ai" ? "Thử lại lượt AI" : "Đồng bộ và thử lại";
}
async function api(path, options = {}) {
  let res;
  try { res = await fetch(API + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } }); }
  catch (_) { const e = new Error("Không kết nối được Backend. Hãy kiểm tra server và API base URL."); e.network = true; throw e; }
  let data = null; try { data = await res.json(); } catch (_) {}
  if (!res.ok) { const e = new Error(data?.detail || ("HTTP " + res.status)); e.status = res.status; throw e; }
  return data;
}
function errorText(e) {
  if (e?.network || e?.name === "TypeError") return e.message || "Không kết nối được Backend.";
  if (e?.status === 400) return "Thao tác không hợp lệ: " + e.message;
  if (e?.status === 404) return "Không tìm thấy ván đấu. Hãy tạo ván mới.";
  if (e?.status === 422) return "Dữ liệu gửi lên không hợp lệ.";
  if (e?.status >= 500) return "Backend đang gặp sự cố. Vui lòng thử lại sau.";
  return e?.message || "Đã xảy ra lỗi.";
}
function updateUrl() {
  const p = new URLSearchParams({ game_id: s.id || "", mode: s.game?.mode || mode.value, difficulty: s.difficulty });
  history.replaceState({}, "", location.pathname + "?" + p.toString());
}
function render() {
  const g = s.game; turn.classList.toggle("hidden", !g);
  if (!g) { board.innerHTML = ""; return; }
  current.textContent = g.current_player || "-";
  current.className = "tag tag-" + String(g.current_player || "x").toLowerCase();
  status.textContent = ({ IN_PROGRESS: "", X_WON: "X thắng!", O_WON: "O thắng!", DRAW: "Hòa!" })[g.status] ?? "Trạng thái không xác định";
  status.className = "game-alert " + String(g.status).toLowerCase();
  difficultyGroup?.classList.toggle("hidden", g.mode !== "HUMAN_VS_AI");
  if (difficulty) difficulty.value = s.difficulty;
  board.innerHTML = "";
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    const b = document.createElement("button"), v = g.board?.[r]?.[c] || "EMPTY";
    const p = v === "X" || v === "O" ? v : "";
    const humanTurn = g.mode === "HUMAN_VS_HUMAN" || (g.mode === "HUMAN_VS_AI" && g.current_player === "X");
    b.type = "button"; b.textContent = p;
    b.setAttribute("aria-label", p ? `Hàng ${r+1}, cột ${c+1}: ${p}` : `Đánh hàng ${r+1}, cột ${c+1}`);
    b.className = "cell " + (p ? p.toLowerCase() : "") + (s.lastMove?.row === r && s.lastMove?.col === c ? " last-move" : "");
    b.disabled = s.busy || g.status !== "IN_PROGRESS" || !!p || !humanTurn;
    b.addEventListener("click", () => makeMove(r, c)); board.appendChild(b);
  }
}
async function createGame(gameMode = mode.value) {
  if (s.busy) return; setError(); setBusy(true, "Đang tạo ván...");
  try {
    const g = await api("/api/games", { method: "POST", body: JSON.stringify({ mode: gameMode }) });
    if (!g?.id || !Array.isArray(g.board)) throw new Error("Backend trả về dữ liệu ván đấu không hợp lệ.");
    s.game = g; s.id = g.id; s.lastMove = null; mode.value = g.mode; updateUrl();
  } catch (e) { s.game = null; setError(errorText(e)); }
  finally { setBusy(false); render(); }
}
async function loadGame(id, resumeAI = true) {
  if (!id || s.busy) return; setError(); setBusy(true, "Đang tải ván...");
  try {
    const g = await api("/api/games/" + encodeURIComponent(id));
    if (!Array.isArray(g?.board)) throw new Error("Backend trả về bàn cờ không hợp lệ.");
    s.game = g; s.id = g.id; mode.value = g.mode; updateUrl();
  } catch (e) { s.game = null; setError(errorText(e)); }
  finally { setBusy(false); render(); }
  if (resumeAI && s.game?.status === "IN_PROGRESS" && s.game.mode === "HUMAN_VS_AI" && s.game.current_player === "O") await aiMove();
}
async function makeMove(row, col) {
  const g = s.game;
  if (s.busy || !s.id || !g || g.status !== "IN_PROGRESS" || (g.mode === "HUMAN_VS_AI" && g.current_player !== "X")) return;
  setError(); setBusy(true, "Đang gửi nước đi...");
  try {
    const result = await api("/api/games/" + encodeURIComponent(s.id) + "/moves", { method: "POST", body: JSON.stringify({ row, col }) });
    s.game = result.game; s.lastMove = result.move || null; updateUrl();
  } catch (e) {
    try {
      s.game = await api("/api/games/" + encodeURIComponent(s.id));
      setError(errorText(e), s.game.status === "IN_PROGRESS" && s.game.mode === "HUMAN_VS_AI" && s.game.current_player === "O" ? "ai" : "sync");
    } catch (_) { setError(errorText(e), "sync"); }
  } finally { setBusy(false); render(); }
  if (!s.retry && s.game?.status === "IN_PROGRESS" && s.game.mode === "HUMAN_VS_AI" && s.game.current_player === "O") await aiMove();
}
async function aiMove() {
  if (s.busy || !s.id || !s.game || s.game.mode !== "HUMAN_VS_AI" || s.game.status !== "IN_PROGRESS" || s.game.current_player !== "O") return;
  setError(); setBusy(true, "AI đang suy nghĩ...");
  try {
    const result = await api("/api/games/" + encodeURIComponent(s.id) + "/ai-move", { method: "POST", body: JSON.stringify({ difficulty: s.difficulty }) });
    s.game = result.game; s.lastMove = result.move || null; updateUrl();
  } catch (e) {
    try {
      s.game = await api("/api/games/" + encodeURIComponent(s.id));
      if (s.game.status === "IN_PROGRESS" && s.game.mode === "HUMAN_VS_AI" && s.game.current_player === "X") {
        s.lastMove = null; setError("Đã đồng bộ trạng thái ván đấu. " + errorText(e));
      } else setError(errorText(e), "ai");
    } catch (_) { setError(errorText(e), "ai"); }
  } finally { setBusy(false); render(); }
}
mode.addEventListener("change", () => difficultyGroup?.classList.toggle("hidden", mode.value !== "HUMAN_VS_AI"));
difficulty?.addEventListener("change", () => { if (["easy","medium","hard"].includes(difficulty.value)) s.difficulty = difficulty.value; updateUrl(); });
newBtn.addEventListener("click", () => createGame(mode.value));
retryBtn.addEventListener("click", async () => {
  if (s.busy) return; const action = s.retry; setError();
  if (action === "ai") {
    await loadGame(s.id, false);
    if (s.game?.status === "IN_PROGRESS" && s.game.mode === "HUMAN_VS_AI" && s.game.current_player === "O") await aiMove();
  } else if (s.id) await loadGame(s.id);
  else await createGame(mode.value);
});
render();
if (s.id) loadGame(s.id); else createGame(qs.get("mode") === "HUMAN_VS_AI" ? "HUMAN_VS_AI" : "HUMAN_VS_HUMAN");
