"""Diff two recordings produced by run_scenarios.py.

Usage:  python compare.py <legacy.json> <candidate.json> [expected_differences.json]

Every difference is printed.  Differences listed in expected_differences.json
(step id or ``db:<table>`` -> reason) are intentional changes (e.g. security
fixes) and do not fail the run; any other difference makes the exit code 1.

``_line_replacements`` in that file describes intentional markup changes that
show up on many pages (e.g. the logout control in the shared header): each
``from`` line sequence is rewritten to ``to`` in the LEGACY recording before
comparing, so only that exact, reviewed change is tolerated.
"""
import difflib
import json
import sys


def pretty(value):
    return json.dumps(value, indent=1, ensure_ascii=False, sort_keys=True).splitlines()


def apply_replacements(steps, replacements):
    applied = [0] * len(replacements)
    for step in steps:
        body = step.get('body')
        if not body:
            continue
        for idx, rule in enumerate(replacements):
            old, new = rule['from'], rule['to']
            i = 0
            while i <= len(body) - len(old):
                if body[i:i + len(old)] == old:
                    body[i:i + len(old)] = new
                    applied[idx] += 1
                    i += len(new)
                else:
                    i += 1
    return applied


def main():
    legacy_path, candidate_path = sys.argv[1:3]
    expected, replacements = {}, []
    if len(sys.argv) > 3:
        with open(sys.argv[3], encoding='utf-8') as fd:
            config = json.load(fd)
        replacements = config.get('_line_replacements', [])
        expected = {k: v for k, v in config.items() if not k.startswith('_')}
    with open(legacy_path, encoding='utf-8') as fd:
        legacy = json.load(fd)
    with open(candidate_path, encoding='utf-8') as fd:
        candidate = json.load(fd)

    compared, unexpected, intentional = 0, [], []
    seen_expected = set()

    def report(key, old, new):
        diff = list(difflib.unified_diff(pretty(old), pretty(new), 'legacy', 'candidate', lineterm='', n=2))
        if key in expected:
            seen_expected.add(key)
            intentional.append(key)
            print('\n=== EXPECTED difference: %s\n    reason: %s' % (key, expected[key]))
        else:
            unexpected.append(key)
            print('\n=== UNEXPECTED difference: %s' % key)
        print('\n'.join(diff[:120]))
        if len(diff) > 120:
            print('... (%d more diff lines)' % (len(diff) - 120))

    applied = apply_replacements(legacy['steps'], replacements)
    old_steps = {s['id']: s for s in legacy['steps']}
    new_steps = {s['id']: s for s in candidate['steps']}
    for step_id in sorted(set(old_steps) | set(new_steps)):
        compared += 1
        old, new = old_steps.get(step_id), new_steps.get(step_id)
        if old != new:
            report(step_id, old, new)

    for table in sorted(set(legacy['db_state']) | set(candidate['db_state'])):
        compared += 1
        old, new = legacy['db_state'].get(table), candidate['db_state'].get(table)
        if old != new:
            report('db:' + table, old, new)

    for rule, count in zip(replacements, applied):
        print('line replacement applied %3dx: %s' % (count, rule['reason']))
    stale = sorted(set(expected) - seen_expected)
    print('\n' + '=' * 72)
    print('compared items      : %d' % compared)
    print('identical           : %d' % (compared - len(unexpected) - len(intentional)))
    print('expected differences: %d' % len(intentional))
    print('UNEXPECTED          : %d' % len(unexpected))
    for key in unexpected:
        print('   - ' + key)
    if stale:
        print('note: expected differences that did not occur (stale entries):')
        for key in stale:
            print('   - ' + key)
    sys.exit(1 if unexpected else 0)


if __name__ == '__main__':
    main()
