from PySide import QtCore, QtGui

class RELib(object):
    def __init__(self):
        print("loading lib: "),
        self.model = ResultsModel()

    def check(self, pattern):
        raise NotImplementedError

    def getMatches(self, regex, text):
        raise NotImplementedError

    def getFlags(self):
        raise NotImplementedError

    def setFlag(self, flag, state):
        raise NotImplementedError

class ResRow(object):
    def __init__(self, data, color = 0xff0000, span=None):
        self.index = data[0]
        self.group = data[1]
        self.color = color
        self.span = span

    def getGroup(self):
        return self.group

    def getIndex(self):
        return self.index

    def getColor(self):
        return self.color

class ResultsModel(QtCore.QAbstractTableModel):
    LBL = "GROUP"
    rows = []
    cols = 1

    def clear(self):
        self.beginResetModel()
        self.LBL = "GROUP"
        self.rows=[]
        self.endResetModel()

    def showError(self, err):
        self.beginResetModel()
        self.LBL = "ERROR"
        self.rows= [ResRow([None, err])]
        self.endResetModel()

    def __init__(self, parent = None):
        super(ResultsModel, self).__init__(parent)

    def columnCount(self, index):
        if index.isValid():
            return 0
        return self.cols

    def rowCount(self, index):
        if index.isValid():
            return 0
        return len(self.rows)

    def data(self, index, role):
        if not index.isValid():
            return None
        if not 0 <= index.row() < len(self.rows):
            return None
        if role == QtCore.Qt.DisplayRole:
            return self.rows[index.row()].getGroup()
        if role == QtCore.Qt.BackgroundColorRole:
            color = self.rows[index.row()].getColor()
            return QtGui.QColor(color)

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.LBL
            else:
                return self.rows[section].getIndex()
        if role == QtCore.Qt.DisplayPropertyRole:
            print("ok")
        return None

    def setMatches(self, matches):
        # TODO set the color!
        for match in matches:
            i = 0;
            for i in range(match.lastindex + 1):
                self.rows.append(ResRow([i, match.group(i)]))

