"""Bootstrap executed in the CHILD interpreter that runs a student's program.

    cd /tmp/solution-xxxx && python -I -S sandbox_bootstrap.py

It installs a Python audit hook (PEP 578, cannot be removed once installed)
that denies the dangerous capabilities a teaching exercise never needs:
spawning processes, network access, native code, databases and any file
access except reading the standard library and the program itself.
The program then runs as ``__main__``; uncaught exceptions are printed without
the bootstrap frame, so students see exactly the usual Python traceback.

This complements (does not replace) the OS level limits applied by
mainapp.sandbox (timeout, CPU, memory, file size, process count, empty env).
"""
import builtins
import linecache  # noqa: F401 - pre-imported for traceback printing
import os
import sys
import traceback

BLOCKED_EVENTS = (
    'os.system', 'os.exec', 'os.posix_spawn', 'os.spawn', 'os.fork', 'os.forkpty', 'os.kill',
    'os.killpg', 'os.remove', 'os.rename', 'os.rmdir', 'os.mkdir', 'os.chmod', 'os.chown',
    'os.chflags', 'os.truncate', 'os.symlink', 'os.link', 'os.putenv', 'os.unsetenv', 'os.chdir',
    'os.utime', 'os.startfile', 'os.setxattr', 'os.removexattr', 'os.add_dll_directory',
    'sys.remote_exec', 'cpython.remote_debugger_script',
)
BLOCKED_MODULES = {
    'subprocess', 'socket', 'ctypes', 'sqlite3', 'shutil', 'pty', 'urllib', 'http', 'ftplib',
    'smtplib', 'imaplib', 'poplib', 'nntplib', 'telnetlib', 'webbrowser', 'resource', 'fcntl',
    'winreg', '_winapi', 'msvcrt', 'mmap', 'signal',
}
BOOTSTRAP_FILE = os.path.realpath(__file__)
PROGRAM_NAME = 'program.py'
EXIT_MESSAGE = ('SystemExit: the program was stopped before the tests ran '
                '(SystemExit and sys.exit() are not allowed in exercises)\n')
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC


def install_restrictions(workdir):
    readable_roots = tuple(sorted({os.path.realpath(p) + os.sep for p in (
        sys.prefix, sys.base_prefix, sys.exec_prefix, sys.base_exec_prefix, workdir)}))

    def deny(what):
        raise PermissionError('Operation not allowed in exercises: %s' % what)

    def audit(event, args):
        if event == 'open':
            path, mode, flags = args
            if (flags or 0) & WRITE_FLAGS or (mode and any(c in mode for c in 'wax+')):
                deny('writing files')
            if isinstance(path, int):
                return
            real = os.path.realpath(os.fsdecode(path))
            if not real.startswith(readable_roots):
                deny('reading %s' % os.fsdecode(path))
        elif event.startswith(BLOCKED_EVENTS) or event.split('.', 1)[0] in BLOCKED_MODULES:
            deny(event)

    sys.addaudithook(audit)


def main():
    # the program is always ./program.py of the private working directory
    # (the parent process creates it and starts this interpreter there)
    program = os.path.realpath(PROGRAM_NAME)
    with open(program, encoding='utf-8') as fd:
        source = fd.read()
    try:
        code = compile(source, program, 'exec')
    except SyntaxError as exc:
        traceback.print_exception(type(exc), exc, None)
        sys.exit(1)

    sys.argv = [program]
    namespace = {'__name__': '__main__', '__file__': program, '__builtins__': builtins,
                 '__doc__': None, '__spec__': None}
    install_restrictions(os.path.dirname(program))
    try:
        exec(code, namespace)
    except SystemExit:
        # raise SystemExit / sys.exit() would stop the program before the tests
        # run - with status 0 that looked like a solved task
        sys.stderr.write(EXIT_MESSAGE)
        sys.exit(1)
    except BaseException as exc:  # print like the interpreter would, minus bootstrap frames
        print_student_traceback(exc)
        sys.exit(1)


def print_student_traceback(exc):
    report = traceback.TracebackException(type(exc), exc, exc.__traceback__)
    pending = [report]
    while pending:
        item = pending.pop()
        item.stack = traceback.StackSummary.from_list(
            [frame for frame in item.stack if os.path.realpath(frame.filename) != BOOTSTRAP_FILE])
        pending.extend(e for e in (item.__cause__, item.__context__) if e is not None)
    sys.stderr.write(''.join(report.format()))


if __name__ == '__main__':
    main()
