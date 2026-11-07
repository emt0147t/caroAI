const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require('@playwright/test');
const { prepareFont, evidencePage, captureStable } = require('./stable-fonts.cjs');

async function disableMotion(page) {
  await page.addStyleTag({
    content: '*, *::before, *::after { transition: none !important; animation: none !important; }'
  });
}

async function stabilizeStartPage(page) {
  await disableMotion(page);
  await page.evaluate(() => {
    const list = document.getElementById('recentGamesList');
    if (list) {
      list.innerHTML = '<div class="recent-row"><div class="recent-info"><span class="recent-mode">Người vs Người</span><span class="recent-meta">10 nước</span></div><span class="result-tag result-x_won">X thắng</span><a class="recent-open" href="#">Mở →</a></div>';
    }
    const total = document.getElementById('totalGamesCount');
    if (total) total.textContent = '10';
    const status = document.getElementById('systemStatus');
    if (status) status.className = 'status-pill status-online';
    const statusText = document.getElementById('statusText');
    if (statusText) statusText.textContent = 'Hệ thống sẵn sàng';
  });
}

async function stabilizeHistoryPage(page) {
  await disableMotion(page);
  await page.evaluate(() => {
    const list = document.getElementById('list');
    if (list) {
      list.innerHTML = '<article class="item"><div><div class="name">Người vs Người</div><div class="meta">12:00:00 01/01/2026 · Đang chơi · 2 nước</div></div><a href="#">Mở bàn cờ →</a></article>';
    }
  });
}

(async () => {
  const baseUrl = (process.env.CAROAI_BASE_URL || 'http://127.0.0.1:8080').replace(/\/$/, '');
  const label = process.env.EVIDENCE_LABEL || 'candidate';
  const outputDir = path.join('evidence', label);
  await fs.mkdir(outputDir, { recursive: true });

  const font = await prepareFont(outputDir);
  const browser = await chromium.launch({ headless: true });
  try {
    // 1. Mobile 390x844 Light Screenshots
    const mobilePage = await evidencePage(browser, { viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 }, font);
    await mobilePage.goto(baseUrl + '/', { waitUntil: 'networkidle' });
    await stabilizeStartPage(mobilePage);
    await captureStable(mobilePage, { path: path.join(outputDir, 'start-390x844.png'), fullPage: true });

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
    await disableMotion(mobilePage);
    await mobilePage.locator('#board .cell').first().waitFor({ state: 'visible' });
    await captureStable(mobilePage, { path: path.join(outputDir, 'game-390x844.png'), fullPage: true });

    await mobilePage.goto(baseUrl + '/history.html', { waitUntil: 'networkidle' });
    await mobilePage.waitForFunction(() => {
      const state = document.querySelector('#state');
      return !state || !state.textContent.includes('Đang tải');
    });
    await stabilizeHistoryPage(mobilePage);
    await captureStable(mobilePage, { path: path.join(outputDir, 'history-390x844.png'), fullPage: true });

    // 2. Desktop 1280x800 Light Screenshots
    const desktopPage = await evidencePage(browser, { viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 }, font);
    await desktopPage.goto(baseUrl + '/', { waitUntil: 'networkidle' });
    await stabilizeStartPage(desktopPage);
    await captureStable(desktopPage, { path: path.join(outputDir, 'start-1280x800.png'), fullPage: true });

    await desktopPage.goto(baseUrl + '/trong_tran/index.html?game_id=' + encodeURIComponent(game.id), {
      waitUntil: 'networkidle'
    });
    await disableMotion(desktopPage);
    await desktopPage.locator('#board .cell').first().waitFor({ state: 'visible' });
    await captureStable(desktopPage, { path: path.join(outputDir, 'game-1280x800.png'), fullPage: true });

    await desktopPage.goto(baseUrl + '/history.html', { waitUntil: 'networkidle' });
    await desktopPage.waitForFunction(() => {
      const state = document.querySelector('#state');
      return !state || !state.textContent.includes('Đang tải');
    });
    await stabilizeHistoryPage(desktopPage);
    await captureStable(desktopPage, { path: path.join(outputDir, 'history-1280x800.png'), fullPage: true });

    // 3. Check Dark Theme Support
    await desktopPage.goto(baseUrl + '/', { waitUntil: 'networkidle' });
    const supportsDarkTheme = await desktopPage.evaluate(
      () => typeof window.CaroAI?.theme?.apply === 'function'
    );

    if (supportsDarkTheme) {
      // 3. Desktop 1280x800 Dark Screenshots
      await disableMotion(desktopPage);
      await desktopPage.evaluate(() => {
        window.CaroAI.theme.apply('dark');
        localStorage.setItem('caroai_theme', 'dark');
      });
      await stabilizeStartPage(desktopPage);
      await captureStable(desktopPage, { path: path.join(outputDir, 'dark-start-1280x800.png'), fullPage: true });

      await desktopPage.goto(baseUrl + '/trong_tran/index.html?game_id=' + encodeURIComponent(game.id), {
        waitUntil: 'networkidle'
      });
      await disableMotion(desktopPage);
      await desktopPage.locator('#board .cell').first().waitFor({ state: 'visible' });
      await captureStable(desktopPage, { path: path.join(outputDir, 'dark-game-1280x800.png'), fullPage: true });

      await desktopPage.goto(baseUrl + '/history.html', { waitUntil: 'networkidle' });
      await desktopPage.waitForFunction(() => {
        const state = document.querySelector('#state');
        return !state || !state.textContent.includes('Đang tải');
      });
      await stabilizeHistoryPage(desktopPage);
      await captureStable(desktopPage, { path: path.join(outputDir, 'dark-history-1280x800.png'), fullPage: true });

      // 4. Mobile 390x844 Dark Screenshots (Task A1-05 requirement)
      const mobileDarkPage = await evidencePage(browser, { viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 }, font);
      await mobileDarkPage.goto(baseUrl + '/', { waitUntil: 'networkidle' });
      await disableMotion(mobileDarkPage);
      await mobileDarkPage.evaluate(() => {
        window.CaroAI.theme.apply('dark');
        localStorage.setItem('caroai_theme', 'dark');
      });
      await stabilizeStartPage(mobileDarkPage);
      await captureStable(mobileDarkPage, { path: path.join(outputDir, 'dark-start-390x844.png'), fullPage: true });

      await mobileDarkPage.goto(baseUrl + '/trong_tran/index.html?game_id=' + encodeURIComponent(game.id), {
        waitUntil: 'networkidle'
      });
      await disableMotion(mobileDarkPage);
      await mobileDarkPage.locator('#board .cell').first().waitFor({ state: 'visible' });
      await captureStable(mobileDarkPage, { path: path.join(outputDir, 'dark-game-390x844.png'), fullPage: true });

      await mobileDarkPage.goto(baseUrl + '/history.html', { waitUntil: 'networkidle' });
      await mobileDarkPage.waitForFunction(() => {
        const state = document.querySelector('#state');
        return !state || !state.textContent.includes('Đang tải');
      });
      await stabilizeHistoryPage(mobileDarkPage);
      await captureStable(mobileDarkPage, { path: path.join(outputDir, 'dark-history-390x844.png'), fullPage: true });
    } else {
      process.stdout.write('Skipping dark screenshots for ' + label + ': theme API is unavailable.\n');
    }

    process.stdout.write('Captured start, game and history screenshots (mobile and desktop light' +
      (supportsDarkTheme ? ', plus desktop and mobile dark' : '') + ') for ' + label + '.\n');
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
