const { test, expect } = require('./fixtures');

test('FAQ answers expand one at a time', async ({ page }) => {
  await page.goto('/faq.html');
  const questions = page.locator('dl dt');
  const answers = page.locator('dl dd');
  expect(await questions.count()).toBeGreaterThan(2);
  for (let i = 0; i < await answers.count(); i += 1) {
    await expect(answers.nth(i)).toBeHidden();
  }

  await questions.nth(0).click();
  await expect(answers.nth(0)).toBeVisible();
  await expect(questions.nth(0).locator('.glyphiconRight')).toHaveClass(/glyphicon-chevron-down/);

  await questions.nth(1).click();
  await expect(answers.nth(1)).toBeVisible();
  await expect(answers.nth(0)).toBeHidden();

  await questions.nth(1).click();
  await expect(answers.nth(1)).toBeHidden();
});
