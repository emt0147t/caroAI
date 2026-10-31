const { test, expect } = require('@playwright/test');

test('empty History API response has an explicit empty state and no retry error', async ({ page }) => {
  await page.route('**/api/history?*', route => route.fulfill({
    status: 200, contentType: 'application/json', body: JSON.stringify({ items: [] })
  }));
  await page.goto('/history.html');
  await expect(page.locator('#state')).toHaveText('Chưa có ván đấu được lưu.');
  await expect(page.locator('.empty')).toHaveText('Chưa có ván đấu nào được lưu.');
  await expect(page.getByRole('button', { name: 'Thử lại' })).toHaveCount(0);
  await expect(page.locator('#historyPanel')).toHaveAttribute('aria-busy', 'false');
});

test('malformed History API entries do not leave a blank list with a success message', async ({ page }) => {
  await page.route('**/api/history?*', route => route.fulfill({
    status: 200, contentType: 'application/json', body: JSON.stringify({ items: [null, {}, { id: '' }] })
  }));
  await page.goto('/history.html');
  await expect(page.locator('#state')).toHaveText('Chưa có ván đấu được lưu.');
  await expect(page.locator('.empty')).toBeVisible();
});

test('opening a saved game from History restores its backend state', async ({ page, request }) => {
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.ok()).toBeTruthy();
  const game = await create.json();
  const move = await request.post('/api/games/' + encodeURIComponent(game.id) + '/moves', { data: { row: 7, col: 7 } });
  expect(move.ok()).toBeTruthy();

  await page.goto('/history.html');
  const open = page.locator('a[href*="game_id=' + encodeURIComponent(game.id) + '"]');
  await expect(open).toBeVisible();
  await open.click();
  await expect(page).toHaveURL(/trong_tran\/index\.html\?game_id=/);
  await expect(page.getByRole('button', { name: 'Hàng 8, cột 8: X' })).toBeVisible();
  await expect(page.locator('#currentPlayer')).toHaveText('O');
});

test('start screen supports keyboard mode selection and visible focus', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('Tab');
  const focused = await page.evaluate(() => ({
    mode: document.activeElement?.getAttribute('data-mode'),
    outlineWidth: getComputedStyle(document.activeElement).outlineWidth
  }));
  expect(focused.mode).toBe('HUMAN_VS_HUMAN');
  expect(focused.outlineWidth).toBe('3px');

  await page.keyboard.press('Tab');
  await page.keyboard.press('Enter');
  await expect(page.locator('#difficultyGroup')).toBeVisible();
  await expect(page.locator('#difficulty')).toBeEnabled();
  await expect(page.locator('[data-mode="HUMAN_VS_AI"]')).toHaveAttribute('aria-pressed', 'true');
  await page.locator('#difficulty').selectOption('hard');
  await page.getByRole('button', { name: /Bắt đầu ván đấu/ }).click();
  await expect(page).toHaveURL(/difficulty=hard/);
});

test('start screen reports API errors and restores the retryable start control', async ({ page }) => {
  await page.route('**/api/games', async route => {
    await new Promise(resolve => setTimeout(resolve, 250));
    await route.fulfill({
      status: 503, contentType: 'application/json',
      body: JSON.stringify({ detail: 'Game service temporarily unavailable.' })
    });
  });
  await page.goto('/');
  const start = page.locator('#startBtn');
  await start.click();
  await expect(start).toBeDisabled();
  await expect(page.getByRole('alert')).toContainText('Game service temporarily unavailable.');
  await expect(page.getByRole('button', { name: /Bắt đầu ván đấu/ })).toBeEnabled();
});

test('configured same-origin API base URL is used to create a real game', async ({ page }) => {
  await page.addInitScript(() => { window.CAROAI_API_BASE_URL = window.location.origin; });
  await page.goto('/');
  await page.getByRole('button', { name: /Bắt đầu ván đấu/ }).click();
  await expect(page).toHaveURL(/trong_tran\/index\.html\?game_id=/);
});

test('reduced-motion preference suppresses the animated loading indicator', async ({ page, request }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.ok()).toBeTruthy();
  const game = await create.json();
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(game.id));
  await expect(page.locator('#board .cell')).toHaveCount(225);
  const duration = await page.locator('.pulse-dot').evaluate(el => getComputedStyle(el).animationDuration);
  expect(Number.parseFloat(duration)).toBeLessThanOrEqual(0.001);
});

test('finished backend win shows the result card and its new-game action', async ({ page, request }) => {
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.ok()).toBeTruthy();
  const game = await create.json();
  for (const [row, col] of [[7,0],[8,0],[7,1],[8,1],[7,2],[8,2],[7,3],[8,3],[7,4]]) {
    const response = await request.post('/api/games/' + game.id + '/moves', { data: { row, col } });
    expect(response.ok()).toBeTruthy();
  }
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(game.id));
  await expect(page.locator('#resultPanel')).toBeVisible();
  await expect(page.locator('#resultTitle')).toHaveText('X thắng!');
  await expect(page.locator('#resultDetail')).toContainText('xác nhận và lưu bởi Backend');
  await page.getByRole('button', { name: 'Chơi ván mới' }).click();
  await expect(page.locator('#resultPanel')).toBeHidden();
  await expect(page.locator('#board .cell')).toHaveCount(225);
  await expect(page.locator('#gameStatus')).toBeEmpty();
});

test('finished backend draw shows the draw result card', async ({ page, request }) => {
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.ok()).toBeTruthy();
  const game = await create.json();
  const cells = { X: [], O: [] };
  for (let row = 0; row < 15; row++) {
    for (let col = 0; col < 15; col++) {
      cells[(row + Math.floor(col / 2)) % 2 === 0 ? 'X' : 'O'].push([row, col]);
    }
  }
  for (let ply = 0; ply < 225; ply++) {
    const player = ply % 2 === 0 ? 'X' : 'O';
    const [row, col] = cells[player].shift();
    const response = await request.post('/api/games/' + game.id + '/moves', { data: { row, col } });
    expect(response.ok()).toBeTruthy();
  }
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(game.id));
  await expect(page.locator('#resultPanel')).toBeVisible();
  await expect(page.locator('#resultTitle')).toHaveText('Hòa!');
});

test('start, game and History screens do not overflow at phone, tablet and desktop widths', async ({ page, request }) => {
  const widths = [320, 360, 390, 768, 1280];
  const checkWidth = async () => {
    const width = await page.evaluate(() => window.innerWidth);
    const scrollWidth = await page.evaluate(() => Math.max(
      document.documentElement.scrollWidth, document.body.scrollWidth
    ));
    expect(scrollWidth, 'horizontal overflow at ' + width + 'px').toBeLessThanOrEqual(width + 1);
  };

  await page.goto('/');
  for (const width of widths) {
    await page.setViewportSize({ width, height: 844 });
    await checkWidth();
  }

  await page.goto('/history.html');
  for (const width of widths) {
    await page.setViewportSize({ width, height: 844 });
    await checkWidth();
  }

  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.ok()).toBeTruthy();
  const game = await create.json();
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(game.id));
  await expect(page.locator('#board .cell')).toHaveCount(225);
  for (const width of widths) {
    await page.setViewportSize({ width, height: 844 });
    await checkWidth();
  }
});
