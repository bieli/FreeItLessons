"""Allowlist cleaning of the HTML typed by authors in the admin.

Course contents, FAQ answers and task hints are HTML on purpose (paragraphs,
lists, links, images, tables). Every staff account can log in to the admin, so
the markup is cleaned before it reaches a browser: scripts, event handlers,
``javascript:`` links, forms, frames and unknown tags are removed, the text and
the formatting stay. The stored value is not changed.

The allowlist covers everything used by the bundled course material.
"""
from urllib.parse import urlsplit

import nh3

ALLOWED_TAGS = {
    'a', 'abbr', 'b', 'blockquote', 'br', 'caption', 'cite', 'code', 'col', 'colgroup', 'dd', 'del',
    'div', 'dl', 'dt', 'em', 'figcaption', 'figure', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i',
    'img', 'ins', 'kbd', 'li', 'ol', 'p', 'pre', 'q', 's', 'samp', 'small', 'span', 'strong', 'sub',
    'sup', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'u', 'ul',
}
CELL_ATTRIBUTES = {'align', 'colspan', 'rowspan', 'valign', 'width'}
ALLOWED_ATTRIBUTES = {
    '*': {'class', 'style', 'title'},
    'a': {'href', 'name', 'target'},
    'img': {'alt', 'height', 'src', 'width'},
    'table': {'border', 'cellpadding', 'cellspacing', 'width'},
    'td': CELL_ATTRIBUTES,
    'th': CELL_ATTRIBUTES,
    'col': {'span', 'width'},
    'colgroup': {'span', 'width'},
}
ALLOWED_STYLE_PROPERTIES = {
    'background-color', 'color', 'font-style', 'font-weight', 'height', 'text-align',
    'text-decoration', 'vertical-align', 'white-space', 'width',
}
ALLOWED_URL_SCHEMES = {'http', 'https', 'mailto'}


def clean_html(value):
    """Return the author's HTML without anything that could run code."""
    if value is None:
        return None
    return nh3.clean(
        str(value),
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_URL_SCHEMES,
        filter_style_properties=ALLOWED_STYLE_PROPERTIES,
        link_rel='noopener noreferrer',
    )


def safe_url(value):
    """``value`` if it is a web, e-mail or relative link, otherwise ``'#'``
    (no ``javascript:`` or ``data:`` URLs in href/src attributes)."""
    value = str(value or '').strip()
    try:
        scheme = urlsplit(value).scheme.lower()
    except ValueError:
        return '#'
    if scheme and scheme not in ALLOWED_URL_SCHEMES:
        return '#'
    return value
