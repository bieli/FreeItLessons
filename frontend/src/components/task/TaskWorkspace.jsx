import { useCallback, useEffect, useRef, useState } from 'react';
import { ajax, HttpError } from '../../lib/api';
import { assertColors, FAILED, PASSED } from '../../lib/asserts';
import { getContext } from '../../lib/context';
import { encodeLatin1Base64, UnsupportedCharacterError } from '../../lib/latin1Base64';
import { formatDuration, useStopwatch } from '../../lib/useStopwatch';
import CodeEditor from './CodeEditor';
import HighlightedCode from './HighlightedCode';

export const MAX_HINT_NO = 5;
const MAIN_BLOCK = "\n# main\nif __name__ == '__main__':\n    __run_tests()\n# main\n                ";
const HINT_LABELS = ['Poproszę o podpowiedź 1', 'Poproszę o podpowiedź 2', 'Poproszę o podpowiedź 3',
  'Poproszę o podpowiedź 4', 'Poddaje się !!!'];

function safeBase64(text) {
  try {
    return encodeLatin1Base64(text);
  } catch {
    return ''; // tests are only informative for the server (it uses the stored ones)
  }
}

/**
 * Online exercise: code editor, run (server side tests), output, assert list,
 * hints and the time spent (sent with every run).
 */
export default function TaskWorkspace({ taskId, code = '', tests = '', asserts = [] }) {
  const { userId } = getContext();
  const editor = useRef(null);
  const seconds = useStopwatch();
  const secondsRef = useRef(0);
  secondsRef.current = seconds;
  const hintIdRef = useRef(0);

  const [output, setOutput] = useState({ text: '', error: false });
  const [colors, setColors] = useState(() => asserts.map(() => FAILED));
  const [unlockedHint, setUnlockedHint] = useState(1);
  const [hint, setHint] = useState(null); // {html} | {text}

  const run = useCallback(async () => {
    let program;
    try {
      program = encodeLatin1Base64(editor.current?.getValue() ?? code);
    } catch (error) {
      if (!(error instanceof UnsupportedCharacterError)) throw error;
      setOutput({
        error: true,
        text: `Program zawiera znak "${error.char}", którego nie można wysłać do sprawdzenia `
          + '(np. polskie litery ą, ę, ł, ś, ź, ż, ć, ń).\nUsuń go (także z komentarzy) i uruchom ponownie !',
      });
      return;
    }
    try {
      const result = await ajax('/zadania/task/code/run/', {
        method: 'POST',
        data: {
          user_id: userId, task_id: taskId, code: program, hint_id: hintIdRef.current,
          tests: safeBase64(tests), timer: formatDuration(secondsRef.current),
        },
      });
      setOutput({ text: result, error: false });
      setColors(assertColors(result, asserts));
    } catch (error) {
      const status = error instanceof HttpError ? `HTTP ${error.status}` : 'HTTP 0';
      const thrown = error instanceof HttpError ? error.statusText : error.message;
      setOutput({ error: true, text: `ERROR IN SERVER RESPONSE -> status: "${status}", text: "error", errorThrown: "${thrown}"` });
    }
  }, [userId, taskId, code, tests, asserts]);

  // the starter code is run when the page opens (shows which tests fail)
  const started = useRef(false);
  useEffect(() => {
    if (started.current) return;
    started.current = true;
    run();
  }, [run]);

  const requestHint = async (hintId) => {
    if (hintId > unlockedHint) return;
    hintIdRef.current = hintId;
    try {
      const result = await ajax('/zadania/task/code/hint/', {
        method: 'POST', data: { user_id: userId, task_id: taskId, hint_id: hintId },
      });
      setHint(result.includes('<p>')
        ? { html: `<strong>Podpowiedź</strong>${result}` }
        : { text: `### Podpowiedź\n### ----\n\n${result}` });
      setUnlockedHint((current) => Math.max(current, Math.min(hintId + 1, MAX_HINT_NO)));
    } catch (error) {
      console.error('hint request failed', error);
    }
  };

  return (
    <>
      <div className="row">
        <div className="col-md-12">
          <button id="program_run" type="button" className="btn btn-success btn-lg btn-block active" onClick={run}>
            Uruchom program == testuj rozwiązanie
          </button>
        </div>
      </div>
      <div className="row">
        <div id="source_task_code" className={hint ? 'col-md-6' : 'col-md-12'}>
          <CodeEditor id="source_code_block" initialValue={code} editorRef={editor} />
        </div>
        <div id="source_task_hint" className={hint ? 'col-md-6' : undefined}>
          {hint?.html !== undefined
            ? <pre id="source_task_hint_content" dangerouslySetInnerHTML={{ __html: hint.html }} />
            : <pre id="source_task_hint_content" hidden={!hint}>{hint?.text}</pre>}
        </div>
      </div>
      <hr />
      <div className="row">
        <div className="col-md-6">
          <h4 className="text-info">Wynik działania programu po uruchomieniu:</h4>
          <pre
            id="program_output"
            aria-live="polite"
            style={{ background: output.error ? 'darkred' : 'black', color: 'white' }}
          >
            {output.text}
          </pre>
        </div>
        <div className="col-md-6">
          <h4 className="text-info" id="unit_tests_results_text">Wynik wykonania testów:</h4>
          <div id="asserts_list">
            {asserts.length ? asserts.map((assertion, index) => (
              <blockquote
                key={index}
                style={{ background: colors[index], color: 'white' }}
                data-assert-status={colors[index] === PASSED}
              >
                {assertion}
              </blockquote>
            )) : <div className="text-warning" style={{ padding: 20 }}>Brak assercji.</div>}
          </div>
        </div>
      </div>
      <hr />
      <div className="row">
        <div className="col-md-6">
          <h4 className="text-info">Funkcja testowa programu:</h4>
          <div id="source_tests_block"><HighlightedCode code={tests} /></div>
        </div>
        <div className="col-md-6">
          <h4 className="text-info">Blok startowy programu:</h4>
          <div id="source_main_block"><pre><code>{MAIN_BLOCK}</code></pre></div>
        </div>
      </div>
      <hr />
      <div className="row" id="hints">
        <div className="col-md-1">&nbsp;</div>
        {HINT_LABELS.map((label, index) => {
          const hintId = index + 1;
          const disabled = hintId > unlockedHint;
          return (
            <div className="col-md-2" key={hintId}>
              <button
                type="button"
                id={`hint-${hintId}`}
                className={`btn ${hintId === MAX_HINT_NO ? 'btn-danger' : 'btn-warning'} btn-lg btn-block${disabled ? ' disabled' : ''}`}
                aria-disabled={disabled}
                onClick={() => requestHint(hintId)}
              >
                {label}
              </button>
            </div>
          );
        })}
        <div className="col-md-1">&nbsp;</div>
      </div>
      <div className="row">
        <div id="timerHtml" style={{ float: 'right', color: 'white' }}>{formatDuration(seconds)}</div>
      </div>
    </>
  );
}
