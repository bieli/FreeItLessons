import { useEffect, useState } from 'react';
import { ajax } from '../../lib/api';
import { getContext, staticUrl } from '../../lib/context';
import OpinionDialog from './OpinionDialog';

const STATUS_PATTERN = /^(new|doit|help|good|done)$/;

/**
 * Course content (admin authored HTML) the student can rate. The icon in the
 * background shows the student's current opinion, loaded from the server.
 */
export default function ContentBlock({ contentId, html = '' }) {
  const { isAuthenticated, userId } = getContext();
  const [status, setStatus] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return undefined;
    let active = true;
    ajax('/content/user/', { data: { user_id: userId, content_id: contentId } })
      .then((result) => active && STATUS_PATTERN.test(result) && setStatus(result))
      .catch(() => {}); // 400 "content NOT EXISTS" = not rated yet
    return () => { active = false; };
  }, [isAuthenticated, userId, contentId]);

  const onClick = (event) => {
    if (['A', 'IMG'].includes(event.target.tagName)) return; // links/images inside the content
    openRating();
  };

  const openRating = () => {
    if (!isAuthenticated) {
      window.alert('W celu wystawienia oceny kontekstu musisz być zalogowany !');
      return;
    }
    setDialogOpen(true);
  };

  // keyboard: Enter / Space on the focused block itself (not on a link inside it)
  const onKeyDown = (event) => {
    if (event.target !== event.currentTarget || (event.key !== 'Enter' && event.key !== ' ')) return;
    event.preventDefault();
    openRating();
  };

  const submit = (selected) => {
    setDialogOpen(false);
    ajax('/content/user/status/', {
      method: 'POST',
      data: { user_id: userId, content_id: contentId, status: selected },
    })
      .then(() => setStatus(selected))
      .catch((error) => console.error('opinion not saved', error));
  };

  return (
    <>
      <blockquote
        className="bq1"
        id={`content_id__${contentId}`}
        data-id={contentId}
        style={status ? { backgroundImage: `url("${staticUrl(`mainapp/img/${status}.png`)}")` } : undefined}
        tabIndex={0}
        title="Kliknij lub naciśnij Enter, aby ocenić ten fragment"
        onClick={onClick}
        onKeyDown={onKeyDown}
        dangerouslySetInnerHTML={{ __html: html }}
      />
      {dialogOpen && <OpinionDialog onSubmit={submit} onClose={() => setDialogOpen(false)} />}
    </>
  );
}
