import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import StatusPieChart, { countStatuses, slicePath } from '../src/components/admin/StatusPieChart';

it('counts statuses of the admin change list', () => {
  document.body.innerHTML = `<table id="result_list"><tbody>
    <tr><td class="field-status">Good</td></tr><tr><td class="field-status">Good</td></tr>
    <tr><td class="field-status">Help</td></tr></tbody></table>`;
  expect(countStatuses()).toEqual({ New: 0, Doit: 0, Help: 1, Good: 2, Done: 0 });
});

it('renders a pie with legend', () => {
  render(<StatusPieChart counts={{ New: 1, Doit: 0, Help: 1, Good: 2, Done: 0 }} />);
  expect(screen.getByText('Content Statuses Activities')).toBeInTheDocument();
  expect(document.querySelectorAll('svg path')).toHaveLength(3);
  expect(screen.getByText('Good: 2 (50%)')).toBeInTheDocument();
});

it('slicePath draws a full circle for a single status', () => {
  expect(slicePath(150, 150, 140, 0, 2 * Math.PI)).toMatch(/^M 150 10 A/);
});
