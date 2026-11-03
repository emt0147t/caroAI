const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require('@playwright/test');

const DEFAULT_BASELINE_DIR = path.join('evidence', 'baseline');
const DEFAULT_CANDIDATE_DIR = path.join('evidence', 'candidate');
const DEFAULT_DIFF_DIR = path.join('evidence', 'diff');
const DEFAULT_DIFF_THRESHOLD = 0.02; // 2% maximum allowable mismatched pixels
const DEFAULT_COLOR_TOLERANCE = 25; // RGB channel delta tolerance for subpixel antialiasing

async function compareImagesInBrowser(page, baselineBuf, candidateBuf, colorTolerance) {
  const base64Baseline = baselineBuf.toString('base64');
  const base64Candidate = candidateBuf.toString('base64');

  return await page.evaluate(async ({ base64Baseline, base64Candidate, colorTolerance }) => {
    function loadImage(src) {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = src;
      });
    }

    const img1 = await loadImage('data:image/png;base64,' + base64Baseline);
    const img2 = await loadImage('data:image/png;base64,' + base64Candidate);

    const width = Math.max(img1.naturalWidth, img2.naturalWidth);
    const height = Math.max(img1.naturalHeight, img2.naturalHeight);

    const c1 = document.createElement('canvas');
    c1.width = width;
    c1.height = height;
    const ctx1 = c1.getContext('2d');
    ctx1.drawImage(img1, 0, 0);
    const data1 = ctx1.getImageData(0, 0, width, height).data;

    const c2 = document.createElement('canvas');
    c2.width = width;
    c2.height = height;
    const ctx2 = c2.getContext('2d');
    ctx2.drawImage(img2, 0, 0);
    const data2 = ctx2.getImageData(0, 0, width, height).data;

    const diffCanvas = document.createElement('canvas');
    diffCanvas.width = width;
    diffCanvas.height = height;
    const diffCtx = diffCanvas.getContext('2d');
    const diffImageData = diffCtx.createImageData(width, height);
    const diffData = diffImageData.data;

    const totalPixels = width * height;
    let mismatchedPixels = 0;

    for (let i = 0; i < data1.length; i += 4) {
      const r1 = data1[i];
      const g1 = data1[i + 1];
      const b1 = data1[i + 2];
      const a1 = data1[i + 3];

      const r2 = data2[i];
      const g2 = data2[i + 1];
      const b2 = data2[i + 2];
      const a2 = data2[i + 3];

      const delta = Math.abs(r1 - r2) + Math.abs(g1 - g2) + Math.abs(b1 - b2) + Math.abs(a1 - a2);

      if (delta > colorTolerance) {
        mismatchedPixels++;
        // Red highlight for diff
        diffData[i] = 255;
        diffData[i + 1] = 0;
        diffData[i + 2] = 0;
        diffData[i + 3] = 255;
      } else {
        // Faint dimmed context
        const gray = Math.round((r1 * 0.299 + g1 * 0.587 + b1 * 0.114) * 0.3);
        diffData[i] = gray;
        diffData[i + 1] = gray;
        diffData[i + 2] = gray;
        diffData[i + 3] = 180;
      }
    }

    diffCtx.putImageData(diffImageData, 0, 0);
    const diffDataUrl = diffCanvas.toDataURL('image/png');

    return {
      width1: img1.naturalWidth,
      height1: img1.naturalHeight,
      width2: img2.naturalWidth,
      height2: img2.naturalHeight,
      totalPixels,
      mismatchedPixels,
      diffRatio: mismatchedPixels / totalPixels,
      diffDataUrl
    };
  }, { base64Baseline, base64Candidate, colorTolerance });
}

