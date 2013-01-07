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
from PySide import QtGui, QtCore
from os.path import expanduser
from urllib2 import urlopen, URLError
from PyRExPorts import *

re = RELib.__subclasses__()[0]() #TODO make it extendable already!!

COLORS =[QtGui.QColor("Red"), QtGui.QColor("Lime")]

class PyRExPainter(object): # Not using QSyntaxHighlighter due to the need of multiline text blocks.
    def __init__(self, reditor, rematch):
        self.reditor = reditor
        self.rematch = rematch
        self.document = rematch.document()
        self.setup()
        self.initColorscheme()

    def setup(self):
        self.document.contentsChange.connect(self.highlight)

    def initColorscheme(self):
        self.default = QtGui.QTextCharFormat()
        self.pallete=[QtGui.QTextCharFormat() for i in range(2)]
        self.pallete[0].setBackground(COLORS[0])
        self.pallete[1].setBackground(COLORS[1])

    def highlight(self):
        self.unFormat()
        pattern = self.reditor.text()
        if re.check(pattern):
            self.document.blockSignals(True)
            self.rematch.busyState(True)

            self.brush = self.BrushThread(pattern, self.document.toPlainText())
            self.brush.documentReady.connect(self.presentDocument, QtCore.Qt.QueuedConnection)
            self.brush.start()

    def presentDocument(self, document):
        self.document = document
        self.rematch.setDocument(self.document)
        self.document.blockSignals(False)
        self.rematch.busyState(False)

    def unFormat(self):
        self.document.blockSignals(True)
        cursor = self.rematch.textCursor()
        cursor.select(cursor.Document)
        cursor.setCharFormat(self.default)
        self.document.blockSignals(False)

    class BrushThread(QtCore.QThread):
        documentReady = QtCore.Signal(QtGui.QTextDocument)

        def __init__(self, pattern, txt, parent=None):
            super(PyRExPainter.BrushThread, self).__init__(parent)
            self.txt = txt
            self.pattern = pattern
            self.pallete=[QtGui.QTextCharFormat() for i in range(2)] # TWO TIMES !!! REMOVE !!
            self.pallete[0].setBackground(COLORS[0])
            self.pallete[1].setBackground(COLORS[1])

        def run(self):
            i = 0
            self.doc = QtGui.QTextDocument(self.txt)
            self.cursor = QtGui.QTextCursor(self.doc)
            for match in re.getMatches(self.pattern, self.txt):
                frm, to = match.getIndexes()
                self.setFormat(frm, to, self.pallete[i])
                i += 1
                i = (i % 2)
            type(self.doc)
            self.documentReady.emit(self.doc)

        def setFormat(self, frm, to, form):
            self.cursor.setPosition(frm, self.cursor.MoveAnchor)
            self.cursor.setPosition(to, self.cursor.KeepAnchor)
            self.cursor.setCharFormat(form)

class PyRExEdit(QtGui.QLineEdit):
    PLACEHOLDER = "type your regex"

    def __init__(self, parent):
        super(PyRExEdit, self).__init__(parent)
        self.shapeUp()

    def shapeUp(self):
        self.setPlaceholderText(self.PLACEHOLDER)

    def linkTo(self, rematch):
        self.renoir = PyRExPainter(self, rematch)
        self.textChanged.connect(self.renoir.highlight)

class PyRExMatchBox(QtGui.QTextEdit):
    def __init__(self, parent = None):
        super(PyRExMatchBox, self).__init__(parent)
        self.initGui()
        self.getContent() # TODO DELETE!!!

    def initGui(self):
        self.bbar = self.BusyBar(self)
        overLay = QtGui.QHBoxLayout(self)
        overLay.addSpacing(30)
        overLay.addWidget(self.bbar)
        overLay.addSpacing(30)
        self.setLayout(overLay)
        self.busyState(False)

    def busyState(self, busy=True):
        if busy:
            self.bbar.reset()
            self.bbar.show()
            self.setEnabled(False)
        else:
            self.bbar.hide()
            self.setEnabled(True)

    def getContent(self): # TODO DELETE!!!
        address = "http://textfiles.com/anarchy/201.txt"
        try:
            response = urlopen(address)
            self.setPlainText(response.read())
        except URLError as urlerr:
            if hasattr(urlerr, 'reason'):
                self.setPlainText(urlerr.reason)
            else:
                self.setPlainText(str(urlerr.code))

    class BusyBar(QtGui.QProgressBar):
        def __init__(self, parent=None):
            super(PyRExMatchBox.BusyBar, self).__init__(parent)
            self.setRange(0, 0)
            self.setTextVisible(False)

