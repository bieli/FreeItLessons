const { test, expect } = require('./fixtures');
const { ADMIN, login, knownJqueryBug } = require('./helpers');

test('content status list shows the statistics chart', async ({ page }, testInfo) => {
  knownJqueryBug(test, testInfo, 'content_status_stats.js uses an undefined global $ (the admin only has django.jQuery) - the chart never rendered');
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await login(page, ADMIN);
  await page.goto('/admin/mainapp/contentstatus/');
  testInfo.annotations.push({ type: 'page errors', description: errors.join(' | ') || 'none' });
  const chart = page.locator('#chart');
  await expect(chart.locator('svg')).toBeVisible();
  await expect(chart).toContainText('Content Statuses Activities');
  for (const status of ['New', 'Doit', 'Help', 'Good', 'Done']) {
    await expect(chart).toContainText(status);
  }
});