(async () => {
  const baselineDir = process.env.BASELINE_DIR || DEFAULT_BASELINE_DIR;
  const candidateDir = process.env.CANDIDATE_DIR || DEFAULT_CANDIDATE_DIR;
  const diffDir = process.env.DIFF_DIR || DEFAULT_DIFF_DIR;
  const diffThreshold = parseFloat(process.env.VISUAL_DIFF_THRESHOLD || String(DEFAULT_DIFF_THRESHOLD));
  const colorTolerance = parseInt(process.env.PIXEL_COLOR_TOLERANCE || String(DEFAULT_COLOR_TOLERANCE), 10);

  process.stdout.write(`========================================================\n`);
  process.stdout.write(`CaroAI Automated Visual Regression Test\n`);
  process.stdout.write(`Baseline : ${baselineDir}\n`);
  process.stdout.write(`Candidate: ${candidateDir}\n`);
  process.stdout.write(`Diffs    : ${diffDir}\n`);
  process.stdout.write(`Threshold: ${(diffThreshold * 100).toFixed(2)}% | Tolerance: ${colorTolerance}\n`);
  process.stdout.write(`========================================================\n\n`);

  await fs.mkdir(diffDir, { recursive: true });

  let baselineFiles = [];
  try {
    const entries = await fs.readdir(baselineDir);
    baselineFiles = entries.filter(f => f.endsWith('.png')).sort();
  } catch (err) {
    console.error(`Failed to read baseline directory "${baselineDir}":`, err.message);
    process.exit(1);
  }

  if (baselineFiles.length === 0) {
    console.error(`Error: No baseline PNG screenshots found in "${baselineDir}".`);
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  let failedCount = 0;
  const results = [];

  try {
    for (const filename of baselineFiles) {
      const baselinePath = path.join(baselineDir, filename);
      const candidatePath = path.join(candidateDir, filename);

      let candidateExists = false;
      try {
        await fs.access(candidatePath);
        candidateExists = true;
      } catch {
        candidateExists = false;
      }

      if (!candidateExists) {
        process.stdout.write(`[FAIL] ${filename}: Missing in candidate directory!\n`);
        failedCount++;
        results.push({ filename, passed: false, reason: 'Missing in candidate' });
        continue;
      }

      const baselineBuf = await fs.readFile(baselinePath);
      const candidateBuf = await fs.readFile(candidatePath);

      const res = await compareImagesInBrowser(page, baselineBuf, candidateBuf, colorTolerance);
      const diffPercent = (res.diffRatio * 100).toFixed(2);
      const passed = res.diffRatio <= diffThreshold;

      if (!passed) {
        failedCount++;
      }

      // Save diff image if there are mismatched pixels
      if (res.mismatchedPixels > 0) {
        const base64Data = res.diffDataUrl.replace(/^data:image\/png;base64,/, '');
        await fs.writeFile(path.join(diffDir, filename), Buffer.from(base64Data, 'base64'));
      }

      const statusTag = passed ? 'PASS' : 'FAIL';
      process.stdout.write(
        `[${statusTag}] ${filename.padEnd(28)} ` +
        `Diff: ${diffPercent.padStart(5)}% ` +
        `(${res.mismatchedPixels.toLocaleString()} / ${res.totalPixels.toLocaleString()} px) ` +
        `[Dim: ${res.width1}x${res.height1} vs ${res.width2}x${res.height2}]\n`
      );

      results.push({
        filename,
        passed,
        diffPercent,
        mismatchedPixels: res.mismatchedPixels,
        totalPixels: res.totalPixels
      });
    }
  } finally {
    await browser.close();
  }

  process.stdout.write(`\n--------------------------------------------------------\n`);
  process.stdout.write(`Visual Regression Summary: ${baselineFiles.length - failedCount} Passed, ${failedCount} Failed (out of ${baselineFiles.length})\n`);
  process.stdout.write(`--------------------------------------------------------\n`);

  if (failedCount > 0) {
    process.stderr.write(`Visual regression test FAILED with ${failedCount} mismatch(es) exceeding ${(diffThreshold * 100).toFixed(2)}% threshold.\n`);
    process.stderr.write(`Inspect diff images in "${diffDir}" for visual changes.\n`);
    process.stderr.write(`To update baseline with approved candidate images:\n`);
    process.stderr.write(`  node -e "require('fs').cpSync('${candidateDir}', '${baselineDir}', {recursive: true})"\n`);
    process.exit(1);
  } else {
    process.stdout.write(`Visual regression test PASSED. All screenshots match within ${(diffThreshold * 100).toFixed(2)}% tolerance.\n\n`);
  }
})().catch(err => {
  console.error('Unexpected error during visual regression test:', err);
  process.exit(1);
});
