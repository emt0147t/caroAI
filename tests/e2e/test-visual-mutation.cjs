const fs = require('node:fs/promises');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { chromium } = require('@playwright/test');

const TEST_DIR = path.join('evidence', '_mutation_test');
const BASELINE_DIR = path.join(TEST_DIR, 'baseline');
const CANDIDATE_DIR = path.join(TEST_DIR, 'candidate');
const DIFF_DIR = path.join(TEST_DIR, 'diff');

async function createTestImage(page, width, height, drawFn) {
  return await page.evaluate(async ({ width, height, drawFnStr }) => {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    
    // Default blue fill
    ctx.fillStyle = '#2563eb';
    ctx.fillRect(0, 0, width, height);

    if (drawFnStr) {
      const fn = eval('(' + drawFnStr + ')');
      fn(ctx, width, height);
    }

    const dataUrl = canvas.toDataURL('image/png');
    return dataUrl.replace(/^data:image\/png;base64,/, '');
  }, { width, height, drawFnStr: drawFn ? drawFn.toString() : null });
}

function runComparator(envOverrides = {}) {
  const env = {
    ...process.env,
    BASELINE_DIR,
    CANDIDATE_DIR,
    DIFF_DIR,
    VISUAL_DIFF_THRESHOLD: '0.02',
    ...envOverrides
  };

  return spawnSync('node', ['tests/e2e/compare-visual-evidence.cjs'], {
    env,
    encoding: 'utf-8'
  });
}

(async () => {
  process.stdout.write(`======================================================================\n`);
  process.stdout.write(`CaroAI Visual Regression Mutation Test Suite\n`);
  process.stdout.write(`Verifying deliberate visual changes & dimension mismatches cause failure\n`);
  process.stdout.write(`======================================================================\n\n`);

  await fs.rm(TEST_DIR, { recursive: true, force: true });
  await fs.mkdir(BASELINE_DIR, { recursive: true });
  await fs.mkdir(CANDIDATE_DIR, { recursive: true });
  await fs.mkdir(DIFF_DIR, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  let passedChecks = 0;
  let totalChecks = 0;

  try {
    // Generate valid dummy mobile dark evidence so Section 1 passes
    const dummyMobileDark = await createTestImage(page, 390, 844);
    await fs.writeFile(path.join(CANDIDATE_DIR, 'dark-start-390x844.png'), Buffer.from(dummyMobileDark, 'base64'));
    await fs.writeFile(path.join(CANDIDATE_DIR, 'dark-game-390x844.png'), Buffer.from(dummyMobileDark, 'base64'));
    await fs.writeFile(path.join(CANDIDATE_DIR, 'dark-history-390x844.png'), Buffer.from(dummyMobileDark, 'base64'));

    // Check 1: Identical baseline and candidate must PASS (exit code 0)
    totalChecks++;
    process.stdout.write(`[Test 1] Identical baseline and candidate images...\n`);
    const baseImg = await createTestImage(page, 200, 200);
    await fs.writeFile(path.join(BASELINE_DIR, 'sample.png'), Buffer.from(baseImg, 'base64'));
    await fs.writeFile(path.join(CANDIDATE_DIR, 'sample.png'), Buffer.from(baseImg, 'base64'));

    const res1 = runComparator();
    if (res1.status === 0) {
      process.stdout.write(`  ✔ PASS: Comparator exited with code 0 on identical images.\n`);
      passedChecks++;
    } else {
      process.stderr.write(`  ✘ FAIL: Comparator exited with code ${res1.status} on identical images!\n${res1.stdout}\n${res1.stderr}\n`);
    }

    // Check 2: Deliberate visual mutation > 2% must FAIL (exit code 1) and create diff
    totalChecks++;
    process.stdout.write(`[Test 2] Deliberate visual pixel mutation (>2% threshold)...\n`);
    // Mutate 20% of image area (50x80px = 4,000 / 40,000 = 10%)
    const mutatedImg = await createTestImage(page, 200, 200, (ctx) => {
      ctx.fillStyle = '#dc2626';
      ctx.fillRect(0, 0, 50, 80);
    });
    await fs.writeFile(path.join(CANDIDATE_DIR, 'sample.png'), Buffer.from(mutatedImg, 'base64'));

    const res2 = runComparator();
    const diffExists = await fs.access(path.join(DIFF_DIR, 'sample.png')).then(() => true).catch(() => false);

    if (res2.status !== 0 && diffExists) {
      process.stdout.write(`  ✔ PASS: Visual mutation detected (exit code ${res2.status}) and diff image generated.\n`);
      passedChecks++;
    } else {
      process.stderr.write(`  ✘ FAIL: Mutation was not caught! status=${res2.status}, diffExists=${diffExists}\n${res2.stdout}\n${res2.stderr}\n`);
    }

    // Check 3: Strict image dimension mismatch must FAIL (reject silent padding)
    totalChecks++;
    process.stdout.write(`[Test 3] Image dimension mismatch (strict rejection of silent padding)...\n`);
    const dimensionMismatchImg = await createTestImage(page, 200, 205);
    await fs.writeFile(path.join(CANDIDATE_DIR, 'sample.png'), Buffer.from(dimensionMismatchImg, 'base64'));

    const res3 = runComparator();
    if (res3.status !== 0 && res3.stdout.includes('DIMENSION MISMATCH')) {
      process.stdout.write(`  ✔ PASS: Dimension mismatch detected and rejected without silent padding.\n`);
      passedChecks++;
    } else {
      process.stderr.write(`  ✘ FAIL: Dimension mismatch did not fail properly! status=${res3.status}\n${res3.stdout}\n${res3.stderr}\n`);
    }

    // Check 4: Missing candidate file must FAIL
    totalChecks++;
    process.stdout.write(`[Test 4] Baseline image missing in candidate...\n`);
    await fs.unlink(path.join(CANDIDATE_DIR, 'sample.png'));

    const res4 = runComparator();
    if (res4.status !== 0 && res4.stdout.toLowerCase().includes('missing in candidate')) {
      process.stdout.write(`  ✔ PASS: Missing candidate file detected and flagged.\n`);
      passedChecks++;
    } else {
      process.stderr.write(`  ✘ FAIL: Missing candidate file was not caught! status=${res4.status}\n${res4.stdout}\n${res4.stderr}\n`);
    }

  } finally {
    await browser.close();
    await fs.rm(TEST_DIR, { recursive: true, force: true });
  }

  process.stdout.write(`\n======================================================================\n`);
  process.stdout.write(`Mutation Test Summary: ${passedChecks}/${totalChecks} checks passed.\n`);
  process.stdout.write(`======================================================================\n`);

  if (passedChecks !== totalChecks) {
    process.exit(1);
  }
})().catch(err => {
  console.error('Unexpected error during mutation test:', err);
  process.exit(1);
});
