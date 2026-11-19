import { useEffect, useRef, useState } from 'react';
import { getContext } from '../../lib/context';

const PUBLIC_LINKS = [
  ['/faq.html', 'Pytania i odpowiedzi'],
  ['/mentorzy.html', 'Mentorzy'],
  ['/kursy.html', 'Kursy'],
];
const USER_LINKS = [
  ['/admin/password_change/', 'Zmień hasło'],
  ['/opinions/', 'Moje oceny kursu'],
  ['/achievements/', 'Osiągnięcia'],
];

/** Site header: collapsible (mobile) menu, user dropdown and logout (POST). */
export default function NavBar() {
  const { isAuthenticated, username, csrfToken } = getContext();
  const [menuOpen, setMenuOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const logoutForm = useRef(null);

  useEffect(() => {
    if (!dropdownOpen) return undefined;
    const onClick = (event) => {
      if (!dropdownRef.current?.contains(event.target)) setDropdownOpen(false);
    };
    const onKey = (event) => {
      if (event.key === 'Escape') setDropdownOpen(false);
    };
    document.addEventListener('click', onClick);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('click', onClick);
      document.removeEventListener('keydown', onKey);
    };
  }, [dropdownOpen]);

  const links = isAuthenticated ? [...PUBLIC_LINKS, ['/zadania.html', 'Zadania']] : PUBLIC_LINKS;

  return (
    <div className="container-fluid">
      <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <div className="navbar-header">
          <button
            className="navbar-toggler"
            type="button"
            aria-controls="navbarNavDropdown"
            aria-expanded={menuOpen}
            aria-label="Toggle navigation"
            onClick={() => setMenuOpen((open) => !open)}
          >
            <span className="navbar-toggler-icon" />
          </button>
          <a className="navbar-brand" href="/">Start</a>
        </div>

        <div className={`collapse navbar-collapse${menuOpen ? ' in' : ''}`} id="navbarNavDropdown">
          <ul className="nav navbar-nav">
            {links.map(([href, label]) => (
              <li key={href}><a href={href} className="modula-font active">{label}</a></li>
            ))}
          </ul>
          <ul className="nav navbar-nav pull-right">
            {isAuthenticated ? (
              <>
                <li ref={dropdownRef} className={`dropdown${dropdownOpen ? ' open' : ''}`}>
                  <a
                    href="#"
                    className="dropdown-toggle active"
                    role="button"
                    aria-haspopup="true"
                    aria-expanded={dropdownOpen}
                    onClick={(event) => {
                      event.preventDefault();
                      setDropdownOpen((open) => !open);
                    }}
                  >
                    Zalogowany <b>{username}</b><span className="caret" />
                  </a>
                  <ul className="dropdown-menu">
                    {USER_LINKS.map(([href, label]) => <li key={href}><a href={href}>{label}</a></li>)}
                  </ul>
                </li>
                <li>
                  <form ref={logoutForm} method="post" action="/admin/logout/" style={{ display: 'none' }}>
                    <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
                  </form>
                  <a
                    href="/admin/logout/"
                    onClick={(event) => {
                      event.preventDefault();
                      logoutForm.current.submit();
                    }}
                  >
                    Wyloguj
                  </a>
                </li>
              </>
            ) : (
              <li><a href="/admin/login/?next=/">Zaloguj się</a></li>
            )}
          </ul>
        </div>
      </nav>
    </div>
  );
}
