const { test, expect } = require('@playwright/test');

test('empty History API response has an explicit empty state and no retry error', async ({ page }) => {
  await page.route('**/api/history?*', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ items: [] })
  }));
  await page.goto('/history.html');
  await expect(page.locator('#state')).toHaveText('Chưa có ván đấu được lưu.');
  await expect(page.locator('.empty')).toHaveText('Chưa có ván đấu nào được lưu.');
  await expect(page.getByRole('button', { name: 'Thử lại' })).toHaveCount(0);
  await expect(page.locator('#historyPanel')).toHaveAttribute('aria-busy', 'false');
});

test('malformed History API entries do not leave a blank list with a success message', async ({ page }) => {
  await page.route('**/api/history?*', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ items: [null, {}, { id: '' }] })
  }));
  await page.goto('/history.html');
  await expect(page.locator('#state')).toHaveText('Chưa có ván đấu được lưu.');
  await expect(page.locator('.empty')).toBeVisible();
});

test('opening a saved game from History restores its backend state', async ({ page, request }) => {
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.ok()).toBeTruthy();
  const game = await create.json();
  const move = await request.post('/api/games/' + encodeURIComponent(game.id) + '/moves', {
    data: { row: 7, col: 7 }
  });
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

test('start, game and History screens do not overflow at phone, tablet and desktop widths', async ({ page, request }) => {
  const widths = [320, 360, 390, 768, 1280];
  const checkWidth = async () => {
    const width = await page.evaluate(() => window.innerWidth);
    const scrollWidth = await page.evaluate(() => Math.max(
      document.documentElement.scrollWidth,
      document.body.scrollWidth
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
