import { useEffect, useMemo, useRef, useState } from 'react';
import { basicSetup } from 'codemirror';
import { EditorView, keymap } from '@codemirror/view';
import { Compartment, EditorState } from '@codemirror/state';
import { indentWithTab, redo, undo } from '@codemirror/commands';
import { gotoLine, openSearchPanel } from '@codemirror/search';
import { indentUnit } from '@codemirror/language';
import { python } from '@codemirror/lang-python';

/**
 * Python code editor (CodeMirror 6) - replacement of edit_area: syntax
 * highlighting, tab = 4 spaces, word wrap, search, go to line, undo/redo,
 * fullscreen. ``editorRef.current.getValue()`` returns the current code.
 */
export default function CodeEditor({ id, initialValue = '', editorRef }) {
  const host = useRef(null);
  const view = useRef(null);
  const wrapping = useMemo(() => new Compartment(), []);
  const [wrap, setWrap] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);

  useEffect(() => {
    const editor = new EditorView({
      parent: host.current,
      state: EditorState.create({
        doc: initialValue,
        extensions: [
          basicSetup,
          python(),
          indentUnit.of('    '),
          EditorState.tabSize.of(4),
          keymap.of([indentWithTab]),
          wrapping.of(EditorView.lineWrapping),
          EditorView.contentAttributes.of({ 'aria-label': 'Kod programu' }),
        ],
      }),
    });
    view.current = editor;
    if (editorRef) editorRef.current = { getValue: () => editor.state.doc.toString() };
    return () => editor.destroy();
  }, [initialValue, wrapping, editorRef]);

  useEffect(() => {
    view.current?.dispatch({ effects: wrapping.reconfigure(wrap ? EditorView.lineWrapping : []) });
  }, [wrap, wrapping]);

  const command = (fn) => () => {
    fn(view.current);
    view.current.focus();
  };

  return (
    <div id={id} className={`code-editor${fullscreen ? ' code-editor--fullscreen' : ''}`}>
      <div className="code-editor__toolbar btn-group btn-group-xs" role="toolbar" aria-label="Edytor">
        <button type="button" className="btn btn-default" onClick={command(openSearchPanel)} title="Szukaj (Ctrl+F)">Szukaj</button>
        <button type="button" className="btn btn-default" onClick={command(gotoLine)} title="Idź do linii (Ctrl+Alt+G)">Idź do linii</button>
        <button type="button" className="btn btn-default" onClick={command(undo)} title="Cofnij (Ctrl+Z)">Cofnij</button>
        <button type="button" className="btn btn-default" onClick={command(redo)} title="Ponów (Ctrl+Y)">Ponów</button>
        <button type="button" className={`btn btn-default${wrap ? ' active' : ''}`} aria-pressed={wrap} onClick={() => setWrap((on) => !on)}>Zawijanie wierszy</button>
        <button type="button" className={`btn btn-default${fullscreen ? ' active' : ''}`} aria-pressed={fullscreen} onClick={() => setFullscreen((on) => !on)}>Pełny ekran</button>
      </div>
      <div ref={host} className="code-editor__host" />
    </div>
  );
}
