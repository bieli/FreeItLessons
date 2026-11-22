// Shared `test`: on the React UI any uncaught JavaScript error and any resource
// blocked by the Content Security Policy fails the test (the jQuery UI is known
// to throw - e.g. edit_area's missing change_code callback - and has no CSP).
const base = require('@playwright/test');

const test = base.test.extend({
  pageErrors: [async ({ page }, use, testInfo) => {
    const errors = [];
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('console', (message) => {
      if (message.type() === 'error' && /Content Security Policy/i.test(message.text())) {
        errors.push(`CSP: ${message.text()}`);
      }
    });
    await use(errors);
    if (testInfo.project.name !== 'jquery') {
      base.expect(errors, 'uncaught JavaScript errors or CSP violations in the page').toEqual([]);
    } else if (errors.length) {
      testInfo.annotations.push({ type: 'page errors (jquery)', description: errors.join(' | ') });
    }
  }, { auto: true }],
});

module.exports = { test, expect: base.expect };
