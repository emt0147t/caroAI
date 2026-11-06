const fs = require('node:fs/promises');
const fsSync = require('node:fs');
const path = require('node:path');
const { chromium } = require('@playwright/test');

const DEFAULT_BASELINE_DIR = fsSync.existsSync(path.join('evidence', 'before'))
  ? path.join('evidence', 'before')
  : path.join('evidence', 'baseline');
const DEFAULT_CANDIDATE_DIR = path.join('evidence', 'candidate');
const DEFAULT_DIFF_DIR = path.join('evidence', 'diff');
const DEFAULT_DIFF_THRESHOLD = 0.02; // 2.0% strict threshold for unchanged screens
const DEFAULT_COLOR_TOLERANCE = 25; // RGB channel delta tolerance for anti-aliasing

// New evidence files introduced in A1.1: base application does not have equivalent mobile dark captures
const NEW_MOBILE_DARK_EVIDENCE = [
  'dark-start-390x844.png',
  'dark-game-390x844.png',
  'dark-history-390x844.png'
];

// Documented, approved visual changes between base and candidate.
// Cell sizing increased to min 24x24px for WCAG 2.2 SC 2.5.8 compliance, resulting in ~17-18% diff.
const APPROVED_EXCEPTIONS = {
  'game-390x844.png': {
    maxDiff: 0.20,
    reason: 'A1-03: WCAG 2.2 SC 2.5.8 mobile board cell sizing (min 24px) and layout safe-centering'
  },
  'dark-game-390x844.png': {
    maxDiff: 0.20,
    reason: 'A1-03: WCAG 2.2 SC 2.5.8 dark mobile board cell sizing (min 24px) and safe-centering'
  }
};

