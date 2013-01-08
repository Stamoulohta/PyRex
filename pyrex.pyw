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
from os.path import expanduser
from PySide import QtGui, QtCore
from urllib2 import urlopen, URLError
from Dialogs import UrlDialog, FileDialog

from PyRExPorts import * # Automated extention import!

re = RELib.__subclasses__()[0]() #TODO make it extendable already!!

COLORS =[QtGui.QColor("Red"), QtGui.QColor("Lime")]

class PyRExPainter(QtGui.QTextCursor):                  # Not using QSyntaxHighlighter due to the need of multiline text blocks.
    """Highlighting Cursor Class."""

    PAINTING = False
    STOP     = False

    def __init__(self, reditor, rematch):
        """Class constructor."""
        super(PyRExPainter, self).__init__(rematch.document())
        self.document().contentsChanged.connect(self.enqueue)
        self.queue = self.Enqueuer(self)
        self.reditor = reditor
        self.rematch = rematch
        self.initColorscheme()

    def initColorscheme(self):
        """Creates The character formats to be used."""
        self.default = QtGui.QTextCharFormat()
        self.pallete=[QtGui.QTextCharFormat() for i in range(2)]
        self.pallete[0].setBackground(COLORS[0])
        self.pallete[1].setBackground(COLORS[1])

    def forceStop(self, stop):
        """Used for exiting the pain_t loop when application exits."""
        self.STOP = stop

    def begin(self):
        """Initiates the highlighing procedure."""
        self.STOP = False
        self.unFormat()
        self.pain_t()

    def enqueue(self):
        """Initiates the Enqueueing thread."""
        while self.queue.isRunning():
            pass
        self.queue = self.Enqueuer(self)
        self.queue.Stopped.connect(self.begin)
        self.queue.start()

    def pain_t(self):
        """The actual highlighting loop."""
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
                QtCore.QCoreApplication.processEvents()
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
        """Sets the character format inbetween the indexes."""
        self.setPosition(frm, self.MoveAnchor)
        self.setPosition(to,  self.KeepAnchor)
        self.setCharFormat(form)

    def unFormat(self):
        """Clears the format of the whole document."""
        self.document().blockSignals(True)
        self.select(self.Document)
        self.setCharFormat(self.default)
        self.document().blockSignals(False)

    class Enqueuer(QtCore.QThread):
        """Stops the pain_t loop from a seperate thread."""

        Stopped = QtCore.Signal()

        def __init__(self, outer, parent=None):
            """Class constructor."""
            super(PyRExPainter.Enqueuer, self).__init__(parent)
            self.outer = outer
            if self.outer.PAINTING:
                self.outer.STOP = True

        def run(self):
            """Just waits for the pain_t loop to exit
            before emiting the Stopped signal."""
            while self.outer.STOP and self.outer.PAINTING:
                pass
            self.Stopped.emit()

class PyRExEdit(QtGui.QLineEdit):
    """QLineEdit extention for typing regex patterns."""

    PLACEHOLDER = "type your regex"

    def __init__(self, parent):
        """Class constructor."""
        super(PyRExEdit, self).__init__(parent)
        self.setPlaceholderText(self.PLACEHOLDER)

    def linkTo(self, rematch):
        """Creates a PyRExPainter instance and connects the textChanged signal to it."""
        self.renoir = PyRExPainter(self, rematch)
        self.textChanged.connect(self.renoir.enqueue)

class PyRExMatchBox(QtGui.QTextEdit):
    """QTextEdit extention for the sample text."""

    def __init__(self, parent = None):
        """Class constructor."""
        super(PyRExMatchBox, self).__init__(parent)
        self.initGui()

    def initGui(self):
        """Overlays the BusyBar widget."""
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
        """Sets the state."""
        if busy:
            self.bbar.reset()
            self.bbar.show()
        else:
            self.bbar.hide()
        self.setReadOnly(busy)

    def setBBarValue(self, value):
        """Sets BusyBar's current value."""
        self.bbar.setValue(value)

    def setBBarRange(self, maximum):
        """Sets BusyBar's range."""
        self.bbar.setRange(0, maximum)

    class BusyBar(QtGui.QProgressBar):
        """QProgressBar extention class."""

        def __init__(self, parent=None):
            """Class constructor."""
            super(PyRExMatchBox.BusyBar, self).__init__(parent)
            effect = QtGui.QGraphicsOpacityEffect(self)
            effect.setOpacity(0.7)
            self.setGraphicsEffect(effect)
            self.setTextVisible(False)

