#!/usr/bin/env python2
# vim: fileencoding=utf-8:
#======================================================================================================================#
#
# Copyright © 2012 George A Stamoulis (g.a.stamoulis@gmail.com)
#
# TODO LICENCE GOES HERE...
#
#======================================================================================================================#
"""
TODO Describe and comment the code...

author  : George Stamoulis
email   : g.a.stamoulis@gmail.com
website : http://www.stamoulohta.com
edited  : 10/12/2012

"""

import sys, webbrowser
from Dialogs import UrlDialog
from PySide import QtGui, QtCore
from os.path import expanduser
from urllib2 import urlopen, URLError
from PyRExPorts import *

re = RELib.__subclasses__()[0]() #TODO make it extendable already!!

COLORS =[QtGui.QColor("Red"), QtGui.QColor("Lime")]

class PyRExPainter(QtGui.QTextCursor): # Not using QSyntaxHighlighter due to the need of multiline text blocks.
    PAINTING = False
    STOP     = False

    def __init__(self, reditor, rematch):
        super(PyRExPainter, self).__init__(rematch.document())
        self.document().contentsChanged.connect(self.enqueue)
        self.queue = self.Enqueuer(self)
        self.reditor = reditor
        self.rematch = rematch
        self.initColorscheme()

    def initColorscheme(self):
        self.default = QtGui.QTextCharFormat()
        self.pallete=[QtGui.QTextCharFormat() for i in range(2)]
        self.pallete[0].setBackground(COLORS[0])
        self.pallete[1].setBackground(COLORS[1])

    def begin(self):
        self.STOP = False
        self.unFormat()
        self.pain_t()

    def enqueue(self):
        while self.queue.isRunning():
            pass
        self.queue = self.Enqueuer(self)
        self.queue.Stopped.connect(self.begin)
        self.queue.start()

    def pain_t(self):
        self.PAINTING = True
        pattern = self.reditor.text()
        if re.check(pattern):
            self.document().blockSignals(True)          # We're missing the signals from PyRExMatchBox
            self.rematch.busyState(True)                # when we pain_t ..and we can't help it. ;)
            i = 0
            txt = self.document().toPlainText()
            matches = re.getMatches(pattern, txt)
            self.rematch.setBBarRange(len(matches))
            for num, match in enumerate(matches):
                QtCore.QCoreApplication.processEvents() # FIXME if application Exits, this doesn't stop.
                self.rematch.setBBarValue(num)
                if not self.STOP:
                    frm, to = match.getIndexes()
                    self.setFormat(frm, to, self.pallete[i])
                    i += 1
                    i = (i % 2)
                elif self.STOP:
                    break
            self.document().blockSignals(False)
            self.rematch.busyState(False)
        self.PAINTING = False
        self.STOP = False

    def setFormat(self, frm, to, form):
        self.setPosition(frm, self.MoveAnchor)
        self.setPosition(to,  self.KeepAnchor)
        self.setCharFormat(form)

    def unFormat(self):
        self.document().blockSignals(True)
        self.select(self.Document)
        self.setCharFormat(self.default)
        self.document().blockSignals(False)

    class Enqueuer(QtCore.QThread):
        Stopped = QtCore.Signal()

        def __init__(self, outer, parent=None):
            super(PyRExPainter.Enqueuer, self).__init__(parent)
            self.outer = outer
            if self.outer.PAINTING:
                self.outer.STOP = True

        def run(self):
            while self.outer.STOP:
                pass
            self.Stopped.emit()

class PyRExEdit(QtGui.QLineEdit):
    PLACEHOLDER = "type your regex"

    def __init__(self, parent):
        super(PyRExEdit, self).__init__(parent)
        self.shapeUp()

    def shapeUp(self):
        self.setPlaceholderText(self.PLACEHOLDER)

    def linkTo(self, rematch):
        self.renoir = PyRExPainter(self, rematch)
        self.textChanged.connect(self.renoir.enqueue)

class PyRExMatchBox(QtGui.QTextEdit):
    def __init__(self, parent = None):
        super(PyRExMatchBox, self).__init__(parent)
        self.initGui()

    def initGui(self):
        self.bbar = self.BusyBar(self)
        overLay_h = QtGui.QHBoxLayout()
        overLay_h.addSpacing(30)
        overLay_h.addWidget(self.bbar)
        overLay_h.addSpacing(30)
        overLay_v = QtGui.QVBoxLayout(self)
        overLay_v.addStretch(1)
        overLay_v.addLayout(overLay_h)
        self.setLayout(overLay_v)
        self.busyState(False)

    def busyState(self, busy=True):
        if busy:
            self.bbar.reset()
            self.bbar.show()
        else:
            self.bbar.hide()
        self.setReadOnly(busy)

    def setBBarValue(self, value):
        self.bbar.setValue(value)

    def setBBarRange(self, maximum):
        self.bbar.setRange(0, maximum)

    class BusyBar(QtGui.QProgressBar):
        def __init__(self, parent=None):
            super(PyRExMatchBox.BusyBar, self).__init__(parent)
            effect = QtGui.QGraphicsOpacityEffect(self)
            effect.setOpacity(0.7)
            self.setGraphicsEffect(effect)
            self.setTextVisible(False)

