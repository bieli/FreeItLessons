const { test, expect } = require('./fixtures');
const { login, collectAlerts } = require('./helpers');

const CHAPTER = '/kursy/2/rozdzial/3.html';

function firstContent(page) {
  return page.locator("blockquote[id^='content_id__']").first();
}

async function icon(locator) {
  return locator.evaluate((el) => getComputedStyle(el).backgroundImage.match(/(\w+)\.png/)[1]);
}

// click the blockquote itself (its padding), not a link/image inside the content
const clickBlock = (locator) => locator.click({ position: { x: 8, y: 8 } });

test('anonymous visitor is asked to log in before rating', async ({ page }) => {
  const alerts = collectAlerts(page);
  await page.goto(CHAPTER);
  await clickBlock(firstContent(page));
  await expect.poll(() => alerts).toEqual(['W celu wystawienia oceny kontekstu musisz być zalogowany !']);
  await expect(page.getByRole('dialog')).toHaveCount(0);
});

test('student rates a course content - icon updated and persisted', async ({ page }) => {
  const alerts = collectAlerts(page);
  await login(page);
  await page.goto(CHAPTER);
  const block = firstContent(page);
  const dialog = page.getByRole('dialog');

  await clickBlock(block);
  await expect(dialog).toBeVisible();
  await expect(dialog).toContainText('Ocena wskazanego konspektu');
  await expect(dialog.locator("input[name='dialog-send-status-select']")).toHaveCount(5);

  await dialog.getByRole('button', { name: 'Prześlij opinię' }).click();
  await expect.poll(() => alerts).toEqual(['Proszę wskazać jedną opcję !']);
  await expect(dialog).toBeVisible();

  await dialog.locator("input[name='dialog-send-status-select'][value='good']").check();
  await dialog.getByRole('button', { name: 'Prześlij opinię' }).click();
  await expect(dialog).toBeHidden();
  await expect.poll(() => icon(block)).toBe('good');

  await page.reload();
  await expect.poll(() => icon(firstContent(page))).toBe('good');
});

test('cancel keeps the previous rating', async ({ page }) => {
  await login(page);
  await page.goto(CHAPTER);
  const block = firstContent(page);
  await clickBlock(block);
  const dialog = page.getByRole('dialog');
  await dialog.locator("input[name='dialog-send-status-select'][value='help']").check();
  await dialog.getByRole('button', { name: 'Prześlij opinię' }).click();
  await expect.poll(() => icon(block)).toBe('help');

  await clickBlock(block);
  await dialog.locator("input[name='dialog-send-status-select'][value='done']").check();
  await dialog.getByRole('button', { name: 'Cancel' }).click();
  await expect(dialog).toBeHidden();
  await page.reload();
  await expect.poll(() => icon(firstContent(page))).toBe('help');
});
