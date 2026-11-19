import { render } from '@testing-library/react';
import { expect, it } from 'vitest';
import FloatingBackground, { chooseScene } from '../src/components/home/FloatingBackground';
import RotatingStatusIcons from '../src/components/home/RotatingStatusIcons';
import { setContext } from './utils';

it('floating background renders the digits scene into body', () => {
  render(<FloatingBackground random={() => 0.7} />);
  const containers = document.body.querySelectorAll('.float-container');
  expect(containers).toHaveLength(2);
  expect(containers[0].children).toHaveLength(12);
  expect(containers[1].children).toHaveLength(20);
  const { animation } = containers[0].firstChild.style;
  expect(animation).toContain('float');
  expect(animation).toContain('15s');
  expect(document.getElementById('floating-style').textContent).toContain('@keyframes float');
});

it('the satellites scene is chosen for random < 0.5', () => {
  const scene = chooseScene(() => 0.2);
  expect(scene.map((group) => group.number)).toEqual([2, 2]);
  expect(scene[0].repeat).toBe(1);
});

it('status icons', () => {
  setContext({});
  const { container } = render(<RotatingStatusIcons />);
  const images = container.querySelectorAll('img');
  expect([...images].map((img) => img.id)).toEqual(['img1', 'img2', 'img3', 'img4', 'img5']);
  expect(images[2]).toHaveAttribute('src', '/static/mainapp/img/help.png');
  expect(images[0].style.transition).toBe('transform 5000ms ease-in-out');
});
