"""Template filters for author supplied content (see mainapp/sanitize.py).

The results are plain strings, so Django still escapes them when they are put
into an HTML attribute (``data-html="{{ content.value|clean_html }}"``).
"""
from django import template

from mainapp import sanitize

register = template.Library()


@register.filter
def clean_html(value):
    return sanitize.clean_html(value)


@register.filter
def safe_url(value):
    return sanitize.safe_url(value)
