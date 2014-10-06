import codecs
import base64

try:
    from PyQt4 import QtGui, QtCore, QtSql
    from PyQt4.uic import loadUiType
except ImportError:
    from PySide import QtGui, QtCore, QtSql
    from loadui import loadUiType

import commands

form_class, base_class = loadUiType('./widgets/blob.ui')


class BlobDialog(base_class):
    def __init__(self, parent=None):
        super(BlobDialog, self).__init__(parent)
        
        self._ui = form_class()
        self._ui.setupUi(self)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self._ui.tContent.textChanged.connect(self.__contentChanged)
        self._ui.bText.clicked.connect(self.__textHandler)
        self._ui.bImage.clicked.connect(self.__imageHandler)
        self._ui.bLoad.clicked.connect(self.__loadHandler)
        self._ui.bOk.clicked.connect(self.__acceptHandler)
        self._ui.bCancel.clicked.connect(self.close)
        
        self.__textHandler()
        
        self._initialValue = u''
        self._content = u''
        self._isaccepted = False
    
    def content(self):
        if self._isaccepted:
            if self._ui.ckSetNull.isChecked():
                return None
            
            if commands.istext(self._content):
                return self._ui.tContent.document().toPlainText()
            else:
                return self._content
        else:
            return self._initialValue
    
    def setContent(self, content):
        self._content = content
        if content is None:
            self._ui.ckSetNull.setChecked(True)
            
            return
        
        content = u"".join(i for i in content if ord(i)<128)
        content = content.decode('string-escape')
        self._ui.tContent.setPlainText(content)
        self._initialValue = content
    
    def __imageHandler(self):
        self._ui.tContent.setVisible(False)
        self._ui.wImage.setVisible(True)
        
        data = QtCore.QByteArray(self._content)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(data)
        self._ui.lImage.setPixmap(pixmap)

    def __textHandler(self):
        self._ui.tContent.setVisible(True)
        self._ui.wImage.setVisible(False)
    
    def __contentChanged(self):
        if self._content is None:
            length = 0
        else:
            length = len(self._content)
        self._ui.lSize.setText(str(length))
    
    def __acceptHandler(self):
        self._isaccepted = True
        self.close()
    
    def __loadHandler(self):
        file_ = QtGui.QFileDialog.getOpenFileName(self)
        if isinstance(file_, (list, tuple)):
            file_ = file_[0]
        
        if file_:
            fh = open(file_, 'rb')
            data = fh.read()
            fh.close()
            self._ui.tContent.setPlainText(data)
            self._content = data
            self.__contentChanged()
