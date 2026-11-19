const { expect } = require('@playwright/test');

const STUDENT = process.env.E2E_STUDENT || 'student';
const ADMIN = process.env.E2E_ADMIN || 'admin';
const PASSWORD = process.env.E2E_PASSWORD || 'Regression-Pass-2024!';

async function login(page, username = STUDENT) {
  await page.goto('/admin/login/?next=/');
  await page.fill('#id_username', username);
  await page.fill('#id_password', PASSWORD);
  await page.locator('#login-form [type=submit]').click();
  await expect(page.getByText('Zalogowany')).toBeVisible();
}

/** Collects window.alert() messages (and accepts them). */
function collectAlerts(page) {
  const messages = [];
  page.on('dialog', async (dialog) => {
    messages.push(dialog.message());
    await dialog.accept();
  });
  return messages;
}

/** The code editor is the replaced component: edit_area (jQuery UI) or CodeMirror (React). */
async function setEditorCode(page, code) {
  const legacy = await page.evaluate(() => typeof window.editAreaLoader !== 'undefined');
  if (legacy) {
    // edit_area keeps its own buffer and re-syncs the textarea on "run" - set both
    await page.evaluate((src) => {
      // the page configures change_callback "change_code" but defines it only in a closure
      window.change_code = window.change_code || (() => {});
      window.editAreaLoader.setValue('source_code_block', src);
      document.getElementById('source_code_block').value = src;
    }, code);
    return;
  }
  const editor = page.locator('#source_code_block .cm-content');
  await editor.click();
  await page.keyboard.press('ControlOrMeta+a');
  await page.keyboard.insertText(code);
}

/** Rotation angle (deg) of an element from its computed CSS transform. */
async function rotation(locator) {
  return locator.evaluate((el) => {
    const t = getComputedStyle(el).transform;
    if (!t || t === 'none') return 0;
    const [a, b] = t.match(/matrix\(([^)]+)\)/)[1].split(',').map(Number);
    return Math.round((Math.atan2(b, a) * 180) / Math.PI);
  });
}

/**
 * Marks a test as a known defect of the jQuery UI: Playwright then expects it
 * to FAIL there (and reports if it unexpectedly passes), while it must pass on React.
 */
function knownJqueryBug(test, testInfo, reason) {
  test.fail(testInfo.project.name === 'jquery', `known jQuery UI defect: ${reason}`);
}

const GREEN = 'rgb(0, 128, 0)';
const DARKRED = 'rgb(139, 0, 0)';

module.exports = {
  STUDENT, ADMIN, PASSWORD, login, collectAlerts, setEditorCode, rotation, knownJqueryBug, GREEN, DARKRED,
};
