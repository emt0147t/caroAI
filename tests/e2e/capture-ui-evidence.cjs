const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require('@playwright/test');

(async () => {
  const baseUrl = (process.env.CAROAI_BASE_URL || 'http://127.0.0.1:8080').replace(/\/$/, '');
  const label = process.env.EVIDENCE_LABEL || 'candidate';
  const outputDir = path.join('evidence', label);
  await fs.mkdir(outputDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  try {
    // 1. Mobile 390x844 Light Screenshots (CI standard)
    const mobilePage = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
    await mobilePage.goto(baseUrl + '/', { waitUntil: 'networkidle' });
    await mobilePage.screenshot({ path: path.join(outputDir, 'start-390x844.png'), fullPage: true });

    const created = await mobilePage.request.post(baseUrl + '/api/games', {
      data: { mode: 'HUMAN_VS_HUMAN' }
    });
    if (!created.ok()) throw new Error('Could not create screenshot game: HTTP ' + created.status());
    const game = await created.json();
    if (!game?.id) throw new Error('Backend did not return a game ID for screenshot capture.');

    // Make 2 moves to demonstrate board marks and last-move
    await mobilePage.request.post(baseUrl + '/api/games/' + encodeURIComponent(game.id) + '/moves', { data: { row: 7, col: 7 } });
    await mobilePage.request.post(baseUrl + '/api/games/' + encodeURIComponent(game.id) + '/moves', { data: { row: 7, col: 8 } });

    await mobilePage.goto(baseUrl + '/trong_tran/index.html?game_id=' + encodeURIComponent(game.id), {
      waitUntil: 'networkidle'
    });
    await mobilePage.locator('#board .cell').first().waitFor({ state: 'visible' });
    await mobilePage.screenshot({ path: path.join(outputDir, 'game-390x844.png'), fullPage: true });

    await mobilePage.goto(baseUrl + '/history.html', { waitUntil: 'networkidle' });
    await mobilePage.waitForFunction(() => {
      const state = document.querySelector('#state');
      return state && !state.textContent.includes('Đang tải');
    });
    await mobilePage.screenshot({ path: path.join(outputDir, 'history-390x844.png'), fullPage: true });

    // 2. Desktop 1280x800 Light Screenshots
    const desktopPage = await browser.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });
    await desktopPage.goto(baseUrl + '/', { waitUntil: 'networkidle' });
    await desktopPage.screenshot({ path: path.join(outputDir, 'start-1280x800.png'), fullPage: true });

    await desktopPage.goto(baseUrl + '/trong_tran/index.html?game_id=' + encodeURIComponent(game.id), {
      waitUntil: 'networkidle'
    });
    await desktopPage.locator('#board .cell').first().waitFor({ state: 'visible' });
    await desktopPage.screenshot({ path: path.join(outputDir, 'game-1280x800.png'), fullPage: true });

    await desktopPage.goto(baseUrl + '/history.html', { waitUntil: 'networkidle' });
    await desktopPage.waitForFunction(() => {
      const state = document.querySelector('#state');
      return state && !state.textContent.includes('Đang tải');
    });
    await desktopPage.screenshot({ path: path.join(outputDir, 'history-1280x800.png'), fullPage: true });

    // 3. Desktop 1280x800 Dark Screenshots (candidate only).
    // The original baseline predates the shared theme API, so absence of that API
    // must skip only dark-mode evidence rather than failing the baseline capture.
    await desktopPage.goto(baseUrl + '/', { waitUntil: 'networkidle' });
    const supportsDarkTheme = await desktopPage.evaluate(
      () => typeof window.CaroAI?.theme?.apply === 'function'
    );

    if (supportsDarkTheme) {
      await desktopPage.evaluate(() => {
        window.CaroAI.theme.apply('dark');
        localStorage.setItem('caroai_theme', 'dark');
      });
      await desktopPage.screenshot({ path: path.join(outputDir, 'dark-start-1280x800.png'), fullPage: true });

      await desktopPage.goto(baseUrl + '/trong_tran/index.html?game_id=' + encodeURIComponent(game.id), {
        waitUntil: 'networkidle'
      });
      await desktopPage.locator('#board .cell').first().waitFor({ state: 'visible' });
      await desktopPage.screenshot({ path: path.join(outputDir, 'dark-game-1280x800.png'), fullPage: true });

      await desktopPage.goto(baseUrl + '/history.html', { waitUntil: 'networkidle' });
      await desktopPage.waitForFunction(() => {
        const state = document.querySelector('#state');
        return state && !state.textContent.includes('Đang tải');
      });
      await desktopPage.screenshot({ path: path.join(outputDir, 'dark-history-1280x800.png'), fullPage: true });
    } else {
      process.stdout.write('Skipping dark screenshots for ' + label + ': theme API is unavailable.\n');
    }

    process.stdout.write('Captured start, game and history screenshots (mobile and desktop light' +
      (supportsDarkTheme ? ', plus desktop dark' : '') + ') for ' + label + '.\n');
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
