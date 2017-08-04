from __future__ import division
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtCore import Qt
from PyQt4.QtWebKit import QWebView

from segyviewlib import resource_html


class HelpWindow(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent, Qt.WindowStaysOnTopHint | Qt.Window)
        self.setVisible(False)

        self._view_help = QWebView(self)
        self._view_help.load(resource_html("helppage.html"))
        self._view_help.show()

        f_layout = QHBoxLayout()
        f_layout.addWidget(self._view_help)

        self.setLayout(f_layout)
