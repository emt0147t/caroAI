const { defineConfig, devices } = require('@playwright/test');
module.exports = defineConfig({
  testDir: './tests/e2e', fullyParallel: false, forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
  timeout: 45000, expect: { timeout: 10000 },
  use: {
    baseURL: process.env.CAROAI_BASE_URL || 'http://127.0.0.1:8080',
    trace: 'retain-on-failure', screenshot: 'only-on-failure',
    video: 'retain-on-failure', ...devices['Desktop Chrome']
  },
  outputDir: 'test-results'
});