class PyRExTV(QtGui.QTableView):
    def __init__(self, parent):
        super(PyRExTV, self).__init__(parent)
        self.setup()

    def setup(self):
        #self.setReadOnly(True) # FIXME
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
                for i in range(match.lastindex + 1):
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
        self.reditor.renoir.highlight()


    def updateClipBoard(self):
        self.clipBoard.setText(self.reditor.text(), QtGui.QClipboard.Clipboard)
        self.clipBoard.setText(self.reditor.text(), QtGui.QClipboard.Selection)

    def fileOpen(self):#XXX give it some polish..!
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File", expanduser("~"))[0]
        if fileName:
            with open(fileName, "r") as f:
                self.rematch.setText(f.read())

    def newRe(self):
        self.reditor.clear()

    def urlOpen(self):#XXX give it some polish..!
        urlDialog = QtGui.QInputDialog()
        urlDialog.resize(800, 300) # FIXME does not work!
        address, ok = urlDialog.getText(self, "Open URL", "Enter url:")
        if ok and address:
            if not address.startswith(("http://", "https://", "file://")):
                address = "http://"+address
            try:
                response = urlopen(address)
                self.rematch.setPlainText(response.read())
            except URLError as urlerr:
                if hasattr(urlerr, 'reason'):
                    self.results.showError(str(urlerr.reason))
                else:
                    self.results.showError(str(urlerr.code))

    def fileSaveAs(self):
        # TODO either save the file human readable or with pickle.
        print("will save it for tomorrow !:)")

    def printRe(self):
        if not self.printDialog:
            printer = QtGui.QPrinter(QtGui.QPrinter.ScreenResolution)
            printer.setOutputFileName("regexp.pdf")
            self.printDialog = QtGui.QPrintDialog(printer, self) #FIXME enable output file, name, type etc...
            self.printDialog.setOptions(QtGui.QAbstractPrintDialog.PrintToFile)
        if self.printDialog.exec_() == QtGui.QDialog.Accepted:
            doc = QtGui.QTextDocument(self.reditor.text(), self)
            doc.print_(self.printDialog.printer())

    def visitMe(self):
        url = "http://www.stamoulohta.com"
        webbrowser.open_new_tab(url)

    def dummy(self):
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
                                 (("'document-save-as'", 'None', "'&Save As'"),("'Ctrl+S'",), ("'Save RE as'",), ('self.fileSaveAs',)),
                                 (("'document-print'", 'None', "'&Print'"),("'Ctrl+P'",), ("'Print RE'",), ('self.printRe',)),
                                 (("'application-exit'", 'None', "'&Quit'"),("'Ctrl+Q'",), ("'Exit PyREx'",), ('self.close',)) ],
                     "&Edit" : [ (("'edit-undo'", 'None', "'&Undo'"),("'Ctrl+Z'",), ("'Undo'",), ('self.dummy',)),
                                 (("'edit-redo'", 'None', "'&Redo'"),("'Ctrl+Shift+Z'",), ("'Redo'",), ('self.dummy',)),
                                 (("'edit-cut'", 'None', "'Cu&t'"),("'Ctrl+X'",), ("'Cut'",), ('self.dummy',)),
                                 (("'edit-copy'", 'None', "'&Copy'"),("'Ctrl+C'",), ("'Copy'",), ('self.dummy',)),
                                 (("'edit-paste'", 'None', "'&Paste'"),("'Ctrl+V'",), ("'Paste'",), ('self.dummy',)) ],
                     "&Help" : [ (("'help-content'", 'None', "'PyREx &Help'"),("'F1'",), ("'Help'",), ('self.dummy',)),
                                 (("'help-license'", 'None', "'&License'"),("'Ctrl+L'",), ("'License Information'",), ('self.dummy',)),
                                 (("'help-visit'", 'None', "'Visit the Developer'"),("''",), ("'Visit www.stamoulohta.com'",), ('self.visitMe',)),
                                 (("'help-about'", 'None', "'&About'"),("'Ctrl+A'",), ("'About'",), ('self.dummy',)) ] }
        menuActions["toolBar"] =  [ menuActions["&File"][2], menuActions["&File"][0], menuActions["&File"][1], menuActions["&File"][3],
                                    menuActions["&File"][4], menuActions["&Edit"][0], menuActions["&Edit"][1], menuActions["&Edit"][2],
                                    menuActions["&Edit"][3], menuActions["&Edit"][4] ]

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
