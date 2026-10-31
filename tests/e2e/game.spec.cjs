const { test, expect } = require('@playwright/test');

async function startGame(page, mode = 'HUMAN_VS_HUMAN', difficulty = 'medium') {
  await page.goto('/');
  if (mode === 'HUMAN_VS_AI') {
    await page.getByRole('button', { name: 'Người vs AI' }).click();
    await page.locator('#difficulty').selectOption(difficulty);
  }
  await page.getByRole('button', { name: /Bắt đầu ván đấu/ }).click();
  await expect(page).toHaveURL(/trong_tran\/index\.html\?game_id=/);
  await expect(page.locator('#board .cell')).toHaveCount(225);
  await expect(page.locator('#loadingBox')).toHaveClass(/hidden/);
  return new URL(page.url()).searchParams.get('game_id');
}
async function getGame(request, id) {
  const response = await request.get('/api/games/' + encodeURIComponent(id));
  expect(response.ok()).toBeTruthy();
  return response.json();
}

test('PvP creates a real backend game and renders alternating authoritative moves', async ({ page, request }) => {
  const id = await startGame(page);
  await page.getByRole('button', { name: 'Đánh hàng 8, cột 8' }).click();
  await expect(page.locator('#currentPlayer')).toHaveText('O');
  await expect(page.locator('#board .cell').filter({ hasText: /^X$/ })).toHaveCount(1);
  await page.getByRole('button', { name: 'Đánh hàng 8, cột 9' }).click();
  await expect(page.locator('#currentPlayer')).toHaveText('X');
  expect(submittedDifficulty).toBe('hard');
  const game = await getGame(request, id);
  expect(game.move_count).toBe(2);
  expect(game.board[7][7]).toBe('X');
  expect(game.board[7][8]).toBe('O');
});

test('PvAI difficulty reaches the real API; AI move is rendered from backend state', async ({ page, request }) => {
  const id = await startGame(page, 'HUMAN_VS_AI', 'hard');
  await expect(page.locator('#aiDifficulty')).toHaveValue('hard');
  let submittedDifficulty = null;
  await page.route('**/api/games/*/ai-move', async route => {
    submittedDifficulty = route.request().postDataJSON()?.difficulty ?? null;
    await route.continue();
  });
  await page.getByRole('button', { name: 'Đánh hàng 8, cột 8' }).click();
  await expect(page.locator('#loadingBox')).toBeVisible();
  await expect(page.locator('#board .cell').filter({ hasText: /^O$/ })).toHaveCount(1, { timeout: 30000 });
  await expect(page.locator('#currentPlayer')).toHaveText('X');
  const game = await getGame(request, id);
  expect(game.move_count).toBe(2);
  expect(game.board[7][7]).toBe('X');
  expect(game.board.flat().filter(v => v === 'O')).toHaveLength(1);
  expect(game.current_player).toBe('X');
});

test('busy state disables cells and prevents duplicate move submissions', async ({ page }) => {
  await startGame(page);
  let calls = 0;
  await page.route('**/api/games/*/moves', async route => {
    calls += 1;
    await new Promise(resolve => setTimeout(resolve, 500));
    await route.continue();
  });
  const cell = page.getByRole('button', { name: 'Đánh hàng 8, cột 8' });
  await cell.click();
  await expect(cell).toBeDisabled();
  await cell.click({ force: true }).catch(() => {});
  await expect(page.locator('#currentPlayer')).toHaveText('O');
  expect(calls).toBe(1);
});

for (const [statusCode, message] of [[400, 'Thao tác không hợp lệ'], [422, 'Dữ liệu gửi lên không hợp lệ']]) {
  test('shows HTTP ' + statusCode + ' error without fabricating a move', async ({ page }) => {
    await startGame(page);
    await page.route('**/api/games/*/moves', route => route.fulfill({
      status: statusCode, contentType: 'application/json',
      body: JSON.stringify({ detail: 'E2E injected HTTP ' + statusCode })
    }));
    await page.getByRole('button', { name: 'Đánh hàng 8, cột 8' }).click();
    await expect(page.locator('#errorBox')).toBeVisible();
    await expect(page.locator('#errorMessage')).toContainText(message);
    await expect(page.locator('#board .cell').filter({ hasText: /^X$/ })).toHaveCount(0);
  });
}

test('404 missing game is visible and does not render a fabricated board state', async ({ page }) => {
  await page.goto('/trong_tran/index.html?game_id=not-a-real-game-id&mode=HUMAN_VS_HUMAN');
  await expect(page.locator('#errorBox')).toBeVisible();
  await expect(page.locator('#errorMessage')).toContainText('Không tìm thấy ván đấu');
  await expect(page.locator('#board .cell')).toHaveCount(0);
});

