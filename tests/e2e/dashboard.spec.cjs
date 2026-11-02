const { test, expect } = require('@playwright/test');

test('dashboard displays brand header, system health status, and quick nav', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.brand-name')).toContainText('CaroAI');
  await expect(page.locator('#systemStatus')).toBeVisible();
  await expect(page.locator('#statusText')).toHaveText('Hệ thống sẵn sàng', { timeout: 10000 });
  await expect(page.locator('#systemStatus')).toHaveClass(/status-online/);

  // Quick navigation to rules and history
  const historyNav = page.locator('.header-nav a[href="history.html"]');
  await expect(historyNav).toBeVisible();
  const rulesNav = page.locator('.header-nav a[href="#rulesSection"]');
  await expect(rulesNav).toBeVisible();
});

test('dashboard displays game metrics and features showcase', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.metrics-grid')).toBeVisible();
  await expect(page.locator('.metric-value', { hasText: '15 × 15' })).toBeVisible();
  await expect(page.locator('.metric-value', { hasText: 'PvP / AI' })).toBeVisible();

  // Features showcase section
  const features = page.locator('.dashboard-features .feature-card');
  await expect(features).toHaveCount(3);
  await expect(features.nth(0)).toContainText('Chuẩn Gomoku 15 × 15');
  await expect(features.nth(1)).toContainText('Backend Quyết Định Tuyệt Đối');
  await expect(features.nth(2)).toContainText('Động Cơ AI Minimax');

  // Rules section
  const rules = page.locator('.rules-grid .rule-item');
  await expect(rules).toHaveCount(4);
});

test('dashboard handles system health offline state gracefully', async ({ page }) => {
  await page.route('**/health', route => route.abort('failed'));
  await page.goto('/');
  await expect(page.locator('#systemStatus')).toHaveClass(/status-offline/);
  await expect(page.locator('#statusText')).toHaveText('Mất kết nối Backend');
});

test('dashboard recent games widget renders persisted backend matches', async ({ page, request }) => {
  // Create a game to guarantee at least one match in history
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.ok()).toBeTruthy();

  await page.goto('/');
  await expect(page.locator('.stats-card')).toBeVisible();
  const recentRows = page.locator('#recentGamesList .recent-row');
  await expect(recentRows.first()).toBeVisible({ timeout: 10000 });
  await expect(recentRows.first().locator('.recent-open')).toHaveAttribute('href', /game_id=/);
});
