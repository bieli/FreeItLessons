"""Hooks for django-axes (login throttling, see the AXES_* settings).

A login is blocked after AXES_FAILURE_LIMIT wrong passwords for the same
username from the same IP address, until AXES_COOLOFF_TIME has passed. Locking
the (username, IP) pair - not the IP alone - matters at school: a whole class
usually reaches the server through one public IP address, and a student who
mistypes their password must not lock out the others. Locking the username
alone would let anyone lock out any student by typing their name.
"""
from django.conf import settings
from django.shortcuts import render


def client_ip(request):
    """Address of the visitor. Behind the TLS reverse proxy (DJANGO_BEHIND_TLS_PROXY)
    it is the address the proxy saw: the last X-Forwarded-For entry (the earlier
    entries are sent by the client and can be forged)."""
    if settings.BEHIND_TLS_PROXY:
        forwarded = [part.strip() for part in request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')]
        forwarded = [part for part in forwarded if part]
        if forwarded:
            return forwarded[-1]
    return request.META.get('REMOTE_ADDR')


def lockout_response(request, original_response=None, credentials=None):
    minutes = max(1, int(settings.AXES_COOLOFF_TIME.total_seconds() // 60))
    return render(request, 'mainapp/lockout.html', {
        'failure_limit': settings.AXES_FAILURE_LIMIT,
        'cooloff_minutes': minutes,
    }, status=429)
