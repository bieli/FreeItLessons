const { test, expect } = require('./fixtures');
const { STUDENT, login, knownJqueryBug } = require('./helpers');

const nav = (page, name) => page.locator('.navbar').getByRole('link', { name, exact: true });
// a page without extra scripts (on the home page the jQuery UI loads Bootstrap JS twice)
const PLAIN_PAGE = '/mentorzy.html';

async function checkUserDropdown(page) {
  const opinions = nav(page, 'Moje oceny kursu');
  await expect(opinions).toBeHidden();
  await page.locator('.navbar').getByText('Zalogowany').click();
  await expect(opinions).toBeVisible();
  await expect(nav(page, 'Zmień hasło')).toBeVisible();
}

async function checkMobileToggle(page) {
  const courses = nav(page, 'Kursy');
  await expect(courses).toBeHidden();
  await page.getByRole('button', { name: 'Toggle navigation' }).click();
  await expect(courses).toBeVisible();
  await page.waitForTimeout(600); // let the open animation finish, as a person would
  await page.getByRole('button', { name: 'Toggle navigation' }).click();
  await expect(courses).toBeHidden();
}

test('anonymous visitor sees the public menu and the login link', async ({ page }) => {
  await page.goto('/');
  for (const name of ['Pytania i odpowiedzi', 'Mentorzy', 'Kursy']) {
    await expect(nav(page, name)).toBeVisible();
  }
  await expect(nav(page, 'Zadania')).toHaveCount(0);
  await nav(page, 'Zaloguj się').click();
  await expect(page).toHaveURL(/\/admin\/login\/\?next=\//);
});

test('student menu: tasks link, user dropdown and navigation', async ({ page }) => {
  await login(page);
  await page.goto(PLAIN_PAGE);
  await expect(page.locator('.navbar')).toContainText(`Zalogowany ${STUDENT}`);
  await expect(nav(page, 'Zadania')).toBeVisible();
  await checkUserDropdown(page);
  await nav(page, 'Osiągnięcia').click();
  await expect(page).toHaveURL(/\/achievements\/$/);
  await expect(page.getByText('Liczba zdobytych punktów')).toBeVisible();
});

test('user dropdown on the home page', async ({ page }, testInfo) => {
  knownJqueryBug(test, testInfo, 'home.html loads jQuery + Bootstrap JS a second time, the dropdown opens and closes at once');
  await login(page);
  await page.goto('/');
  await checkUserDropdown(page);
});

test('logout from the header', async ({ page }) => {
  await login(page);
  await nav(page, 'Wyloguj').click();
  await page.goto('/');
  await expect(nav(page, 'Zaloguj się')).toBeVisible();
  await expect(page.getByText('Zalogowany')).toHaveCount(0);
});

test('mobile: the menu collapses behind the toggle button', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 800 });
  await page.goto(PLAIN_PAGE);
  await checkMobileToggle(page);
});

test('mobile: menu toggle on the home page', async ({ page }, testInfo) => {
  knownJqueryBug(test, testInfo, 'home.html loads Bootstrap JS twice, the collapsed menu cannot be closed again');
  await page.setViewportSize({ width: 375, height: 800 });
  await page.goto('/');
  await checkMobileToggle(page);
});
