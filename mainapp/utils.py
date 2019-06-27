# import codecs, difflib, Levenshtein, distance
#
#
# def get_distance(doc1):
#     sr = doc1.lower().split("\t")
#
#     diffl = difflib.SequenceMatcher(None, sr[3], sr[4]).ratio()
#     lev = Levenshtein.ratio(sr[3], sr[4])
#     sor = 1 - distance.sorensen(sr[3], sr[4])
#     jac = 1 - distance.jaccard(sr[3], sr[4])
#
#     print(diffl, lev, sor, jac)

import difflib


def similar(seq1, seq2, ratio=0.9):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > ratio


class TaskCodeRun:
    @staticmethod
    def is_code_block_secure(code_block):
      phrase = set(['input', 'bytes(', 'raw_input', 'import ', '__import__', 'super', 'file', 'compile',
                    ' loader', 'open(', 'write(', '/proc/', 'execfile', 'callable', 'globals', 'memoryview',
                    'process', 'subprocess', 'os.', 'sys.', 'staticmethod', 'classmethod', 'help'])

      # TODO: check below conversion method
      #if isinstance(code_block, (bytes, bytearray)):
      #    code_block = bytes(code_block).decode('utf-8')

      return not (str(code_block) in phrase)
