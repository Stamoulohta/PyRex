
class RELib(object):
    def __init__(self):
        print("loading lib:"),

    def setModel(self, model):
        self.model = model

    def check(self, pattern):
        raise NotImplementedError

    def getMatches(self, regex, text):
        raise NotImplementedError

    def getFlags(self):
        raise NotImplementedError

    def setFlag(self, flag, state):
        raise NotImplementedError

    class REMatch(object):
        def __init__(self, match):
            self.match = match

        def group(self, index):
            raise NotImplementedError

        def getIndexes(self):
            raise NotImplementedError

        def span(self, group = 0):
            raise NotImplementedError
     
