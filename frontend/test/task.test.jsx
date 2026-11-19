import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, expect, it, vi } from 'vitest';
import TaskWorkspace from '../src/components/task/TaskWorkspace';
import { mockFetch, setContext, STUDENT } from './utils';

// the editor itself is CodeMirror; here a textarea stands in for it
vi.mock('../src/components/task/CodeEditor', () => ({
  default: ({ id, initialValue, editorRef }) => {
    const ref = (el) => { if (el && editorRef) editorRef.current = { getValue: () => el.value }; };
    return <textarea id={id} aria-label="code" defaultValue={initialValue} ref={ref} />;
  },
}));

const TESTS = "# tests\ndef __run_tests():\n    assert 'X' == f('X')\n    assert 'ab' == f('ba')\n    print('ASSERTS TESTS - OK.')\n# tests";
const PROPS = { taskId: 1, code: 'def f(x):\n    return x', tests: TESTS, asserts: ["assert 'X' == f('X')", "assert 'ab' == f('ba')"] };
const decode = (b64) => atob(b64);

beforeEach(() => setContext(STUDENT));

it('runs the starter code on open and colours the asserts', async () => {
  const calls = mockFetch({
    'POST /zadania/task/code/run/': [200, "Traceback\n    assert 'ab' == f('ba')\nAssertionError"],
  });
  render(<TaskWorkspace {...PROPS} />);
  await waitFor(() => expect(document.getElementById('program_output')).toHaveTextContent('AssertionError'));
  const body = calls[0].body;
  expect(decode(body.get('code'))).toBe(PROPS.code);
  expect(decode(body.get('tests'))).toBe(TESTS);
  expect(body.get('hint_id')).toBe('0');
  expect(body.get('timer')).toMatch(/^\d\d:\d\d:\d\d$/);
  expect(body.get('user_id')).toBe('2');
  const blocks = document.querySelectorAll('#asserts_list blockquote');
  expect(blocks[0].style.background).toBe('green');
  expect(blocks[1].style.background).toBe('darkred');
  expect(document.querySelectorAll('#source_tests_block span[class*=tok-]').length).toBeGreaterThan(3);
});

it('a correct solution turns all asserts green', async () => {
  mockFetch({ 'POST /zadania/task/code/run/': (call) => [200, call.body.get('code') === btoa('ok') ? 'ASSERTS TESTS - OK.' : 'x'] });
  const user = userEvent.setup();
  render(<TaskWorkspace {...PROPS} />);
  const editor = screen.getByLabelText('code');
  await user.clear(editor);
  await user.type(editor, 'ok');
  await user.click(screen.getByRole('button', { name: /Uruchom program/ }));
  await waitFor(() => expect(document.getElementById('program_output')).toHaveTextContent('ASSERTS TESTS - OK.'));
  document.querySelectorAll('#asserts_list blockquote').forEach((block) => expect(block.style.background).toBe('green'));
});

it('characters the server cannot accept are reported, not sent', async () => {
  const calls = mockFetch({ 'POST /zadania/task/code/run/': [200, 'x'] });
  const user = userEvent.setup();
  render(<TaskWorkspace {...PROPS} />);
  await waitFor(() => expect(calls).toHaveLength(1));
  await user.type(screen.getByLabelText('code'), '# żółw');
  await user.click(screen.getByRole('button', { name: /Uruchom program/ }));
  expect(document.getElementById('program_output')).toHaveTextContent('Program zawiera znak "ż"');
  expect(calls).toHaveLength(1);
});

it('server errors are shown in the output', async () => {
  mockFetch({ 'POST /zadania/task/code/run/': [400, 'wrong timer'] });
  render(<TaskWorkspace {...PROPS} />);
  await waitFor(() => expect(document.getElementById('program_output'))
    .toHaveTextContent('ERROR IN SERVER RESPONSE -> status: "HTTP 400"'));
  expect(document.getElementById('program_output').style.background).toBe('darkred');
});

it('hints unlock one by one and are sent with the next run', async () => {
  const calls = mockFetch({
    'POST /zadania/task/code/run/': [200, 'x'],
    'POST /zadania/task/code/hint/': (call) => [200, call.body.get('hint_id') === '1' ? '<p>use slicing</p>' : 'plain hint'],
  });
  const user = userEvent.setup();
  render(<TaskWorkspace {...PROPS} />);
  expect(screen.getByRole('button', { name: 'Poproszę o podpowiedź 2' })).toHaveClass('disabled');
  await user.click(screen.getByRole('button', { name: 'Poproszę o podpowiedź 2' }));
  expect(calls.filter((call) => call.path.endsWith('hint/'))).toHaveLength(0);

  await user.click(screen.getByRole('button', { name: 'Poproszę o podpowiedź 1' }));
  const hint = document.getElementById('source_task_hint_content');
  await waitFor(() => expect(hint).toHaveTextContent('Podpowiedźuse slicing'));
  expect(hint.querySelector('strong')).toHaveTextContent('Podpowiedź');
  expect(document.getElementById('source_task_code')).toHaveClass('col-md-6');
  expect(screen.getByRole('button', { name: 'Poproszę o podpowiedź 2' })).not.toHaveClass('disabled');

  await user.click(screen.getByRole('button', { name: 'Poproszę o podpowiedź 2' }));
  await waitFor(() => expect(hint).toHaveTextContent('### Podpowiedź ### ---- plain hint'));
  await user.click(screen.getByRole('button', { name: /Uruchom program/ }));
  await waitFor(() => expect(calls.filter((call) => call.path.endsWith('run/'))).toHaveLength(2));
  expect(calls.filter((call) => call.path.endsWith('run/'))[1].body.get('hint_id')).toBe('2');
});
