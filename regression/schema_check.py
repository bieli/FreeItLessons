# Executed in the candidate app (``manage.py shell -c``) against a copy of the
# legacy database: verifies that the models fit the real (partly hand altered)
# legacy schema.  Prints findings; exits non-zero on incompatibilities.
import sys

from django.apps import apps
from django.db import connection

problems, notes = [], []
with connection.cursor() as cursor:
    for model in apps.get_app_config('mainapp').get_models():
        tables = [(model._meta.db_table, [f for f in model._meta.concrete_fields])]
        tables += [(f.m2m_db_table(), None) for f in model._meta.many_to_many]
        for table, fields in tables:
            info = connection.introspection.get_table_description(cursor, table)
            columns = {c.name: c for c in info}
            if fields is None:
                continue
            for field in fields:
                col = columns.get(field.column)
                if col is None:
                    problems.append('%s.%s: column missing in database' % (table, field.column))
                elif field.null and not col.null_ok:
                    notes.append('%s.%s: model allows NULL, database column is NOT NULL'
                                 % (table, field.column))
            known = {f.column for f in fields}
            cursor.execute('PRAGMA table_info("%s")' % table)
            for _, name, _, notnull, default, _ in cursor.fetchall():
                if name not in known:
                    msg = '%s.%s: extra legacy column (not in model), default=%r' % (table, name, default)
                    if notnull and default is None:
                        problems.append(msg + ' - NOT NULL without default breaks inserts')
                    else:
                        notes.append(msg)
for line in notes:
    print('schema note   :', line)
for line in problems:
    print('SCHEMA PROBLEM:', line)
print('schema check: %d problem(s), %d note(s)' % (len(problems), len(notes)))
if problems:
    sys.exit(1)
