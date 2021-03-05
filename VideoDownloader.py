# -*- coding: utf-8 -*-
# website: http://30daydo.com
# @Time : 2020/4/19 1:13
# @File : VideoDownloader.py
import os
import random
import threading
import subprocess
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from ui.FormMain import Ui_Form
from ui.website_list import Ui_Form as sub_ui
from config import path
from loguru import logger
from PyQt5.QtWidgets import QFileDialog

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
        self.loadFromFile_btn.clicked.connect(self.open_file)

        self.YOU_GET_PATH = path  # you-get 下载路径
        self.CMD = 'python {} --debug {}'
        self.file = 'queue'
        if not os.path.exists(self.file):
            self.task_dict = {'Done': [], 'Todo': []}
        else:
            self.fp = open(self.file, 'rb')
            self.task_dict = pickle.load(self.fp)
        self.show()


    @property
    def pending_task(self):
        return self.task_dict['Todo']

    def delete_task(self,id):
        try:
            self.task_dict['Todo'].remove(id)

        except Exception as e:
            print(e)

    def show_pending(self):
        print(self.pending_task)
        
    def closeEvent(self, event):

        self.update_file()
        event.accept()

    def show_website(self):
        ui = sub_ui()
        parent = QMainWindow()
        ui.setupUi(parent)
        parent.show()

    def open_file(self):
        fileName, filetype = QFileDialog.getOpenFileName(self,
                                                         "选取文件",
                                                         "C:/",
                                                         "All Files (*);;Text Files (*.txt)")  # 设置文件扩展名过滤,注意用双分号间隔

        if not filename:
            return
            
        url_list = self.read_from_file(fileName)
        for url in url_list:
            if len(url) > 5 and url.startswith('http'):
                self.add(url)

    def add_queue(self):
        url = self.lineEdit.text()
        if not os.path.exists(self.YOU_GET_PATH):
            QMessageBox.warning(self, "注意", "下载出错，请更新最新程序！",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return None

        if len(url) < 5:
            QMessageBox.about(self, "注意", "请填写正确的视频URL")
            return None

        self.add(url)
        self.update_file()

    def update_file(self):
        with open(self.file, 'wb') as fp:
            pickle.dump(self.task_dict, fp)
            fp.close()

    def add(self, url):
        '''
        加入队列
        '''
        if url not in self.task_dict['Todo']:
            self.logger.info(f'添加任务URL： {url}')
            self.task_dict['Todo'].append(url)
        else:
            self.logger.info(f'任务URL{url} 已经存在！')

    def download(self):
        '''
        开始下载
        '''
        task = threading.Thread(target=self.download_thread, args=())
        task.setDaemon(True)
        task.start()

    def read_from_file(self, filename):
        with open(filename, 'r') as f:
            return f.readlines()

    def download_thread(self):

        while True:
            self.label_2.setText('正在下载，请耐心等待')
            l = len(self.task_dict['Todo'])
            if l == 0:
                print('没有任务，退出循环')
                break

            num = random.randint(0, l-1)
            url = self.task_dict['Todo'][num]

            try:
                self.logger.info(self.CMD.format(self.YOU_GET_PATH, url))
                p = subprocess.Popen(self.CMD.format(self.YOU_GET_PATH, url), stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     shell=True)

                output, error = p.communicate()
            except Exception as e:
                self.logger.error('注意", "下载出错，请更新最新程序！')
                # QMessageBox.warning(self, "注意", "下载出错，请更新最新程序！", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            else:
                if not isinstance(output, str):
                    output = output.decode()

                if len(output) == 0:
                    # QMessageBox.warning(self, "注意", "下载超时，请重试", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    self.logger.error("注意", "下载超时，请重试")
                else:
                    self.label_2.setText('影片已经下载完成')
                    self.logger.info(f'影片下载完成{url}')
                    self.task_dict['Todo'].remove(url)
                    self.task_dict['Done'].append(url)
                    self.update_file()
