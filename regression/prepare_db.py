# Executed inside BOTH the legacy and the candidate app (``manage.py shell -c``)
# so the scripted journeys can log in.  Must stay Django 1.11 compatible.
import os
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

password = os.environ.get('REGRESSION_PASSWORD', 'Regression-Pass-2024!')
for user_id in (1, 2):
    user = User.objects.get(id=user_id)
    user.set_password(password)
    user.save()
Session.objects.all().delete()
print('regression users prepared')
