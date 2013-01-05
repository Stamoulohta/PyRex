# vim: fileencoding=utf-8:expandtab:tabstop=2:softtabstop=2:shiftwidth=2:
#======================================================================================================================#
#
# Copyright © 2012 George A Stamoulis (g.a.stamoulis@gmail.com)
#
# TODO LICENCE GOES HERE...
#
#======================================================================================================================#
"""
Wrapper for the re python library. 

author  : George Stamoulis
email   : g.a.stamoulis@gmail.com
website : http://www.stamoulohta.com
edited  : 10/12/2012

"""
import re
from rEx import RELib

class StdRe(RELib):
    flags = {"ignore case" : [False, re.IGNORECASE], "multi-line" : [False, re.MULTILINE], "dot all" : [False, re.DOTALL],
             "locale" : [False, re.LOCALE], "unicode" : [False, re.UNICODE], "debug" : [False, re.DEBUG] }
    def __init__(self):
        super(StdRe, self).__init__()
        print("StdRe")

    def getFlags(self):
        return [k for k in self.flags.keys()]

    def setFlag(self, flag, state):
        self.flags[flag][0] = state

    def insertFlags(self): # TODO Do this only when needed.
        flagcode = 0
        for flag in self.flags.values():
            if flag[0]:
                flagcode |= flag[1]
        return flagcode

    def check(self, pattern):
        self.model.clear()
        if not pattern: return False
        try:
            re.compile(pattern, self.insertFlags())
            re.purge()
            return True
        except re.error as rerr:
            self.model.showError(str(rerr))
            return False

    def getMatches(self, regex, text):
        self.model.clear()
        mtchs = []
        # TODO Dump the generator thing..
        for match in re.finditer(regex, text, self.insertFlags()):
            mtchs.append(self.PyRexMatch(match))
        self.model.setMatches(mtchs)
        return mtchs

    class PyRexMatch(RELib.REMatch):
        def __init__(self, match):
            super(StdRe.PyRexMatch, self).__init__(match)
            if self.match.lastindex:
                self.lastindex = self.match.lastindex
            else:
                self.lastindex = 0

        def group(self, index):
            return self.match.group(index)

        def getIndexes(self):
            return self.match.span()

        def span(self, group = 0):
            return self.match.span(group)
