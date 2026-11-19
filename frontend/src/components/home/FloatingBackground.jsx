import { useMemo, useState } from 'react';
import { createPortal } from 'react-dom';

// Port of floating.js 2.7.4 (decorative elements floating up the page).
const STEPS = 201;
const KEYFRAMES = Array.from({ length: STEPS + 1 }, (_, i) => {
  const percent = (100 * i) / STEPS;
  return `${percent}% { transform: translate(${10 * Math.sin(i / 10)}vw, ${110 + i * (-120 / STEPS)}vh) }`;
}).join('\n');

export const FLOATING_CSS = `
.float-container { width: 100vw; height: 100vh; overflow: hidden; position: absolute;
  top: 0; left: 0; pointer-events: none; }
.float-container div * { width: 1em; height: 1em }
@keyframes float { ${KEYFRAMES} }`;

const SATELLITE_1 = 'https://cdn2.iconfinder.com/data/icons/color-svg-vector-icons-2/512/satellite_gps_connection_sputnik-512.png';
const SATELLITE_2 = 'https://www.svgrepo.com/show/6980/satellite.svg';
const digit = (value) => <b style={{ fontFamily: 'Courier New' }}>{value}</b>;

// the home page shows either floating binary digits or satellites (50 % / 50 %)
export function chooseScene(random = Math.random) {
  if (random() >= 0.5) {
    return [
      { content: digit('0'), number: 12, duration: 15 },
      { content: digit('1'), number: 20, duration: 20, size: [0.1, 2] },
    ];
  }
  return [
    { content: <img alt="" src={SATELLITE_1} />, number: 2, direction: 'reverse', duration: 20, repeat: 1, size: [0.5, 4] },
    { content: <img alt="" src={SATELLITE_2} />, number: 2, direction: 'reverse', duration: 20, size: [0.1, 3] },
  ];
}

function FloatingGroup({ content, number = 1, duration = 10, repeat = 'infinite', direction = 'normal', size = 2, random }) {
  const items = useMemo(() => {
    const scale = Array.isArray(size) ? Math.floor(random() * (size[1] - size[0] + 1)) + size[0] : size;
    return Array.from({ length: number }, (_, i) => ({
      id: i,
      style: {
        position: 'absolute',
        left: 0,
        fontSize: `${scale}em`,
        transform: 'translateY(110vh)',
        animation: `float ${duration}s linear ${i * random()}s ${repeat} ${direction}`,
        marginLeft: `${100 * random()}vw`,
      },
    }));
  }, [number, duration, repeat, direction, size, random]);
  const [finished, setFinished] = useState(() => new Set());

  return (
    <div className="float-container">
      {items.filter((item) => !finished.has(item.id)).map((item) => (
        <div
          key={item.id}
          style={item.style}
          onAnimationEnd={(event) => {
            if (event.animationName === 'float') setFinished((done) => new Set(done).add(item.id));
          }}
        >
          {content}
        </div>
      ))}
    </div>
  );
}

export default function FloatingBackground({ random = Math.random }) {
  const scene = useMemo(() => chooseScene(random), [random]);
  return createPortal(
    <>
      <style id="floating-style">{FLOATING_CSS}</style>
      {scene.map((group, index) => <FloatingGroup key={index} random={random} {...group} />)}
    </>,
    document.body,
  );
}
