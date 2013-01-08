#!/usr/bin/env python2
# vim: fileencoding=utf-8:
#======================================================================================================================#
"""
Describe and comment the code...
"""
from PySide import QtCore, QtGui

class UrlDialog(QtGui.QWidget):
    RESULTS = (None, False)
    WWW = "www."

    def __init__(self, parent=None):
        super(UrlDialog, self).__init__(parent, QtCore.Qt.Dialog)
        self.setWindowTitle("Open URL")
        self.resize(500, 100)
        self.initGui()
        self.setup()

    def initGui(self):
        label = QtGui.QLabel("Enter url:", self)
        # referenced widgets.
        self.combo = self.ProtocolComboBox(self)
        self.txt = QtGui.QLineEdit(self.WWW, self)
        self.cancel = QtGui.QPushButton("&Cancel")
        self.ok     = QtGui.QPushButton("&OK")
        # row 1
        labellay = QtGui.QHBoxLayout()
        labellay.addWidget(label)
        # row 2
        horizontal = QtGui.QHBoxLayout()
        horizontal.addWidget(self.combo)
        horizontal.addWidget(self.txt)
        # row 3
        bottomlay = QtGui.QHBoxLayout()
        bottomlay.addStretch(1)
        bottomlay.addWidget(self.cancel)
        bottomlay.addWidget(self.ok)
        # Layout
        vertical = QtGui.QVBoxLayout(self)
        vertical.addStretch(1)
        vertical.addLayout(labellay)
        vertical.addLayout(horizontal)
        vertical.addLayout(bottomlay)
        vertical.addStretch(1)
        self.setLayout(vertical)

    def setup(self):
        self.txt.returnPressed.connect(self.urlCheck)
        self.ok.clicked.connect(self.urlCheck)
        self.cancel.clicked.connect(self.cancelDialog)

    def getUrl(self):
        self.show()
        self.txt.setFocus()
        self.eventLoop = QtCore.QEventLoop(self)
        self.eventLoop.exec_()
        self.close()
        return self.RESULTS

    def cancelDialog(self):
        self.RESULTS = (None, False)
        self.eventLoop.exit()

    def urlCheck(self):
        userinput = self.txt.text()
        if userinput in self.WWW:
            return
        else:
            self.RESULTS = (self.combo.currentText()+userinput, True)
            self.eventLoop.exit()

    class ProtocolComboBox(QtGui.QComboBox):
        def __init__(self, parent=None):
            super(UrlDialog.ProtocolComboBox, self).__init__(parent)
            for item in ["http://", "https://", "file://", "ftp://", "ftps://", "script://"]:
                self.addItem(item)


#======================================================================================================================#
def main():
    """Main function.\nJust prints info message and exits."""
    print("""This is a module, not a standalone program.\nIt extends qt dialog classes.""")
    exit(0)

if(__name__=="__main__"):
    main()