async function getImageDimensions(page, buf) {
  const base64 = buf.toString('base64');
  return await page.evaluate(async (base64) => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve({ width: img.naturalWidth, height: img.naturalHeight });
      img.onerror = reject;
      img.src = 'data:image/png;base64,' + base64;
    });
  }, base64);
}

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

    const width1 = img1.naturalWidth;
    const height1 = img1.naturalHeight;
    const width2 = img2.naturalWidth;
    const height2 = img2.naturalHeight;

    // Strict image-dimension validation: do not silently pad images
    if (width1 !== width2 || height1 !== height2) {
      return {
        dimensionMismatch: true,
        width1,
        height1,
        width2,
        height2,
        totalPixels: 0,
        mismatchedPixels: 0,
        diffRatio: 1.0,
        diffDataUrl: null
      };
    }

    const width = width1;
    const height = height1;

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
        // High-visibility red for diff
        diffData[i] = 255;
        diffData[i + 1] = 0;
        diffData[i + 2] = 0;
        diffData[i + 3] = 255;
      } else {
        // Dimmed grayscale background context
        const gray = Math.round((r1 * 0.299 + g1 * 0.587 + b1 * 0.114) * 0.3);
        diffData[i] = gray;
        diffData[i + 1] = gray;
        diffData[i + 2] = gray;
        diffData[i + 3] = 160;
      }
    }

    diffCtx.putImageData(diffImageData, 0, 0);
    const diffDataUrl = diffCanvas.toDataURL('image/png');

    return {
      dimensionMismatch: false,
      width1,
      height1,
      width2,
      height2,
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
  const defaultDiffThreshold = parseFloat(process.env.VISUAL_DIFF_THRESHOLD || String(DEFAULT_DIFF_THRESHOLD));
  const colorTolerance = parseInt(process.env.PIXEL_COLOR_TOLERANCE || String(DEFAULT_COLOR_TOLERANCE), 10);

  process.stdout.write(`======================================================================\n`);
  process.stdout.write(`CaroAI Automated Visual Regression Pipeline\n`);
  process.stdout.write(`Baseline : ${baselineDir}\n`);
  process.stdout.write(`Candidate: ${candidateDir}\n`);
  process.stdout.write(`Diffs    : ${diffDir}\n`);
  process.stdout.write(`Default Threshold: ${(defaultDiffThreshold * 100).toFixed(2)}% | Tolerance: ${colorTolerance}\n`);
  process.stdout.write(`======================================================================\n\n`);

  await fs.mkdir(diffDir, { recursive: true });

  let baselineEntries = [];
  try {
    baselineEntries = await fs.readdir(baselineDir);
  } catch (err) {
    console.error(`Failed to read baseline directory "${baselineDir}":`, err.message);
    process.exit(1);
  }

  let candidateEntries = [];
  try {
    candidateEntries = await fs.readdir(candidateDir);
  } catch (err) {
    console.error(`Failed to read candidate directory "${candidateDir}":`, err.message);
    process.exit(1);
  }

  const baselineFiles = new Set(baselineEntries.filter(f => f.endsWith('.png')));
  const candidateFiles = new Set(candidateEntries.filter(f => f.endsWith('.png')));

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  let failedCount = 0;
  let passedCount = 0;
  let newEvidenceCount = 0;

  try {
    // 1. Validate newly introduced mobile dark-mode evidence independently
    process.stdout.write(`[SECTION 1: Mobile Dark Mode Evidence Validation (Task A1-05)]\n`);
    for (const filename of NEW_MOBILE_DARK_EVIDENCE) {
      if (!candidateFiles.has(filename)) {
        process.stdout.write(`  [FAIL] ${filename.padEnd(28)} Missing in candidate directory!\n`);
        failedCount++;
        continue;
      }

      const candidatePath = path.join(candidateDir, filename);
      const candidateBuf = await fs.readFile(candidatePath);
      const dims = await getImageDimensions(page, candidateBuf);

      if (dims.width !== 390 || dims.height < 844) {
        process.stdout.write(
          `  [FAIL] ${filename.padEnd(28)} Invalid mobile dimensions: ${dims.width}x${dims.height} (expected 390x844+)\n`
        );
        failedCount++;
      } else {
        process.stdout.write(
          `  [PASS] ${filename.padEnd(28)} Validated new evidence (Dim: ${dims.width}x${dims.height} px)\n`
        );
        newEvidenceCount++;
      }
    }
    process.stdout.write(`\n`);

    // 2. Identify common filenames between baseline and candidate
    // Files present in baseline that should be compared
    process.stdout.write(`[SECTION 2: Baseline vs Candidate Visual Regression]\n`);
    const commonFiles = Array.from(baselineFiles).filter(f => candidateFiles.has(f)).sort();
    const missingInCandidate = Array.from(baselineFiles).filter(f => !candidateFiles.has(f));

    for (const missing of missingInCandidate) {
      process.stdout.write(`  [FAIL] ${missing.padEnd(28)} Present in baseline but missing in candidate!\n`);
      failedCount++;
    }

    for (const filename of commonFiles) {
      const baselinePath = path.join(baselineDir, filename);
      const candidatePath = path.join(candidateDir, filename);

      const baselineBuf = await fs.readFile(baselinePath);
      const candidateBuf = await fs.readFile(candidatePath);

      const res = await compareImagesInBrowser(page, baselineBuf, candidateBuf, colorTolerance);

      if (res.dimensionMismatch) {
        process.stdout.write(
          `  [FAIL] ${filename.padEnd(28)} DIMENSION MISMATCH: ` +
          `baseline ${res.width1}x${res.height1} vs candidate ${res.width2}x${res.height2}\n`
        );
        failedCount++;
        continue;
      }

      const exception = APPROVED_EXCEPTIONS[filename];
      const threshold = exception ? exception.maxDiff : defaultDiffThreshold;
      const diffPercent = (res.diffRatio * 100).toFixed(3);
      const passed = res.diffRatio <= threshold;

      if (!passed) {
        failedCount++;
      } else {
        passedCount++;
      }

      if (res.mismatchedPixels > 0 && res.diffDataUrl) {
        const base64Data = res.diffDataUrl.replace(/^data:image\/png;base64,/, '');
        await fs.writeFile(path.join(diffDir, filename), Buffer.from(base64Data, 'base64'));
      }

      const statusTag = passed ? 'PASS' : 'FAIL';
      const note = exception ? ` [Approved diff cap: ${(threshold * 100).toFixed(1)}% | ${exception.reason}]` : '';
      process.stdout.write(
        `  [${statusTag}] ${filename.padEnd(28)} ` +
        `Diff: ${diffPercent.padStart(7)}% ` +
        `(${res.mismatchedPixels.toLocaleString()} / ${res.totalPixels.toLocaleString()} px) ` +
        `[Dim: ${res.width1}x${res.height1}]${note}\n`
      );
    }
  } finally {
    await browser.close();
  }

  process.stdout.write(`\n======================================================================\n`);
  process.stdout.write(`Summary: ${passedCount} Baseline-matched PASS, ${newEvidenceCount} New Evidence Validated, ${failedCount} FAIL\n`);
  process.stdout.write(`======================================================================\n`);

  if (failedCount > 0) {
    process.stderr.write(`Visual regression check FAILED with ${failedCount} error(s).\n`);
    process.stderr.write(`Inspect diff images in "${diffDir}" for visual changes.\n`);
    process.stderr.write(`Note: Golden baselines must NOT be silently overwritten. Any intentional visual change requires design review.\n`);
    process.exit(1);
  } else {
    process.stdout.write(`Visual regression check PASSED. All screenshots match approved specifications.\n\n`);
  }
})().catch(err => {
  console.error('Unexpected error in visual regression comparator:', err);
  process.exit(1);
});
