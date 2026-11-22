"""Execution of students' programs with OS level limits.

Defence in depth for the online exercises (see also sandbox_bootstrap.py):

* no shell - the interpreter is started with an argument list,
* ``-I -S`` isolated interpreter, empty environment (no secrets leak),
* private temporary directory, removed afterwards,
* wall clock timeout, the whole process group is killed on expiry,
* rlimits: CPU time, address space, written file size (caps the output),
  number of processes (no fork bombs),
* audit hook in the child denying processes, network, native code, file writes.

For hostile environments run the application (or a dedicated runner service)
in an additional OS sandbox (gVisor, nsjail, firejail, separate container).
"""
import os
import signal
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass

from django.conf import settings

try:
    import fcntl
    import resource
except ImportError:  # pragma: no cover - not POSIX
    fcntl = resource = None

BOOTSTRAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sandbox_bootstrap.py')
PROGRAM_NAME = 'program.py'


@dataclass
class RunResult:
    stdout: bytes
    stderr: bytes
    returncode: int
    timed_out: bool
    program_path: str


def _limits():
    timeout = int(settings.CODE_RUN_TIMEOUT_SECONDS)
    memory = int(settings.CODE_RUN_MEMORY_MB) * 1024 * 1024
    output = int(settings.CODE_RUN_OUTPUT_KB) * 1024

    def apply():  # runs in the child between fork() and exec()
        if resource is None:
            return
        resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout + 1))
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        resource.setrlimit(resource.RLIMIT_FSIZE, (output, output))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        if hasattr(resource, 'RLIMIT_NPROC') and os.getuid() != 0:
            resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
    return timeout, output, apply


@contextmanager
def user_run_slot(user_id):
    """Yield True when no other program of ``user_id`` is running (all the
    server processes share the lock file), otherwise False."""
    if fcntl is None:  # pragma: no cover - not POSIX
        yield True
        return
    lock_dir = os.path.join(settings.TEMP_SOLUTION_CODE_BLOCK or tempfile.gettempdir(),
                            'freeitlessons-run-locks')
    os.makedirs(lock_dir, mode=0o700, exist_ok=True)
    with open(os.path.join(lock_dir, 'user-%d.lock' % int(user_id)), 'a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def run_program(source):
    """Run ``source`` (str) in a restricted child interpreter."""
    timeout, output_limit, preexec = _limits()
    base_dir = settings.TEMP_SOLUTION_CODE_BLOCK or None
    with tempfile.TemporaryDirectory(prefix='solution-', dir=base_dir) as workdir:
        program = os.path.join(workdir, PROGRAM_NAME)
        with open(program, 'w', encoding='utf-8') as fd:
            fd.write(source)
        out_path, err_path = os.path.join(workdir, 'stdout'), os.path.join(workdir, 'stderr')
        with open(out_path, 'wb') as out, open(err_path, 'wb') as err:
            proc = subprocess.Popen(
                [settings.PYTHON_EXEC, '-I', '-S', BOOTSTRAP],
                stdin=subprocess.DEVNULL, stdout=out, stderr=err, cwd=workdir,
                env={'PYTHONIOENCODING': 'utf-8', 'LANG': 'C.UTF-8', 'NO_COLOR': '1'},
                preexec_fn=preexec, start_new_session=True, close_fds=True)
            timed_out = False
            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()
        with open(out_path, 'rb') as out, open(err_path, 'rb') as err:
            stdout, stderr = out.read(output_limit), err.read(output_limit)
        return RunResult(stdout, stderr, proc.returncode, timed_out, os.path.realpath(program))
