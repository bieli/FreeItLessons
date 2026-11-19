const { test, expect } = require('./fixtures');
const { rotation } = require('./helpers');

test('status icons rotate into place', async ({ page }) => {
  await page.goto('/');
  const expected = { img1: 30, img2: -10, img3: -20, img4: 15, img5: 45 };
  for (const [id, angle] of Object.entries(expected)) {
    await expect.poll(() => rotation(page.locator(`#${id}`)), { timeout: 10_000 }).toBe(angle);
  }
});

test('floating background decoration is animated', async ({ page }) => {
  await page.goto('/');
  const floating = page.locator('.float-container > div');
  await expect.poll(() => floating.count()).toBeGreaterThanOrEqual(2);
  expect(await floating.first().evaluate((el) => getComputedStyle(el).animationName)).toBe('float');
});
