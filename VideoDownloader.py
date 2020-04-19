# -*- coding: utf-8 -*-
# website: http://30daydo.com
# @Time : 2020/4/19 1:13
# @File : VideoDownloader.py
import os
import threading
import subprocess
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox
from FormMain import Ui_Form
from website_list import Ui_Form as sub_ui
import sys

class VideoDownload(QMainWindow,Ui_Form):
    def __init__(self):
        super(VideoDownload,self).__init__()
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.download)
        self.pushButton.clicked.connect(self.show_website)
        self.you_get_path=''
        self.CMD = 'python you-get --debug {}'
        self.show()

    def show_website(self):
        ui=sub_ui()
        parent = QMainWindow()
        ui.setupUi(parent)
        parent.show()

    def download(self):
        url = self.lineEdit.text()
        if not os.path.exists('you-get'):
            QMessageBox.warning(self, "注意", "下载出错，请更新最新程序！", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return None
        if len(url)<5:
            QMessageBox.about(self, "注意", "请填写正确的视频URL")
            return None
        task=threading.Thread(target=self.download_thread,args=(url,))
        task.start()
        print('正在下载')

    def download_thread(self,url):
        print('下载ing')
        self.label_2.setText('正在下载，请耐心等待')
        try:
            p = subprocess.Popen(self.CMD.format(url), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 shell=True)

            output, error = p.communicate()
        except Exception as e:
            QMessageBox.warning(self, "注意", "下载出错，请更新最新程序！", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            output_str = output.decode()
            if len(output_str) == 0:
                QMessageBox.warning(self, "注意", "下载超时，请重试", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            else:
                self.label_2.setText('影片已经下载完成')

if __name__=='__main__':
    app = QApplication(sys.argv)
    wind= VideoDownload()
    sys.exit(app.exec_())