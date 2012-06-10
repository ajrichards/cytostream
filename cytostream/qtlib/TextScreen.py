import os
import sys
from PyQt4 import QtCore, QtGui

def main():
    app = QtGui.QApplication(sys.argv)
    w = TextScreen()
    w.show()
    sys.exit(app.exec_())

class TextScreen(QtGui.QWidget):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)

        # create objects
        #label = QtGui.QLabel(self.tr("Enter command and press Return"))
        #self.le = QtGui.QLineEdit()
        self.allLines = []
        self.textEdit = QtGui.QTextEdit()
        self.textEdit.setTextColor(QtGui.QColor("#000000"))
        self.textEdit.setEnabled(False)

        palette = self.textEdit.palette()
        role = self.textEdit.backgroundRole()
        palette.setColor(role, QtGui.QColor("#000000"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # finalize layout
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)

        ## add start text
        self.add_text("Cytostream model progress")
        self.add_text("Waiting to proceed...")

    def add_text(self,txt):
        self.allLines.append(txt)
        toWrite = ''
        for line in self.allLines:
            toWrite += "\n"+line

        self.textEdit.setText(toWrite)

    def clear_text(self):
        self.allLines = []
        self.textEdit.setText('')

if __name__ == "__main__":
    main()
