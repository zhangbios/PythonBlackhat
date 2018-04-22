# encoding: utf-8
"""

"""
import win32gui
import win32ui
import win32api
import win32con


def get_screen():
    # 获得桌面窗口的句柄
    hdesktop = win32gui.GetDesktopWindow()

    # 获得所有显示屏的像素尺寸
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    # 创建设备描述表
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)

    # 创建基于内存的设备描述表
    mem_dc = img_dc.CreateCompatibleDC()

    # 创建位图对象
    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot)

    # 复制屏幕到我们的内存设备描述表中
    mem_dc.BitBlt((0,0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

    # 将位图保存到文件
    screenshot.SaveBitmapFile(mem_dc, 'D:\\screen.bmp')

    # 释放对象
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())


if __name__ == '__main__':
    get_screen()