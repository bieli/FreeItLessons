import { useMemo } from 'react';
import { classHighlighter, highlightCode } from '@lezer/highlight';
import { parser } from '@lezer/python';

/** Read-only Python source with syntax highlighting (formerly highlight.js). */
export default function HighlightedCode({ code }) {
  const parts = useMemo(() => {
    const out = [];
    highlightCode(code, parser.parse(code), classHighlighter,
      (text, classes) => out.push([text, classes]),
      () => out.push(['\n', '']));
    return out;
  }, [code]);

  return (
    <pre>
      <code className="language-python">
        {parts.map(([text, classes], index) => (classes
          ? <span key={index} className={classes}>{text}</span>
          : <span key={index}>{text}</span>))}
      </code>
    </pre>
  );
}
