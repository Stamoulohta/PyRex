from PySide.QtCore import QRegExp
from rEx import RELib

class QRegExp(RELib):
    def __init__(self):
        super(QRegExp, self).__init__()
        print("QRegExp")
