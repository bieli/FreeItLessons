// One project per UI implementation; every spec runs against each of them.
// E2E_TARGETS="jquery=http://baseline:8000,react=http://candidate:8000"
const { defineConfig, devices } = require('@playwright/test');

const targets = (process.env.E2E_TARGETS || 'react=http://127.0.0.1:8000')
  .split(',')
  .map((item) => item.split('='))
  .map(([name, baseURL]) => ({ name, use: { ...devices['Desktop Chrome'], baseURL } }));

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1, // tests change data (opinions, solutions) - keep them sequential
  retries: 0,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: [['list'], ['html', { outputFolder: process.env.E2E_REPORT_DIR || 'playwright-report', open: 'never' }]],
  use: { trace: 'retain-on-failure', screenshot: 'only-on-failure', locale: 'pl-PL' },
  outputDir: process.env.E2E_RESULTS_DIR || 'test-results',
  projects: targets,
});
