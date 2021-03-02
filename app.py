from VideoDownloader import VideoDownload
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wind = VideoDownload()
    sys.exit(app.exec_())
