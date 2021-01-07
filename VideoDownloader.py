# -*- coding: utf-8 -*-
# website: http://30daydo.com
# @Time : 2020/4/19 1:13
# @File : VideoDownloader.py
import os
import random
import threading
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from FormMain import Ui_Form
from website_list import Ui_Form as sub_ui
import sys
from config import path
from loguru import logger
try:
    import cPickle as pickle
except:
    import pickle


class VideoDownload(QMainWindow, Ui_Form):

    def __init__(self):
        super(VideoDownload, self).__init__()
        self.setupUi(self)
        self.logger = logger
        self.logger.add('applog')
        self.logger.info('启动.....')
        self.download_btn.clicked.connect(self.download)
        self.addqueue_btn.clicked.connect(self.add_queue)
        self.pushButton.clicked.connect(self.show_website)
        self.YOU_GET_PATH = path # you-get 下载路径
        self.CMD = 'python {} --debug {}'
        self.file = 'queue'
        if not os.path.exists(self.file):
            self.task_dict ={'Done':[],'Todo':[]}
        else:
            self.fp = open(self.file,'rb')
            self.task_dict = pickle.load(self.fp)
        self.show()

    def closeEvent(self,event):

        self.update_file()
        event.accept()

    def show_website(self):
        ui = sub_ui()
        parent = QMainWindow()
        ui.setupUi(parent)
        parent.show()

    def add_queue(self):
        url = self.lineEdit.text()
        if not os.path.exists(self.YOU_GET_PATH):
            QMessageBox.warning(self, "注意", "下载出错，请更新最新程序！", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return None

        if len(url) < 5:
            QMessageBox.about(self, "注意", "请填写正确的视频URL")
            return None
        if url not in self.task_dict['Todo']:
            self.logger.info(f'添加任务URL： {url}')
            self.task_dict['Todo'].append(url)
        else:
            self.logger.info(f'任务URL{url} 已经存在！')

        self.update_file()

    def update_file(self):
        with open(self.file,'wb') as fp:
            pickle.dump(self.task_dict,fp)
            fp.close()


    def download(self):
        task = threading.Thread(target=self.download_thread, args=())
        task.setDaemon(True)
        task.start()

    def download_thread(self):

        while True:
            self.label_2.setText('正在下载，请耐心等待')
            l = len(self.task_dict['Todo'])
            if l==0:
                print('没有任务，退出循环')
                break

            num = random.randint(0,l-1)
            url = self.task_dict['Todo'][num]

            try:
                self.logger.info(self.CMD.format(self.YOU_GET_PATH, url))
                p = subprocess.Popen(self.CMD.format(self.YOU_GET_PATH, url), stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     shell=True)

                output, error = p.communicate()
            except Exception as e:

                QMessageBox.warning(self, "注意", "下载出错，请更新最新程序！", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            else:
                if not isinstance(output,str):
                    output = output.decode()

                if len(output) == 0:
                    QMessageBox.warning(self, "注意", "下载超时，请重试", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                else:
                    self.label_2.setText('影片已经下载完成')
                    self.logger.info(f'影片下载完成{url}')
                    self.task_dict['Todo'].remove(url)
                    self.task_dict['Done'].append(url)
                    self.update_file()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wind = VideoDownload()
    sys.exit(app.exec_())
