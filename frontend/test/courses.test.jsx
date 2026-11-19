import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import ContentBlock from '../src/components/courses/ContentBlock';
import { mockFetch, setContext, STUDENT } from './utils';

const HTML = '<p>Lesson <a href="#python">link</a></p>';

it('anonymous visitor is asked to log in', async () => {
  setContext({});
  const alert = vi.spyOn(window, 'alert').mockImplementation(() => {});
  const calls = mockFetch({});
  const { container } = render(<ContentBlock contentId="5" html={HTML} />);
  await userEvent.click(container.querySelector('blockquote'));
  expect(alert).toHaveBeenCalledWith('W celu wystawienia oceny kontekstu musisz być zalogowany !');
  expect(calls).toHaveLength(0);
  expect(screen.queryByRole('dialog')).toBeNull();
});

it('student: shows stored opinion, rates, validates the choice', async () => {
  setContext(STUDENT);
  const alert = vi.spyOn(window, 'alert').mockImplementation(() => {});
  const calls = mockFetch({ 'GET /content/user/': [200, 'doit'], 'POST /content/user/status/': [200, 'OK'] });
  const user = userEvent.setup();
  const { container } = render(<ContentBlock contentId="5" html={HTML} />);
  const block = container.querySelector('#content_id__5');
  await waitFor(() => expect(block.style.backgroundImage).toContain('/static/mainapp/img/doit.png'));
  expect(calls[0].url).toBe('/content/user/?user_id=2&content_id=5');

  await user.click(screen.getByRole('link', { name: 'link' })); // links inside the content do not rate
  expect(screen.queryByRole('dialog')).toBeNull();

  await user.click(block);
  const dialog = screen.getByRole('dialog', { name: 'Ocena wskazanego konspektu' });
  expect(dialog.querySelectorAll('input[name=dialog-send-status-select]')).toHaveLength(5);
  await user.click(screen.getByRole('button', { name: 'Prześlij opinię' }));
  expect(alert).toHaveBeenCalledWith('Proszę wskazać jedną opcję !');

  await user.click(screen.getByRole('radio', { name: /nadążam/ }));
  await user.click(screen.getByRole('button', { name: 'Prześlij opinię' }));
  expect(screen.queryByRole('dialog')).toBeNull();
  await waitFor(() => expect(block.style.backgroundImage).toContain('good.png'));
  const post = calls.find((call) => call.method === 'POST');
  expect(Object.fromEntries(post.body)).toEqual({ user_id: '2', content_id: '5', status: 'good', csrfmiddlewaretoken: 'TOKEN' });
});

it('cancel and Escape close the dialog without saving', async () => {
  setContext(STUDENT);
  const calls = mockFetch({ 'GET /content/user/': [400, 'content NOT EXISTS'] });
  const user = userEvent.setup();
  const { container } = render(<ContentBlock contentId="5" html={HTML} />);
  await user.click(container.querySelector('blockquote'));
  await user.click(screen.getByRole('button', { name: 'Cancel' }));
  expect(screen.queryByRole('dialog')).toBeNull();
  await user.click(container.querySelector('blockquote'));
  await user.keyboard('{Escape}');
  expect(screen.queryByRole('dialog')).toBeNull();
  expect(calls.filter((call) => call.method === 'POST')).toHaveLength(0);
});
