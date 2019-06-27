import unittest

from ddt import ddt, data
from mainapp.utils import TaskCodeRun

@ddt
class TaskCodeRunTest(unittest.TestCase):

    @data('input', 'bytes(', 'raw_input', 'import ', 'execfile', 'super', 'file', 'compile',
           ' loader', 'open(', 'write(', '/proc/', '__import__', 'callable', 'globals', 'memoryview',
           'process', 'subprocess', 'os.', 'sys.', 'staticmethod', 'classmethod', 'help')
    def test_is_code_block_secure(self, cmd_input):      
        result = TaskCodeRun.is_code_block_secure(cmd_input)

        self.assertFalse(result)

    @data('abs', 'divmod', 'sorted', 'all', 'enumerate', 'int', 'ord',
          'str', 'any', 'eval', 'isinstance', 'pow', 'sum', 'basestring', 'issubclass', 'print',
          'bin', 'iter', 'property', 'tuple', 'bool', 'filter', 'len', 'range', 'type', 'bytearray',
          'float', 'list', 'unichr', 'format', 'locals', 'reduce', 'unicode', 'chr', 'frozenset',
          'long', 'reload', 'vars', 'getattr', 'map', 'repr', 'xrange', 'cmp', 'max', 'reversed',
          'zip', 'hasattr', 'round', 'complex', 'hash', 'min', 'set', 'delattr', 'next',
          'setattr', 'dict', 'hex', 'object', 'slice', 'dir', 'id', 'oct', 'sorted')
    def test_is_code_block_secure_for_builtin_python_functions(self, cmd_input):      
        result = TaskCodeRun.is_code_block_secure(cmd_input + '(')

        self.assertTrue(result)

    @unittest.skip
    def test_should_not_pass_with_code_block_with_import(self):
        code_block = """# unit
def reverse_chars(chars):
    reversed = ''
    import os
    # TUTAJ DODAJ SWÓJ KOD    

    return reversed
# unit
"""
#b"# unit\ndef reverse_chars(chars):\n    reversed = ''\n    import os\n    # TUTAJ DODAJ SWOJ KOD    \n\n    return reversed\n# unit"

        result = TaskCodeRun.is_code_block_secure(code_block)

        self.assertFalse(result)

