const { test, expect } = require('@playwright/test');

test('history endpoint unavailability is shown honestly with retry', async ({ page, request }) => {
  await page.goto('/history.html');
  const response = await request.get('/api/games/history?limit=20&offset=0');
  if (response.status() !== 404) test.skip(true, 'History API is available; persistence assertion is exercised in the next test.');
  await expect(page.locator('#state')).toContainText('History API chưa khả dụng');
  await expect(page.getByRole('button', { name: 'Thử lại' })).toBeVisible();
});

test('a created game appears in backend history after reload in a fresh page', async ({ page, context, request }) => {
  const response = await request.get('/api/games/history?limit=20&offset=0');
  if (response.status() === 404) test.skip(true, 'Blocked until M1 merges and publishes the history API contract.');
  expect(response.ok()).toBeTruthy();

  await page.goto('/');
  await page.getByRole('button', { name: /Bắt đầu ván đấu/ }).click();
  await expect(page).toHaveURL(/trong_tran\/index\.html\?game_id=/);
  const id = new URL(page.url()).searchParams.get('game_id');

  const historyPage = await context.newPage();
  await historyPage.goto('/history.html');
  await expect(historyPage.locator('.item a[href*="' + encodeURIComponent(id) + '"]')).toBeVisible();
  await historyPage.reload();
  await expect(historyPage.locator('.item a[href*="' + encodeURIComponent(id) + '"]')).toBeVisible();
});
