# coding:utf-8
"""
    在 Burp 中利用 Bing 服务
"""
from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL

import socket
import urllib
import json
import re
import base64
bing_api_key = 	"iHqAO2qQiQF28W4crY9jjTWH1QmCJj8z9pfmfdQyXrs"
# 访问 http://www.bing.com/dev/en-us/dev-center/


class BurpExtender(IBurpExtender, IContextMenuFactory):
    """
    新建 BurpExtender 类，继承并拓展 IBurpExtender 和 IContextMenuFactory 类
    """
    def registerExtenderCallbacks(self, callbacks):
        """
        注册拓展类的回调函数
        """
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None

        # 建立拓展工具
        callbacks.setExtensionName("Bios Bing!")
        callbacks.registerContextMenuFactory(self)

        return

    def createMenuItems(self, context_menu):
        """
        JMenuItem本质上是一个继承自AbstractButton的按钮，不过它又不完全等同于按钮。
        当鼠标经过某个菜单项时，Swing就认为该菜单项被选中，但并不会触发任何事件；
        当用户在菜单项上释放鼠标，此时Swing也会认为该选项被选中，并触发事件完成相应的操作
        """
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))
        return menu_list

    def bing_menu(self,event):
        """

        """
        # 获取用户点击的详细信息
        http_traffic = self.context.getSelectedMessages()
        print("{} requests highlighted".format(len(http_traffic)))

        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()
            print("User selected host:{}".format(host))
            self.bing_search(host)
        return

    def bing_search(self, host):
        # 检查参数是否是IP或者是主机名
        is_ip = re.match("[0-9]+(?:\.[0-9]+){3}", host)

        if is_ip:
            ip_address = host
            domain = False
        else:
            ip_address = socket.gethostbyname(host)
            domain = True

        bing_query_string = "'ip:{}'".format(ip_address)
        self.bing_query(bing_query_string)

        if domain:
            bing_query_string = "'domain:{}'".format(host)
            self.bing_query(bing_query_string)

    def bing_query(self, bing_query_string):
        print("Performing Bing search:{}".format(bing_query_string))
        # 编码我们的查询
        quoted_query = urllib.quote(bing_query_string)

        http_request = "GET https://api.datamarket.azure.com/Bing/Search/Web?$format=json&$top=20&Query=%s HTTP/1.1\r\n" % quoted_query
        http_request += "Host: api.datamarket.azure.com\r\n"
        http_request += "Connection: close\r\n"
        http_request += "Authorization: Basic {}\r\n".format(base64.b64encode(":{}".format(bing_api_key)))
        http_request += "User-Agent: Blackcat Python\r\n\r\n"

        json_body = self._callbacks.makeHttpRequest("api.datamarket.azure.com",443,True,http_request).tostring()
        json_body = json_body.split("\r\n\r\n",1)[1]

        try:
            r = json.loads(json_body)

            if len(r["d"]["results"]):
                for site in r["d"]["results"]:
                    print("*" * 100)
                    print(site['Title'])
                    print(site['Url'])
                    print(site['Description'])
                    print("*" * 100)

                    j_url = URL(site['Url'])
            if not self._callbacks.isInScope(j_url):
                print("Adding to Burp scope")
                self._callbacks.includeInScope(j_url)
        except:
            print("No results from Bing")
            pass

        return