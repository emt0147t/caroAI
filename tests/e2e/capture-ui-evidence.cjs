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
    const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
    await page.goto(baseUrl + '/', { waitUntil: 'networkidle' });
    await page.screenshot({ path: path.join(outputDir, 'start-390x844.png'), fullPage: true });

    const created = await page.request.post(baseUrl + '/api/games', {
      data: { mode: 'HUMAN_VS_HUMAN' }
    });
    if (!created.ok()) throw new Error('Could not create screenshot game: HTTP ' + created.status());
    const game = await created.json();
    if (!game?.id) throw new Error('Backend did not return a game ID for screenshot capture.');

    await page.goto(baseUrl + '/trong_tran/index.html?game_id=' + encodeURIComponent(game.id), {
      waitUntil: 'networkidle'
    });
    await page.locator('#board .cell').first().waitFor({ state: 'visible' });
    await page.screenshot({ path: path.join(outputDir, 'game-390x844.png'), fullPage: true });

    await page.goto(baseUrl + '/history.html', { waitUntil: 'networkidle' });
    await page.waitForFunction(() => {
      const state = document.querySelector('#state');
      return state && !state.textContent.includes('Đang tải');
    });
    await page.screenshot({ path: path.join(outputDir, 'history-390x844.png'), fullPage: true });
    process.stdout.write('Captured start, game and history screenshots for ' + label + ' at 390x844.\n');
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