class PyRExTV(QtGui.QTableView):
    """QTableView extention for presenting the results."""

    def __init__(self, parent):
        """Class constructor."""
        super(PyRExTV, self).__init__(parent)
        self.initGui()
        self.setup()

    def initGui(self):
        """Tweeks options."""
        self.setCornerButtonEnabled(False)
        self.horizontalHeader().setStretchLastSection(True)

    def setup(self):
        """Sets the Model and connects the current re to it."""
        self.model = self.ResultsModel(self)
        re.setModel(self.model)
        self.setModel(self.model)
        self.clicked.connect(self.onClick)

    def linkTo(self, rematch):
        """References the PyRExMatchBox instance."""
        self.rematch = rematch

    def onClick(self, index):
        """Selects text in PyRExMatchBox instance acording to which result item got clicked."""
        span = self.model.getSpan(index.row())
        cur = self.rematch.textCursor()
        if cur and span:
            cur.setPosition(span[0], cur.MoveAnchor)
            cur.setPosition(span[1], cur.KeepAnchor)
            self.rematch.setTextCursor(cur)

    def showError(self, error):
        """Invokes the Models's showError function."""
        self.model.showError(error)

    class ResRow(object):
        """Model-Item class."""

        def __init__(self, data, color = QtGui.QColor("Black"), span=None):
            """Class constructor."""
            self.index = data[0]
            self.group = data[1]
            self.color = color
            self.span = span

        def getGroup(self):
            """Returns the group string."""
            return self.group

        def getIndex(self):
            """Returns the index string."""
            return self.index

        def getColor(self):
            """Returns the background color."""
            return self.color

        def getSpan(self):
            """Returns the span tuple or None."""
            return self.span

    class ResultsModel(QtCore.QAbstractTableModel):
        """The default Model class."""

        HEADER = LABEL = "GROUP"
        ERROR = "ERROR"
        rows = []
        cols = 1

        def __init__(self, parent = None):
            """Class constructor."""
            super(PyRExTV.ResultsModel, self).__init__(parent)

        def clear(self):
            """Resets the Model."""
            self.beginResetModel()
            self.HEADER = self.LABEL
            self.rows=[]
            self.endResetModel()

        def showError(self, err):
            """Creates an error Model-Item."""
            self.beginResetModel()
            self.HEADER = self.ERROR
            self.rows= [PyRExTV.ResRow([None, err])]
            self.endResetModel()

        def columnCount(self, index):
            """Returns the number of columns."""
            if index.isValid():
                return 0
            return self.cols

        def rowCount(self, index):
            """Returns the number of rows/items."""
            if index.isValid():
                return 0
            return len(self.rows)

        def data(self, index, role):
            """Retrieves and returns the requested data."""
            if not index.isValid():
                return None
            if not 0 <= index.row() < len(self.rows):
                return None
            if role == QtCore.Qt.DisplayRole:
                return self.rows[index.row()].getGroup()
            if role == QtCore.Qt.BackgroundColorRole:
                return self.rows[index.row()].getColor()
            if role == QtCore.Qt.ForegroundRole:
                if QtGui.QColor("Black") == self.rows[index.row()].getColor():
                    return QtGui.QColor("Red")

        def headerData(self, section, orientation, role):
            """Retrieves and returns the requested header data."""
            if role == QtCore.Qt.DisplayRole:
                if orientation == QtCore.Qt.Horizontal:
                    return self.HEADER
                else:
                    return self.rows[section].getIndex()
            return None

        def setMatches(self, matches):
            """Creates and sets the Model-Items for the matches."""
            c = 0
            for match in matches:
                i = 0;
                for i in range(match.lastindex + 1): # TODO named groups.
                    self.rows.append(PyRExTV.ResRow([i, match.group(i)], COLORS[c], match.span(i)))
                c += 1
                c = (c % 2)

        def getSpan(self, index):
            """Returns the span of the indexed Model-Item."""
            return self.rows[index].getSpan()

