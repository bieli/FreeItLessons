import os
import tempfile

from FreeItLessons import settings


class CodeBlock:
    UNIT_SEPARATOR = '# unit'
    TESTS_SEPARATOR = '# tests'
    MAIN_SEPARATOR = '# main'
    EXPECTES_RUN_TESTS_RESULT = 'ASSERTS TESTS - OK.'

    code_sections = {
        UNIT_SEPARATOR: '',
        TESTS_SEPARATOR: '',
        MAIN_SEPARATOR: ''
    }

    def __init__(self, unit_code_block, tests_block, main_block=None):
        self.unit_code_block = unit_code_block
        self.tests_block = tests_block
        self.main_block = main_block
        self.code = self.unit_code_block + "\n\n" + self.tests_block + "\n\n" + self.main_block

    def create_code_blocks_from_full_source(self, src):
        for section in self.code_sections:
            code_pos_start, code_pos_end = tuple(self.findall(section, src))
            # print(code_pos_start, code_pos_end)
            self.code_sections[section] = src[code_pos_start:code_pos_end].replace(section, '')
            print(self.code_sections[section])
        return self.code_sections[self.UNIT_SEPARATOR], self.code_sections[self.TESTS_SEPARATOR], self.code_sections[
            self.MAIN_SEPARATOR]

    def findall(self, string):
        """
        >>> text = "Allowed Hello Hollow"
        >>> tuple(findall('ll', text))
        (1, 10, 16)
        """
        index = 0 - len(sub)
        try:
            while True:
                index = string.index(sub, index + len(sub))
                yield index
        except ValueError:
            pass

    def get_sections(self, hide_solutions=True):
        cb, tb, mb = self.create_code_blocks_from_full_source(self.code)
        if hide_solutions:
            return self._hide_solutions(cb, tb, mb)
        else:
            return cb, tb, mb

    def _hide_solutions(self, cb, tb, mb):
        return '', '', ''


class CodeBlockRunner:
    def __init__(self, code_block_obj):
        self.code_block_obj = code_block_obj

    def run(self):
        self._remove_all_imports()
        # TODO: run with console
        code_to_running = ''
        code_to_running += [line.strip() for line in self.code_block_lines]
        code_to_running += [line.strip() for line in self.tests_block_lines]

        # TODO: pipe/exec runner
        # try:
        # exec.(code_to_running)
        # except:
        #
        # TODO get results from code running
        result = ''
        # TODO: use this method or exec in system
        # with open("somefile.py") as f:
        #     code = compile(f.read(), "somefile.py", 'exec')
        #     exec(code, global_vars, local_vars)

        try:
            f = tempfile.NamedTemporaryFile(delete=False)
            f.write(b"print('aaa from TMPFILE')")
            f.close()
        except:
            os.unlink(f.name)
            result = 'ERR: 3'

        try:
            cmd = "%s %s" % (settings.PYTHON_EXEC, f.name)
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            print("Return code: ", p.returncode)
            print(out.rstrip(), err.rstrip())
        except:
            os.unlink(f.name)
            result = 'ERR: 2'

        return result == self.EXPECTES_RUN_TESTS_RESULT

    def _remove_all_imports(self):
        new_lines = []
        for line in self.code_block_lines:
            if 'import' not in line:
                new_lines.append(line)

        new_test_lines = []
        for line in self.tests_block_lines:
            if 'import' not in line:
                new_test_lines.append(line)

        self.code_block_lines = new_lines
        self.tests_block_lines = new_test_lines

    def get_results(self):
        return False


if __name__ == '__main__':
    from subprocess import Popen, PIPE

    cmd = settings.PYTHON_EXEC + " test003.py"
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    print("Return code: ", p.returncode)
    print(out.rstrip(), err.rstrip())

    # with open('./test003.py', 'r') as fd:
    #     code_block_obj = CodeBlock('', '')
    #     unit_code_block, tests_block, main_block = code_block_obj.get_sections(fd.read())
    #
    #     cb = CodeBlockRunner(code_block_obj)
    #     run_result = cb.run()
    #     run_results = cb.get_results()
    #     if run_result:
    #         print("SUCCESS: run_results -> {}".format(run_results))
    #     else:
    #         print("ERROR: run_results -> {}".format(run_results))
    #
