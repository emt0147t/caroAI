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

async function installAudioTrace(page) {
  await page.addInitScript(() => {
    localStorage.removeItem('caroai_sound_enabled');
    window.__caroaiAudioStarts = [];
    window.__caroaiAudioContexts = [];

    const contextPrototype = window.AudioContext?.prototype;
    if (contextPrototype?.resume) {
      const nativeResume = contextPrototype.resume;
      contextPrototype.resume = function (...args) {
        if (!window.__caroaiAudioContexts.includes(this)) window.__caroaiAudioContexts.push(this);
        return nativeResume.apply(this, args);
      };
    }

    const contextPrototypeForOscillators = window.AudioContext?.prototype;
    if (contextPrototypeForOscillators?.createOscillator) {
      const nativeCreateOscillator = contextPrototypeForOscillators.createOscillator;
      contextPrototypeForOscillators.createOscillator = function (...args) {
        const oscillator = nativeCreateOscillator.apply(this, args);
        const frequency = oscillator.frequency;
        const nativeSetValueAtTime = frequency.setValueAtTime.bind(frequency);
        frequency.setValueAtTime = (value, time) => {
          oscillator.__caroaiScheduledFrequency = value;
          return nativeSetValueAtTime(value, time);
        };
        return oscillator;
      };
    }

    const sourcePrototype = window.AudioScheduledSourceNode?.prototype;
    if (sourcePrototype?.start) {
      const nativeStart = sourcePrototype.start;
      sourcePrototype.start = function (...args) {
        if (this instanceof window.OscillatorNode) {
          window.__caroaiAudioStarts.push({
            frequency: this.__caroaiScheduledFrequency ?? this.frequency.value,
            contextState: this.context.state
          });
        }
        return nativeStart.apply(this, args);
      };
    }
  });
}

async function enableSoundFromUserGesture(page) {
  await page.locator('#soundToggleBtn').click();
  await expect(page.locator('#soundToggleBtn')).toHaveAttribute('aria-pressed', 'true');
  await page.evaluate(() => { window.__caroaiAudioStarts = []; });
}

async function expectTerminalAudio(page, count) {
  await expect.poll(() => page.evaluate(() => window.__caroaiAudioStarts.length)).toBe(count);
  const info = await page.evaluate(() => ({
    starts: window.__caroaiAudioStarts,
    contexts: window.__caroaiAudioContexts.map(context => context.state)
  }));
  expect(info.contexts.length).toBeGreaterThan(0);
  expect(info.contexts.every(state => state === 'running')).toBe(true);
  return info.starts.map(event => event.frequency);
}

test('winning move plays the victory cue through Web Audio', async ({ page, request }) => {
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.status()).toBe(201);
  const game = await create.json();
  for (const [row, col] of [[7,0],[8,0],[7,1],[8,1],[7,2],[8,2],[7,3],[8,3]]) {
    const move = await request.post('/api/games/' + game.id + '/moves', { data: { row, col } });
    expect(move.ok()).toBeTruthy();
  }

  await installAudioTrace(page);
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(game.id));
  await enableSoundFromUserGesture(page);
  await page.getByRole('button', { name: 'Đánh hàng 8, cột 5' }).click();
  await expect(page.locator('#resultTitle')).toHaveText('X thắng!');
  const frequencies = await expectTerminalAudio(page, 3);
  expect(frequencies[0]).toBeLessThan(frequencies[1]);
  expect(frequencies[1]).toBeLessThan(frequencies[2]);
});

test('AI win plays the defeat cue for the human player', async ({ page, request }) => {
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_AI' } });
  expect(create.status()).toBe(201);
  const game = await create.json();

  await installAudioTrace(page);
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(game.id));
  await enableSoundFromUserGesture(page);
  await page.route('**/api/games/*/ai-move', async route => {
    const terminalBoard = game.board.map(row => row.slice());
    terminalBoard[7][7] = 'X';
    terminalBoard[7][8] = 'O';
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        move: { row: 7, col: 8, player: 'O', move_number: 2 },
        game: { ...game, status: 'O_WON', current_player: 'X', move_count: 2, winner: 'O', board: terminalBoard }
      })
    });
  });
  await page.getByRole('button', { name: 'Đánh hàng 8, cột 8' }).click();
  await expect(page.locator('#resultTitle')).toHaveText('O thắng!');
  const frequencies = await expectTerminalAudio(page, 3);
  expect(frequencies[0]).toBeGreaterThan(frequencies[1]);
  expect(frequencies[1]).toBeGreaterThan(frequencies[2]);
});

test('full board plays the draw cue through Web Audio', async ({ page, request }) => {
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.status()).toBe(201);
  const game = await create.json();
  const cells = { X: [], O: [] };
  for (let row = 0; row < 15; row++) {
    for (let col = 0; col < 15; col++) {
      cells[(row + Math.floor(col / 2)) % 2 === 0 ? 'X' : 'O'].push([row, col]);
    }
  }
  for (let ply = 0; ply < 224; ply++) {
    const player = ply % 2 === 0 ? 'X' : 'O';
    const [row, col] = cells[player].shift();
    const move = await request.post('/api/games/' + game.id + '/moves', { data: { row, col } });
    expect(move.ok(), 'backend move ' + (ply + 1)).toBeTruthy();
  }

  await installAudioTrace(page);
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(game.id));
  await enableSoundFromUserGesture(page);
  await page.locator('#board .cell:not(:disabled)').click();
  await expect(page.locator('#resultTitle')).toHaveText('Hòa!');
  const frequencies = await expectTerminalAudio(page, 2);
  expect(frequencies[0]).toBeGreaterThan(frequencies[1]);
});

test('mobile board exposes an ARIA grid and skips occupied cells with arrow keys', async ({ page, request }) => {
  const create = await request.post('/api/games', { data: { mode: 'HUMAN_VS_HUMAN' } });
  expect(create.status()).toBe(201);
  const game = await create.json();

  for (const [row, col] of [[14,14],[0,1],[14,13],[1,2],[14,12],[1,0]]) {
    const move = await request.post('/api/games/' + game.id + '/moves', { data: { row, col } });
    expect(move.ok()).toBeTruthy();
  }

  await page.setViewportSize({ width: 320, height: 600 });
  await page.goto('/trong_tran/index.html?game_id=' + encodeURIComponent(game.id));
  const grid = page.getByRole('grid', { name: 'Bàn cờ Caro 15 x 15' });
  await expect(grid).toBeVisible();
  await expect(grid.getByRole('row')).toHaveCount(15);
  await expect(grid.getByRole('gridcell')).toHaveCount(225);

  const firstCell = page.locator('#board .cell').first();
  await expect(firstCell).toBeVisible();
  const box = await firstCell.boundingBox();
  expect(box.width).toBeGreaterThanOrEqual(23.9);
  expect(box.height).toBeGreaterThanOrEqual(23.9);
  await expect(page.locator('#board .cell[tabindex="0"]')).toHaveCount(1);

  await firstCell.focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.locator('#board .cell[data-row="0"][data-col="2"]')).toBeFocused();
  await page.keyboard.press('ArrowDown');
  await expect(page.locator('#board .cell[data-row="2"][data-col="2"]')).toBeFocused();
  await expect(page.locator('#board .cell[tabindex="0"]')).toHaveCount(1);
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
