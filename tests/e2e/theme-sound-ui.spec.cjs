const { test, expect } = require('@playwright/test');

test('theme toggle switches theme, updates DOM attributes, and persists across reload', async ({ page }) => {
  await page.goto('/');

  const themeBtn = page.locator('#themeToggleBtn');
  await expect(themeBtn).toBeVisible();

  // Determine initial effective theme dynamically from system preference / API
  const initiallyDark = await page.evaluate(() => window.CaroAI.theme.isDark());
  const expectedNextTheme = initiallyDark ? 'light' : 'dark';
  
  // Click theme toggle to switch
  await themeBtn.click();
  const nextTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  expect(nextTheme).toBe(expectedNextTheme);

  // Verify persistence in localStorage
  const storedTheme = await page.evaluate(() => localStorage.getItem('caroai_theme'));
  expect(storedTheme).toBe(expectedNextTheme);

  // Reload page and verify theme remains intact
  await page.reload();
  const reloadedTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  expect(reloadedTheme).toBe(expectedNextTheme);
});

test('theme persistence survives navigation between dashboard, gameplay, and history', async ({ page, request }) => {
  await page.goto('/');

  // Explicitly set dark mode on dashboard
  await page.evaluate(() => {
    window.CaroAI.theme.apply('dark');
    localStorage.setItem('caroai_theme', 'dark');
  });

  // Verify dashboard has dark theme
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');

  // Create a game to navigate to
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.ok()).toBeTruthy();
  const game = await create.json();

  // Navigate to gameplay
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(game.id));
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await expect(page.locator('#board .cell')).toHaveCount(225);

  // Navigate to history
  await page.goto('/history.html');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
});

test('sound is disabled by default and can be toggled with persistence', async ({ page }) => {
  await page.goto('/');

  // Clear any existing localStorage
  await page.evaluate(() => localStorage.clear());
  await page.reload();

  const soundBtn = page.locator('#soundToggleBtn');
  await expect(soundBtn).toBeVisible();

  // Verify disabled by default
  const defaultState = await page.evaluate(() => window.CaroAI.sound.isEnabled());
  expect(defaultState).toBe(false);
  await expect(soundBtn).toHaveAttribute('aria-pressed', 'false');

  // Click to enable sound
  await soundBtn.click();
  const enabledState = await page.evaluate(() => window.CaroAI.sound.isEnabled());
  expect(enabledState).toBe(true);
  await expect(soundBtn).toHaveAttribute('aria-pressed', 'true');

  // Verify persistence
  const storedSound = await page.evaluate(() => localStorage.getItem('caroai_sound_enabled'));
  expect(storedSound).toBe('true');

  // Reload and verify persistence
  await page.reload();
  await expect(page.locator('#soundToggleBtn')).toHaveAttribute('aria-pressed', 'true');
});

test('terminal sound APIs and draw/defeat cues are available and functional', async ({ page, request }) => {
  await page.goto('/');

  // Verify sound API exports
  const soundAPIs = await page.evaluate(() => ({
    hasPlayMove: typeof window.CaroAI?.sound?.playMove === 'function',
    hasPlayVictory: typeof window.CaroAI?.sound?.playVictory === 'function',
    hasPlayDefeat: typeof window.CaroAI?.sound?.playDefeat === 'function',
    hasPlayDraw: typeof window.CaroAI?.sound?.playDraw === 'function'
  }));
  expect(soundAPIs.hasPlayMove).toBe(true);
  expect(soundAPIs.hasPlayVictory).toBe(true);
  expect(soundAPIs.hasPlayDefeat).toBe(true);
  expect(soundAPIs.hasPlayDraw).toBe(true);

  // Enable sound
  await page.evaluate(() => localStorage.setItem('caroai_sound_enabled', 'true'));

  // Create game and spy on sound calls
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  const game = await create.json();
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(game.id));

  // Install spy
  await page.evaluate(() => {
    window.__soundCalls = [];
    const origMove = window.CaroAI.sound.playMove;
    const origDraw = window.CaroAI.sound.playDraw;
    const origVictory = window.CaroAI.sound.playVictory;
    window.CaroAI.sound.playMove = () => { window.__soundCalls.push('move'); origMove(); };
    window.CaroAI.sound.playDraw = () => { window.__soundCalls.push('draw'); origDraw(); };
    window.CaroAI.sound.playVictory = () => { window.__soundCalls.push('victory'); origVictory(); };
  });

  // Make move on cell (0,0)
  await page.locator('#board .cell').first().click();
  await page.waitForTimeout(500);

  const calls = await page.evaluate(() => window.__soundCalls);
  expect(calls).toContain('move');
});

