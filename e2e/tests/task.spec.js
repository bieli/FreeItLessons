const { test, expect } = require('./fixtures');
const { login, setEditorCode, GREEN, DARKRED } = require('./helpers');

const SOLUTION = `# unit
def reverse_chars(chars):
    if len(chars) > 10:
        return None
    return chars[::-1]
# unit
`;

test('task page: auto run, timer, highlighted tests', async ({ page }) => {
  await login(page);
  await page.goto('/zadania/1.html');
  await expect(page.getByText('Zadanie #1')).toBeVisible();

  const asserts = page.locator('#asserts_list blockquote');
  await expect(asserts).toHaveCount(4);
  // the starter code is run when the page opens - all tests fail
  await expect(page.locator('#program_output')).toContainText('AssertionError');
  for (let i = 0; i < 4; i += 1) {
    await expect(asserts.nth(i)).toHaveCSS('background-color', DARKRED);
  }

  await expect(page.locator('#timerHtml')).toHaveText(/^\d\d:\d\d:\d\d$/);
  await expect(page.locator('#timerHtml')).not.toHaveText('00:00:00', { timeout: 5000 });

  await expect(page.locator('#source_tests_block')).toContainText('def __run_tests():');
  expect(await page.locator('#source_tests_block span').count()).toBeGreaterThan(3); // syntax highlighting
  await expect(page.locator('#source_main_block')).toContainText("if __name__ == '__main__':");
});

test('task page: hints unlock one by one', async ({ page }) => {
  await login(page);
  await page.goto('/zadania/1.html');
  await expect(page.locator('#hint-2')).toHaveClass(/disabled/);
  await page.locator('#hint-1').click();
  await expect(page.locator('#source_task_hint_content')).toContainText('Podpowiedź');
  await expect(page.locator('#source_task_hint_content')).toContainText('Spróbuj napisać warunek');
  await expect(page.locator('#hint-2')).not.toHaveClass(/disabled/);
  await expect(page.locator('#hint-3')).toHaveClass(/disabled/);
});

test('task page: a correct solution passes all tests', async ({ page }) => {
  await login(page);
  await page.goto('/zadania/1.html');
  await expect(page.locator('#program_output')).toContainText('AssertionError');

  await setEditorCode(page, SOLUTION);
  await page.locator('#program_run').click();
  await expect(page.locator('#program_output')).toHaveText('ASSERTS TESTS - OK.');
  const asserts = page.locator('#asserts_list blockquote');
  for (let i = 0; i < 4; i += 1) {
    await expect(asserts.nth(i)).toHaveCSS('background-color', GREEN);
  }

  await page.goto('/zadania.html');
  const row = page.locator('h4').filter({ has: page.locator("a[href='/zadania/1.html']") });
  await expect(row).toContainText('★');
});
