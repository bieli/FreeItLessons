import { useEffect, useState } from 'react';
import { staticUrl } from '../../lib/context';

// icon, size, final rotation (deg), duration (ms) - as animated on the former home page
export const ICONS = [
  ['new', 120, 30, 5000],
  ['doit', 160, -10, 1500],
  ['help', 200, -20, 2600],
  ['doit', 160, 15, 3500],
  ['done', 120, 45, 1800],
];

export default function RotatingStatusIcons() {
  const [started, setStarted] = useState(false);

  useEffect(() => {
    // two frames: the browser must paint the 0deg state before the transition starts
    let second;
    const first = requestAnimationFrame(() => {
      second = requestAnimationFrame(() => setStarted(true));
    });
    return () => {
      cancelAnimationFrame(first);
      cancelAnimationFrame(second);
    };
  }, []);

  return (
    <span>
      {ICONS.map(([icon, size, angle, duration], index) => (
        <span key={`${icon}${index}`}>
          {index > 0 && <>&nbsp;&nbsp;➜&nbsp;&nbsp;</>}
          <img
            id={`img${index + 1}`}
            alt=""
            src={staticUrl(`mainapp/img/${icon}.png`)}
            className="img-circle"
            width={size}
            height={size}
            style={{
              transform: `rotate(${started ? angle : 0}deg)`,
              transition: `transform ${duration}ms ease-in-out`,
            }}
          />
        </span>
      ))}
    </span>
  );
}
