import { useEffect, useId, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { staticUrl } from '../../lib/context';

export const STATUSES = [
  ['new', 'nie przeczytałem'],
  ['doit', 'w trakcie nauki'],
  ['help', 'potrzebuję czasu, trudno zrozumieć - pomocy !'],
  ['good', 'ten wątek jest prowadzony ze zrozumieniem - nadążam'],
  ['done', 'zrozumiałem, hurraaa :-)'],
];

/** Modal used to rate a course content (formerly a jQuery UI dialog). */
export default function OpinionDialog({ onSubmit, onClose }) {
  const [selected, setSelected] = useState(null);
  const titleId = useId();
  const dialogRef = useRef(null);

  useEffect(() => {
    document.body.classList.add('modal-open');
    dialogRef.current?.focus();
    return () => document.body.classList.remove('modal-open');
  }, []);

  const submit = () => {
    if (!selected) {
      window.alert('Proszę wskazać jedną opcję !');
      return;
    }
    onSubmit(selected);
  };

  return createPortal(
    <>
      <div className="modal-backdrop in" />
      <div
        ref={dialogRef}
        className="modal opinion-dialog"
        style={{ display: 'block' }}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        onKeyDown={(event) => event.key === 'Escape' && onClose()}
      >
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-header">
              <button type="button" className="close" aria-label="Zamknij" onClick={onClose}>&times;</button>
              <h4 className="modal-title" id={titleId}>Ocena wskazanego konspektu</h4>
            </div>
            <div className="modal-body">
              <p>Oto ikony jakimi może zostać oznaczony konspekt - zgodnie z Twoim wyborem:</p>
              <ul className="list-unstyled">
                {STATUSES.map(([value, label]) => (
                  <li key={value}>
                    <label>
                      <input
                        type="radio"
                        name="dialog-send-status-select"
                        value={value}
                        checked={selected === value}
                        onChange={() => setSelected(value)}
                      />{' '}
                      <img alt="" src={staticUrl(`mainapp/img/${value}.png`)} className="img-circle" width="40" height="40" />
                      {' '}- {label}
                    </label>
                  </li>
                ))}
              </ul>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-primary" onClick={submit}>Prześlij opinię</button>
              <button type="button" className="btn btn-default" onClick={onClose}>Cancel</button>
            </div>
          </div>
        </div>
      </div>
    </>,
    document.body,
  );
}