class PyRExWid(QtGui.QMainWindow):
    """Main window class."""

    def __init__(self):
        """Class constructor."""
        super(PyRExWid, self).__init__(None)
        self.shapeUp()

    def shapeUp(self):
        """Calls the initiation functions."""
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
        """Centers the window to screen."""
        block = self.frameGeometry()
        bullseye = QtGui.QDesktopWidget().availableGeometry().center()
        block.moveCenter(bullseye)
        self.move(block.topLeft())

    def getMenuBar(self):
        """Creates the menu."""
        menuBar = self.menuBar()
        menus=[ "&File", "&Edit", "&Help" ] #TODO "&Libraries" and maybe some 'tools' or 'view'?
        for menu in menus:
            fileMenu = menuBar.addMenu(menu)
            for action in self.getMenuActions(menu):
                fileMenu.addAction(action)

    def getToolbar(self):
        """Creates the toolbar."""
        toolBar = self.addToolBar("Tools")
        for tool in self.getMenuActions("toolBar"):
            toolBar.addAction(tool)

    def getContent(self):
        """Creates and aranges the widget instances."""
        self.reditor = PyRExEdit(self)
        self.retrieve = QtGui.QPushButton(QtGui.QIcon.fromTheme("edit-copy",\
                                                QtGui.QIcon('icons/edit-copy.png')), None)
        self.rematch = PyRExMatchBox(self)
        self.results = PyRExTV(self)

        top  = QtGui.QHBoxLayout()
        splt = QtGui.QSplitter(QtCore.Qt.Horizontal)
        wrap = QtGui.QVBoxLayout()

        top.addWidget(self.reditor, 1)
        top.addWidget(self.retrieve, 0)

        splt.addWidget(self.rematch)
        splt.addWidget(self.results)
        splt.setSizes([750,250])

        wrap.addLayout(self.getReFlagsLayout(re))
        wrap.addLayout(top, 0)
        wrap.addWidget(splt, 1)

        mainWidget = QtGui.QWidget()
        mainWidget.setLayout(wrap)
        return mainWidget

    def getReFlagsLayout(self, libModule):
        """Creates and returns the re options layout."""
        flagwrap = QtGui.QHBoxLayout() #TODO maybe make flagwrap a custom class??
        for flag in libModule.getFlags():
            chkF = QtGui.QCheckBox(flag)
            chkF.stateChanged.connect(self.registerFlag)
            flagwrap.addWidget(chkF)
        return flagwrap

    def setUp(self):
        """References the clipboard and links the widgets."""
        self.clipBoard = QtGui.QApplication.clipboard()
        self.reditor.linkTo(self.rematch)
        self.results.linkTo(self.rematch)

    def setSignals(self):
        """Conects signals to slots."""
        self.retrieve.clicked.connect(self.updateClipBoard)

    def closeEvent(self, event):
        """Slot function. Forces PyRExPainter to stop looping (pain_t) if window is closed."""
        self.reditor.renoir.forceStop(True)
        event.accept()

    def registerFlag(self):
        """Slot function. Sets the selected re option."""
        cbox = self.sender()
        key = cbox.text()
        val = QtCore.Qt.CheckState.Checked == cbox.checkState()
        re.setFlag(key, val)
        self.reditor.renoir.enqueue()


    def updateClipBoard(self):
        """Updates the clipboard."""
        self.clipBoard.setText(self.reditor.text(), QtGui.QClipboard.Clipboard)
        self.clipBoard.setText(self.reditor.text(), QtGui.QClipboard.Selection)

    def newRe(self):
        """Reset the PyRExEdit instance."""
        self.reditor.clear()

    def fileOpen(self):
        """Pops a file dialog and reads the selected file to the PyRExMatchBox instance."""
        fileName = FileDialog.getOpenFileName(self, "Open File", expanduser("~"))[0]
        if fileName:
            try:
                with open(fileName, "r") as f:
                    self.rematch.setText(f.read())
            except IOError as ioerr:
                self.results.showError(ioerr.strerror)

    def urlOpen(self):
        """Pops a url dialog and reads the responce to the PyRExMatchBox instance."""
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
        """Opens my web page in a tab in the default system browser."""
        url = "http://www.stamoulohta.com"
        webbrowser.open_new_tab(url)

    def dummy(self):
        """Dummy function"""
        print("you are dummy 8*!")

    def getMenuActions(self, menu):
        """Creates and returns the appropriate QActions for the menus and toolbar."""
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
