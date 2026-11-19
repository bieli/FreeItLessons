import { useEffect, useRef, useState } from 'react';

export function formatDuration(totalSeconds) {
  const pad = (value) => String(value).padStart(2, '0');
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  return `${pad(hours)}:${pad(minutes)}:${pad(totalSeconds % 60)}`;
}

/** Seconds since mount, updated every second (replacement of easytimer.js). */
export function useStopwatch(now = Date.now) {
  const started = useRef(now());
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setSeconds(Math.floor((now() - started.current) / 1000)), 250);
    return () => clearInterval(id);
  }, [now]);
  return seconds;
}