test('network failure on a move recovers via GET and retry does not replay the human move', async ({ page, request }) => {
  const id = await startGame(page);
  await page.route('**/api/games/*/moves', async route => {
    // Let the real backend commit the move, then simulate the response being lost in transit.
    const response = await route.fetch();
    await response.body();
    await route.abort('failed');
  });
  await page.getByRole('button', { name: 'Đánh hàng 8, cột 8' }).click();
  await expect(page.locator('#errorBox')).toBeVisible();
  await expect(page.locator('#errorMessage')).toContainText('Không kết nối được Backend');
  await expect(page.locator('#retryBtn')).toBeVisible();
  await page.locator('#retryBtn').click();
  await expect(page.locator('#errorBox')).toBeHidden();
  const game = await getGame(request, id);
  expect(game.move_count).toBe(1);
  expect(game.board[7][7]).toBe('X');
});

test('AI retry retries only the AI request and never resends the human move', async ({ page, request }) => {
  const id = await startGame(page, 'HUMAN_VS_AI', 'easy');
  let aiCalls = 0;
  await page.route('**/api/games/*/ai-move', async route => {
    aiCalls += 1;
    if (aiCalls === 1) {
      await route.fulfill({ status: 400, contentType: 'application/json', body: JSON.stringify({ detail: 'temporary AI failure' }) });
    } else await route.continue();
  });
  await page.getByRole('button', { name: 'Đánh hàng 8, cột 8' }).click();
  await expect(page.locator('#retryBtn')).toHaveText('Thử lại lượt AI');
  await page.locator('#retryBtn').click();
  await expect(page.locator('#currentPlayer')).toHaveText('X', { timeout: 30000 });
  const game = await getGame(request, id);
  expect(aiCalls).toBe(2);
  expect(game.move_count).toBe(2);
  expect(game.board.flat().filter(v => v === 'X')).toHaveLength(1);
  expect(game.board.flat().filter(v => v === 'O')).toHaveLength(1);
});

test('end-game state is loaded from API and prevents further moves', async ({ page, request }) => {
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.status()).toBe(201);
  const id = (await create.json()).id;
  for (const [row, col] of [[7,0],[8,0],[7,1],[8,1],[7,2],[8,2],[7,3],[8,3],[7,4]]) {
    const response = await request.post('/api/games/' + id + '/moves', { data: { row, col } });
    expect(response.ok()).toBeTruthy();
  }
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(id));
  await expect(page.locator('#gameStatus')).toContainText('X thắng!');
  const disabled = await page.locator('#board .cell').evaluateAll(cells => cells.every(cell => cell.disabled));
  expect(disabled).toBeTruthy();
  expect((await getGame(request, id)).move_count).toBe(9);
});

test('O win is loaded from API and locks the board for the losing X player', async ({ page, request }) => {
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.status()).toBe(201);
  const id = (await create.json()).id;
  for (const [row, col] of [[0,0],[7,0],[0,1],[7,1],[0,2],[7,2],[0,3],[7,3],[1,0],[7,4]]) {
    const response = await request.post('/api/games/' + id + '/moves', { data: { row, col } });
    expect(response.ok()).toBeTruthy();
  }
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(id));
  await expect(page.locator('#gameStatus')).toContainText('O thắng!');
  const disabled = await page.locator('#board .cell').evaluateAll(cells => cells.every(cell => cell.disabled));
  expect(disabled).toBeTruthy();
  const persisted = await getGame(request, id);
  expect(persisted.status).toBe('O_WON');
  expect(persisted.winner).toBe('O');
  expect(persisted.move_count).toBe(10);
});

test('a full no-five board reaches backend DRAW and locks the UI', async ({ page, request }) => {
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.status()).toBe(201);
  const id = (await create.json()).id;
  const cells = { X: [], O: [] };
  // This 15x15 two-colour pattern has no five consecutive marks in any direction.
  // Counts are 113 X / 112 O, matching the alternating turn order.
  for (let row = 0; row < 15; row++) {
    for (let col = 0; col < 15; col++) {
      cells[(row + Math.floor(col / 2)) % 2 === 0 ? 'X' : 'O'].push([row, col]);
    }
  }
  for (let ply = 0; ply < 225; ply++) {
    const player = ply % 2 === 0 ? 'X' : 'O';
    const [row, col] = cells[player].shift();
    const move = await request.post('/api/games/' + id + '/moves', { data: { row, col } });
    expect(move.status(), 'backend move ' + (ply + 1)).toBe(200);
    if (ply === 224) expect((await move.json()).game.status).toBe('DRAW');
  }
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(id));
  await expect(page.locator('#gameStatus')).toContainText('Hòa!');
  expect(await page.locator('#board .cell').evaluateAll(cells => cells.every(cell => cell.disabled))).toBeTruthy();
  const persisted = await getGame(request, id);
  expect(persisted.status).toBe('DRAW');
  expect(persisted.move_count).toBe(225);
});

test('board remains visible on mobile and desktop viewports', async ({ page }) => {
  await startGame(page);
  for (const width of [360, 390, 1280]) {
    await page.setViewportSize({ width, height: 844 });
    await expect(page.locator('#board')).toBeVisible();
    const box = await page.locator('#board').boundingBox();
    expect(box).not.toBeNull();
    expect(box.width).toBeLessThanOrEqual(width + 1);
    expect(await page.locator('body').evaluate(el => el.scrollWidth)).toBeLessThanOrEqual(width + 1);
  }
});
