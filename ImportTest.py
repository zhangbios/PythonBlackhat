"""
sys.modules 保存的内容为：
当前 import 的模块包含的 库
"""
import sys


class Watcher(object):
    @classmethod
    def find_module(cls, name, path):
        print("Importing", name, path)
        return None


sys.meta_path.insert(0, Watcher)
# sys.meta_path = [Watcher()]
import socket