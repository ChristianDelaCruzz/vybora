"""Global image cache to prevent re-downloading images and causing delays."""
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl, QObject, Signal

# GLOBAL MANAGER: keeps the download alive even if the page is destroyed
_NETWORK_MANAGER = QNetworkAccessManager()
_IMAGE_CACHE: dict[str, QPixmap] = {}
_PENDING_CALLBACKS: dict[str, list] = {}

class ImageLoader(QObject):
    loaded = Signal(QPixmap)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def start(self):
        if self.url in _IMAGE_CACHE:
            self.loaded.emit(_IMAGE_CACHE[self.url])
            return

        if self.url in _PENDING_CALLBACKS:
            _PENDING_CALLBACKS[self.url].append(self.loaded.emit)
            return

        _PENDING_CALLBACKS[self.url] = [self.loaded.emit]
        
        request = QNetworkRequest(QUrl(self.url))
        reply = _NETWORK_MANAGER.get(request)
        
        def on_finished():
            try:
                if reply.error() == QNetworkReply.NetworkError.NoError:
                    pix = QPixmap()
                    pix.loadFromData(reply.readAll().data())
                    _IMAGE_CACHE[self.url] = pix
                    
                    for callback in _PENDING_CALLBACKS.pop(self.url, []):
                        try:
                            callback(pix)
                        except RuntimeError:
                            pass
            finally:
                reply.deleteLater()

        reply.finished.connect(on_finished)