export const ALL_PASSED = 'ASSERTS TESTS - OK.';
export const PASSED = 'green';
export const FAILED = 'darkred';

/**
 * Colours of the assert list after a run (same rules as the former page):
 * all green when the tests printed the OK marker; otherwise the assert quoted
 * in the traceback and every following one are red, the preceding ones green.
 */
export function assertColors(output, asserts) {
  if (output === ALL_PASSED) return asserts.map(() => PASSED);
  const match = output.match(/assert .*/);
  const failing = match ? match[0].trim() : undefined;
  let color = PASSED;
  return asserts.map((assertion) => {
    if (failing === assertion.trim()) color = FAILED;
    return color;
  });
}