class PyRExTV(QtGui.QTableView):
    def __init__(self, parent):
        super(PyRExTV, self).__init__(parent)
        self.setup()

    def setup(self):
        self.model = self.ResultsModel(self)
        re.setModel(self.model)
        self.setModel(self.model)
        self.setCornerButtonEnabled(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.clicked.connect(self.onClick)

    def linkTo(self, rematch):
        self.rematch = rematch

    def onClick(self, index):
        span = self.model.getSpan(index.row())
        cur = self.rematch.textCursor()
        if cur and span:
            cur.setPosition(span[0], cur.MoveAnchor)
            cur.setPosition(span[1], cur.KeepAnchor)
            self.rematch.setTextCursor(cur)

    def showError(self, error):
        self.model.showError(error)

    class ResRow(object):
        def __init__(self, data, color = QtGui.QColor("Red"), span=None):
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

        def getSpan(self):
            return self.span

    class ResultsModel(QtCore.QAbstractTableModel):
        HEADER = LABEL = "GROUP"
        ERROR = "ERROR"
        rows = []
        cols = 1

        def __init__(self, parent = None):
            super(PyRExTV.ResultsModel, self).__init__(parent)

        def clear(self):
            self.beginResetModel()
            self.HEADER = self.LABEL
            self.rows=[]
            self.endResetModel()

        def showError(self, err):
            self.beginResetModel()
            self.HEADER = self.ERROR
            self.rows= [PyRExTV.ResRow([None, err])]
            self.endResetModel()

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
                return self.rows[index.row()].getColor()

        def headerData(self, section, orientation, role):
            if role == QtCore.Qt.DisplayRole:
                if orientation == QtCore.Qt.Horizontal:
                    return self.HEADER
                else:
                    return self.rows[section].getIndex()
            return None

        def setMatches(self, matches):
            c = 0
            for match in matches:
                i = 0;
                for i in range(match.lastindex + 1): # TODO named groups.
                    self.rows.append(PyRExTV.ResRow([i, match.group(i)], COLORS[c], match.span(i)))
                c += 1
                c = (c % 2)

        def getSpan(self, index):
            return self.rows[index].getSpan()

class PyRExWid(QtGui.QMainWindow):

    def __init__(self):
        super(PyRExWid, self).__init__(None)
        self.shapeUp()

    def shapeUp(self):
        self.resize(1000, 600)
        self.center()
        self.setWindowTitle('PyREx')
        self.setWindowIcon(QtGui.QIcon('icons/pyrex.png'))
        self.statusBar()
        self.getMenuBar()
        self.getToolbar()
        self.setCentralWidget(self.getContent())
        self.setUp()
        self.setSignals()
        self.show()

    def center(self):
        block = self.frameGeometry()
        bullseye = QtGui.QDesktopWidget().availableGeometry().center()
        block.moveCenter(bullseye)
        self.move(block.topLeft())

    def getMenuBar(self):
        menuBar = self.menuBar()
        menus=[ "&File", "&Edit", "&Help" ] #XXX"&Libraries"XXX, "&Tools", "&View"]
        for menu in menus:
            fileMenu = menuBar.addMenu(menu)
            for action in self.getMenuActions(menu):
                fileMenu.addAction(action)

    def getToolbar(self):
        toolBar = self.addToolBar("Tools")
        for tool in self.getMenuActions("toolBar"):
            toolBar.addAction(tool)

    def getContent(self):
        self.reditor = PyRExEdit(self)
        self.retrieve = QtGui.QPushButton(QtGui.QIcon.fromTheme("edit-copy",\
                                                QtGui.QIcon('icons/edit-copy.png')), None)
        self.rematch = PyRExMatchBox(self) # QtGui.QTextEdit(self)
        self.results = PyRExTV(self)

        top  = QtGui.QHBoxLayout()
        splt = QtGui.QSplitter(QtCore.Qt.Horizontal)
        wrap = QtGui.QVBoxLayout()

        top.addWidget(self.reditor, 1)
        top.addWidget(self.retrieve, 0)

        splt.addWidget(self.rematch)
        splt.addWidget(self.results)
        splt.setSizes([750,250])

        wrap.addLayout(self.getReFlagsLayout(re)) # reflagger) #//TODO MAY be nt a class...
        wrap.addLayout(top, 0)
        wrap.addWidget(splt, 1)

        mainWidget = QtGui.QWidget()
        mainWidget.setLayout(wrap)
        return mainWidget

    def setUp(self):
        self.printDialog = None
        self.clipBoard = QtGui.QApplication.clipboard()
        self.reditor.linkTo(self.rematch)
        self.results.linkTo(self.rematch)

    def setSignals(self):
        self.retrieve.clicked.connect(self.updateClipBoard)

    def getReFlagsLayout(self, libModule):
        flagwrap = QtGui.QHBoxLayout()
        for flag in libModule.getFlags():
            chkF = QtGui.QCheckBox(flag)
            chkF.stateChanged.connect(self.registerFlag)
            flagwrap.addWidget(chkF)
        return flagwrap

    def registerFlag(self):
        cbox = self.sender()
        key = cbox.text()
        val = QtCore.Qt.CheckState.Checked == cbox.checkState()
        re.setFlag(key, val)
        self.reditor.renoir.enqueue()


    def updateClipBoard(self):
        self.clipBoard.setText(self.reditor.text(), QtGui.QClipboard.Clipboard)
        self.clipBoard.setText(self.reditor.text(), QtGui.QClipboard.Selection)

    def newRe(self):
        self.reditor.clear()

    def fileOpen(self):
        fileName, ok = QtGui.QFileDialog.getOpenFileName(self, "Open File", expanduser("~"))
        if ok and fileName:
            with open(fileName, "r") as f:
                self.rematch.setText(f.read())

    def urlOpen(self):
        urlDialog = UrlDialog(self)
        address, ok = urlDialog.getUrl()
        if ok and address:
            try:
                response = urlopen(address)
                self.rematch.setPlainText(response.read())
            except URLError as urlerr:
                if hasattr(urlerr, 'reason'):
                    self.results.showError(str(urlerr.reason))
                else:
                    self.results.showError(str(urlerr.code))

    def visitMe(self):
        url = "http://www.stamoulohta.com"
        webbrowser.open_new_tab(url)

    def dummy(self):
        """Dummy function"""
        print("you are dummy 8*!")

    def getMenuActions(self, menu):
        actionAid = []
        pattern =[ "actionAid.append(QtGui.QAction(QtGui.QIcon.fromTheme(%s, QtGui.QIcon(%s)), %s, self))",
                   "actionAid[%d].setShortcut(%s)",
                   "actionAid[%d].setStatusTip(%s)",
                   "actionAid[%d].triggered.connect(%s)" ]

        menuActions={"&File" : [ (("'document-open'", 'None', "'&Open File'"),("'Ctrl+O'",), ("'Open a File'",), ('self.fileOpen',)),
                                 (("'insert-link'", 'None', "'Open &Url'"),("'Ctrl+U'",), ("'Open Url'",), ('self.urlOpen',)),
                                 (("'document-new'", 'None', "'&New (clear)'"),("'Ctrl+N'",), ("'Clear the RE'",), ('self.newRe',)),
                                 #(("'document-save-as'", 'None', "'&Save As'"),("'Ctrl+S'",), ("'Save RE as'",), ('self.fileSaveAs',)),
                                 #(("'document-print'", 'None', "'&Print'"),("'Ctrl+P'",), ("'Print RE'",), ('self.printRe',)),
                                 (("'application-exit'", 'None', "'&Quit'"),("'Ctrl+Q'",), ("'Exit PyREx'",), ('self.close',)) ],
                     "&Edit" : [ (("'edit-undo'", 'None', "'&Undo'"),("'Ctrl+Z'",), ("'Undo'",), ('self.dummy',)),
                                 (("'edit-redo'", 'None', "'&Redo'"),("'Ctrl+Shift+Z'",), ("'Redo'",), ('self.dummy',)) ],
                                 #(("'edit-cut'", 'None', "'Cu&t'"),("'Ctrl+X'",), ("'Cut'",), ('self.dummy',)),
                                 #(("'edit-copy'", 'None', "'&Copy'"),("'Ctrl+C'",), ("'Copy'",), ('self.dummy',)),
                                 #(("'edit-paste'", 'None', "'&Paste'"),("'Ctrl+V'",), ("'Paste'",), ('self.dummy',)) ],
                     "&Help" : [ (("'help-content'", 'None', "'PyREx &Help'"),("'F1'",), ("'Help'",), ('self.dummy',)),
                                 (("'help-license'", 'None', "'&License'"),("'Ctrl+L'",), ("'License Information'",), ('self.dummy',)),
                                 (("'help-visit'", 'None', "'Visit the Developer'"),("''",), ("'Visit www.stamoulohta.com'",), ('self.visitMe',)),
                                 (("'help-about'", 'None', "'&About'"),("'Ctrl+A'",), ("'About'",), ('self.dummy',)) ] }
        menuActions["toolBar"] =  [ menuActions["&File"][2], menuActions["&File"][0], menuActions["&File"][1],
                                    menuActions["&Edit"][0], menuActions["&Edit"][1] ]

        for x, act in enumerate(menuActions[menu]):
            for y, arg in enumerate(act):
                if menu is not "toolBar" or y != 2:
                    if y != 0 : arg = (x,)+arg
                    exec(pattern[y] % arg)
        return actionAid

def main():
    """Main function. Start of the program."""
    app = QtGui.QApplication(sys.argv)
    pyrex = PyRExWid()
    sys.exit(app.exec_())

#======================================================================================================================#

if(__name__=="__main__"): main()
