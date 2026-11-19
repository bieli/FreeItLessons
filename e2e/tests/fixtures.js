// Shared `test`: on the React UI any uncaught JavaScript error fails the test
// (the jQuery UI is known to throw - e.g. edit_area's missing change_code callback).
const base = require('@playwright/test');

const test = base.test.extend({
  pageErrors: [async ({ page }, use, testInfo) => {
    const errors = [];
    page.on('pageerror', (error) => errors.push(error.message));
    await use(errors);
    if (testInfo.project.name !== 'jquery') {
      base.expect(errors, 'uncaught JavaScript errors in the page').toEqual([]);
    } else if (errors.length) {
      testInfo.annotations.push({ type: 'page errors (jquery)', description: errors.join(' | ') });
    }
  }, { auto: true }],
});

module.exports = { test, expect: base.expect };