test('mobile board cells maintain WCAG 2.2 minimum 24px hit area and support arrow navigation', async ({ page, request }) => {
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  const game = await create.json();

  // Test at narrow 320px viewport
  await page.setViewportSize({ width: 320, height: 600 });
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(game.id));

  const firstCell = page.locator('#board .cell').first();
  await expect(firstCell).toBeVisible();

  // Verify cell size is >= 24px (WCAG 2.2 SC 2.5.8 Target Size Minimum)
  const box = await firstCell.boundingBox();
  expect(box.width).toBeGreaterThanOrEqual(23.9);
  expect(box.height).toBeGreaterThanOrEqual(23.9);

  // Verify keyboard arrow navigation
  await firstCell.focus();
  await page.keyboard.press('ArrowRight');
  const secondCellFocused = await page.locator('#board .cell').nth(1).evaluate(el => document.activeElement === el);
  expect(secondCellFocused).toBe(true);

  await page.keyboard.press('ArrowDown');
  const cellRow1Col1Focused = await page.locator('#board .cell').nth(16).evaluate(el => document.activeElement === el);
  expect(cellRow1Col1Focused).toBe(true);
});

test('responsive checks pass across full viewport matrix (320, 360, 390, 768, 1024, 1280, 1440)', async ({ page, request }) => {
  const viewports = [
    { width: 320, height: 600 },
    { width: 360, height: 740 },
    { width: 390, height: 844 },
    { width: 768, height: 1024 },
    { width: 1024, height: 768 },
    { width: 1280, height: 800 },
    { width: 1440, height: 900 }
  ];

  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.ok()).toBeTruthy();
  const game = await create.json();

  const urls = [
    '/',
    '/trong_tran/index.html?game_id=' + encodeURIComponent(game.id),
    '/history.html'
  ];

  for (const url of urls) {
    await page.goto(url);
    for (const vp of viewports) {
      await page.setViewportSize(vp);
      const scrollWidth = await page.evaluate(() => Math.max(document.documentElement.scrollWidth, document.body.scrollWidth));
      expect(scrollWidth, 'No horizontal overflow on ' + url + ' at ' + vp.width + 'px').toBeLessThanOrEqual(vp.width + 1);
    }
  }
});

test('theme and sound controls support visible keyboard focus and accessible labels', async ({ page }) => {
  await page.goto('/');

  const themeBtn = page.locator('#themeToggleBtn');
  const soundBtn = page.locator('#soundToggleBtn');

  await expect(themeBtn).toHaveAttribute('aria-label', /giao diện/i);
  await expect(soundBtn).toHaveAttribute('aria-label', /âm thanh/i);

  // Focus theme button and verify focus ring
  await themeBtn.focus();
  const themeFocus = await themeBtn.evaluate(el => ({
    outlineWidth: getComputedStyle(el).outlineWidth,
    outlineStyle: getComputedStyle(el).outlineStyle
  }));
  expect(themeFocus.outlineWidth).toBe('3px');
  expect(themeFocus.outlineStyle).toBe('solid');

  // Focus sound button and verify focus ring
  await soundBtn.focus();
  const soundFocus = await soundBtn.evaluate(el => ({
    outlineWidth: getComputedStyle(el).outlineWidth,
    outlineStyle: getComputedStyle(el).outlineStyle
  }));
  expect(soundFocus.outlineWidth).toBe('3px');
  expect(soundFocus.outlineStyle).toBe('solid');
});
