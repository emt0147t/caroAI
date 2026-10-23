const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const gameScript = fs.readFileSync(path.join(root, 'frontend/Caro_AI/trong_tran/script.js'), 'utf8');
const welcome = fs.readFileSync(path.join(root, 'frontend/Caro_AI/welcome.html'), 'utf8');

test('create game uses supported backend modes and reads game id', () => {
  assert.match(gameScript, /api\("\/api\/games",\s*\{\s*method:\s*"POST"/);
  assert.match(gameScript, /s\.id\s*=\s*g\.id/);
  assert.match(welcome, /JSON\.stringify\(\{\s*mode:\s*selectedMode\s*\}\)/);
  assert.match(welcome, /data\?\.id/);
  assert.doesNotMatch(welcome, /player_symbol|mode:\s*["']pvai["']/i);
});

test('moves render authoritative response.game and send row/col only', () => {
  assert.match(gameScript, /\/moves"\s*,\s*\{\s*method:\s*"POST"\s*,\s*body:\s*JSON\.stringify\(\{\s*row,\s*col\s*\}\)/);
  assert.match(gameScript, /s\.game\s*=\s*result\.game/);
  assert.match(gameScript, /g\.board\?\.\[r\]\?\.\[c\]/);
  assert.match(gameScript, /g\.status\s*!==\s*"IN_PROGRESS"/);
});

test('PvAI gates AI requests by mode, status and O turn; PvP does not trigger AI', () => {
  assert.match(gameScript, /s\.game\.mode\s*!==\s*"HUMAN_VS_AI"/);
  assert.match(gameScript, /s\.game\.status\s*!==\s*"IN_PROGRESS"/);
  assert.match(gameScript, /s\.game\.current_player\s*!==\s*"O"/);
  assert.match(gameScript, /s\.game\.mode === "HUMAN_VS_AI" && s\.game\.current_player === "O"/);
  assert.match(gameScript, /\["easy","medium","hard"\]\.includes/);
});

test('AI retry resynchronizes game and does not replay the human move', () => {
  assert.match(gameScript, /await loadGame\(s\.id, false\)/);
  assert.match(gameScript, /if \(action === "ai"\)/);
  assert.match(gameScript, /setError\(errorText\(e\), s\.game\.status === "IN_PROGRESS"/);
});

test('network and HTTP errors are surfaced to the UI', () => {
  for (const status of [400, 404, 422]) assert.ok(gameScript.includes('e?.status === ' + status));
  assert.match(gameScript, /Không kết nối được Backend/);
  assert.match(gameScript, /errorMsg\.textContent = message/);
});

test('busy state disables board and new game controls to prevent duplicate requests', () => {
  assert.match(gameScript, /if \(s\.busy\) return/);
  assert.match(gameScript, /b\.disabled = s\.busy/);
  assert.match(gameScript, /newBtn\.disabled = value/);
});
