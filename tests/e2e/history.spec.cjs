const { test, expect } = require('@playwright/test');

test('history shows API errors and retry recovers', async ({ page }) => {
  await page.route('**/api/history?*', route => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ detail: 'Game storage is temporarily unavailable.' })
  }));
  await page.goto('/history.html');
  await expect(page.locator('#state')).toContainText('Game storage is temporarily unavailable');
  await expect(page.getByRole('button', { name: 'Thử lại' })).toBeVisible();

  await page.unroute('**/api/history?*');
  await page.getByRole('button', { name: 'Thử lại' }).click();
  await expect(page.locator('#state')).toContainText(/Lịch sử lấy trực tiếp từ Backend|Chưa có ván đấu được lưu/);
});

test('a created game appears in backend history after reload in a fresh page', async ({ page, context, request }) => {
  const before = await request.get('/api/history?limit=100&offset=0');
  expect(before.ok(), 'GET /api/history must be available').toBeTruthy();
  const beforeData = await before.json();
  expect(Array.isArray(beforeData.items)).toBeTruthy();

  await page.goto('/');
  await page.getByRole('button', { name: /Bắt đầu ván đấu/ }).click();
  await page.waitForURL(url => url.pathname.endsWith('/trong_tran/index.html') && url.searchParams.has('game_id'));
  const id = new URL(page.url()).searchParams.get('game_id');
  expect(id).toBeTruthy();

  // Verify the persisted record through the API before checking the UI.
  await expect.poll(async () => {
    const response = await request.get('/api/history?limit=100&offset=0');
    if (!response.ok()) return false;
    const data = await response.json();
    return data.items.some(game => game.id === id);
  }, { timeout: 10000 }).toBeTruthy();

  const historyPage = await context.newPage();
  await historyPage.goto('/history.html');
  const gameLink = historyPage.locator('a[href*="game_id=' + encodeURIComponent(id) + '"]');
  await expect(gameLink).toBeVisible();
  await historyPage.reload();
  await expect(historyPage.locator('a[href*="game_id=' + encodeURIComponent(id) + '"]')).toBeVisible();
});
