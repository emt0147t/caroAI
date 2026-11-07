// Pin only the screenshot harness's external font response. Product CSS stays intact.
const fs = require('node:fs/promises');
const path = require('node:path');
const { createHash } = require('node:crypto');

const COMMIT = '8cd7d0de182c88592d6852c245fe48f66eef55ee';
const SOURCE = `https://raw.githubusercontent.com/google/fonts/${COMMIT}/ofl/plusjakartasans/PlusJakartaSans%5Bwght%5D.ttf`;
const EXPECTED = '89b3fb38aa0d275d7a731d0d817a4f1622b316b4d7fbdedcf02ee9099ff68bc8';
const FIXTURE_URL = 'https://fonts.gstatic.com/caroai-evidence/plus-jakarta-sans.ttf';
const FONT_CSS = `@font-face {
  font-family: 'Plus Jakarta Sans'; font-style: normal; font-weight: 100 900;
  font-display: swap; src: url('${FIXTURE_URL}') format('truetype');
}`;

async function prepareFont(outputDir) {
  const cache = path.join('work', 'visual-fonts', 'plus-jakarta-sans.ttf');
  let font;
  try {
    font = await fs.readFile(cache);
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const response = await fetch(SOURCE, { signal: AbortSignal.timeout(20000) });
        if (!response.ok) throw new Error(`Font download: HTTP ${response.status}`);
        font = Buffer.from(await response.arrayBuffer());
        break;
      } catch (failure) {
        if (attempt === 2) throw failure;
      }
    }
    await fs.mkdir(path.dirname(cache), { recursive: true });
    await fs.writeFile(cache, font);
  }
  if (createHash('sha256').update(font).digest('hex') !== EXPECTED) {
    throw new Error('Pinned screenshot font SHA-256 mismatch');
  }
  await fs.writeFile(path.join(outputDir, 'font-provenance.json'), JSON.stringify({
    source: SOURCE, commit: COMMIT, sha256: EXPECTED,
    license: `https://raw.githubusercontent.com/google/fonts/${COMMIT}/ofl/plusjakartasans/OFL.txt`
  }, null, 2) + '\n');
  return font;
}

async function evidencePage(browser, options, font) {
  const page = await browser.newPage(options);
  await page.route('https://fonts.googleapis.com/**', async route => {
    const family = new URL(route.request().url()).searchParams.get('family') || '';
    if (family.split(':', 1)[0] !== 'Plus Jakarta Sans') return route.continue();
    return route.fulfill({ status: 200, contentType: 'text/css', body: FONT_CSS });
  });
  await page.route(FIXTURE_URL, route => route.fulfill({
    status: 200, contentType: 'font/ttf', body: font,
    headers: { 'access-control-allow-origin': '*' }
  }));
  return page;
}

async function captureStable(page, options) {
  await page.evaluate(async () => {
    await document.fonts.ready;
    const faces = [...document.fonts].filter(face => face.family.includes('Plus Jakarta Sans'));
    if (faces.some(face => face.status === 'error')) throw new Error('Screenshot font failed to load');
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  });
  return page.screenshot(options);
}

module.exports = { prepareFont, evidencePage, captureStable };
