import { useLayoutEffect, useRef } from 'react';

/**
 * Height animated show/hide (replacement of jQuery slideDown/slideUp, 400 ms).
 * When closed the element is display:none, exactly like after jQuery's slideUp.
 */
export default function Collapse({ open, duration = 400, as: Tag = 'div', children, ...rest }) {
  const ref = useRef(null);
  const previous = useRef(open);

  useLayoutEffect(() => {
    const el = ref.current;
    if (previous.current === open) {
      el.style.display = open ? '' : 'none';
      return undefined;
    }
    previous.current = open;
    el.style.overflow = 'hidden';
    el.style.transition = `height ${duration}ms ease`;
    if (open) {
      el.style.display = '';
      const target = el.scrollHeight;
      el.style.height = '0px';
      void el.offsetHeight; // reflow: start the transition from 0
      el.style.height = `${target}px`;
    } else {
      el.style.height = `${el.scrollHeight}px`;
      void el.offsetHeight;
      el.style.height = '0px';
    }
    const timer = setTimeout(() => {
      el.style.transition = '';
      el.style.height = '';
      el.style.overflow = '';
      if (!open) el.style.display = 'none';
    }, duration);
    return () => clearTimeout(timer);
  }, [open, duration]);

  return <Tag ref={ref} {...rest}>{children}</Tag>;
}
