import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import NavBar from '../src/components/layout/NavBar';
import FaqAccordion from '../src/components/faq/FaqAccordion';
import { setContext, STUDENT } from './utils';

describe('NavBar', () => {
  it('anonymous: public links and login', () => {
    setContext({});
    render(<NavBar />);
    expect(screen.getByRole('link', { name: 'Kursy' })).toHaveAttribute('href', '/kursy.html');
    expect(screen.queryByRole('link', { name: 'Zadania' })).toBeNull();
    expect(screen.getByRole('link', { name: 'Zaloguj się' })).toHaveAttribute('href', '/admin/login/?next=/');
  });

  it('student: dropdown opens, closes on outside click; logout posts the form', async () => {
    setContext(STUDENT);
    const user = userEvent.setup();
    const { container } = render(<NavBar />);
    const toggle = screen.getByRole('button', { name: /Zalogowany/ });
    expect(toggle.closest('li')).not.toHaveClass('open');
    await user.click(toggle);
    expect(toggle.closest('li')).toHaveClass('open');
    await user.click(document.body);
    expect(toggle.closest('li')).not.toHaveClass('open');

    const form = container.querySelector('form[action="/admin/logout/"]');
    expect(form).toHaveAttribute('method', 'post');
    expect(form.querySelector('[name=csrfmiddlewaretoken]')).toHaveValue('TOKEN');
    const submit = vi.spyOn(HTMLFormElement.prototype, 'submit').mockImplementation(() => {});
    await user.click(screen.getByRole('link', { name: 'Wyloguj' }));
    expect(submit).toHaveBeenCalled();
  });

  it('mobile toggle shows and hides the menu', async () => {
    setContext({});
    const user = userEvent.setup();
    const { container } = render(<NavBar />);
    const menu = container.querySelector('#navbarNavDropdown');
    await user.click(screen.getByRole('button', { name: 'Toggle navigation' }));
    expect(menu).toHaveClass('in');
    await user.click(screen.getByRole('button', { name: 'Toggle navigation' }));
    expect(menu).not.toHaveClass('in');
  });
});

describe('FaqAccordion', () => {
  it('opens one answer at a time', async () => {
    vi.useFakeTimers();
    const faqs = [{ id: 1, question: 'Q1', answer: '<b>A1</b>' }, { id: 2, question: 'Q2', answer: 'A2' }];
    const { container } = render(<FaqAccordion faqs={faqs} />);
    const [dd1, dd2] = container.querySelectorAll('dd');
    expect(dd1).toHaveStyle({ display: 'none' });
    expect(dd1.querySelector('b')).toHaveTextContent('A1');

    act(() => container.querySelectorAll('dt')[0].click());
    act(() => vi.advanceTimersByTime(500));
    expect(dd1).not.toHaveStyle({ display: 'none' });
    expect(container.querySelector('dt .glyphiconRight')).toHaveClass('glyphicon-chevron-down');

    act(() => container.querySelectorAll('dt')[1].click());
    act(() => vi.advanceTimersByTime(500));
    expect(dd1).toHaveStyle({ display: 'none' });
    expect(dd2).not.toHaveStyle({ display: 'none' });
    vi.useRealTimers();
  });

  it('questions are keyboard accessible (Tab + Enter / Space)', async () => {
    const faqs = [{ id: 1, question: 'Q1', answer: 'A1' }];
    const user = userEvent.setup();
    const { container } = render(<FaqAccordion faqs={faqs} />);
    const question = screen.getByRole('button', { name: /Q1/ });
    await user.tab();
    expect(question).toHaveFocus();
    await user.keyboard('{Enter}');
    expect(question).toHaveAttribute('aria-expanded', 'true');
    expect(container.querySelector('.glyphiconRight')).toHaveClass('glyphicon-chevron-down');
    await user.keyboard(' ');
    expect(question).toHaveAttribute('aria-expanded', 'false');
  });
});
