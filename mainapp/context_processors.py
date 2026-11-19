from django.conf import settings
from django.middleware.csrf import get_token


def frontend(request):
    """Data every React island may need: {{ frontend_context|json_script:"frontend-context" }}."""
    user = getattr(request, 'user', None)
    is_authenticated = bool(user and user.is_authenticated)
    return {
        'frontend_context': {
            'isAuthenticated': is_authenticated,
            'userId': user.id if is_authenticated else None,
            'username': user.get_username() if is_authenticated else '',
            'csrfToken': get_token(request),
            'staticUrl': settings.STATIC_URL,
        }
    }
