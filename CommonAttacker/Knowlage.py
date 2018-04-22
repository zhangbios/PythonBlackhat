# encoding: utf-8
"""

"""
from ctypes import *

p = create_string_buffer(5)
print(sizeof(p))
print(repr(p.raw))
p.raw = 'Hi'.encode('utf-8')
print(repr(p.raw))
print(p.value)