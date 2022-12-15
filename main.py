import base64
import io
import socket
import subprocess
import sys
import threading
from time import sleep

import PIL.Image
import pystray


def win_locked() -> bool:
    # 获取所有进程判断是否存在LogonUI.exe
    process_name = 'LogonUI.exe'
    call_all = 'TASKLIST'
    CREATE_NO_WINDOW = 0x08000000
    output_all = subprocess.check_output(call_all, creationflags=CREATE_NO_WINDOW)
    output_string_all = str(output_all)
    if process_name in output_string_all:
        return True
    else:
        return False


class HttpServer:
    def __init__(self):
        self.running = False
        self.accept_thread = None
        self.tcp_server_socket = None

    def accept(self) -> None:
        while self.running:
            try:
                new_socket, ip_port = self.tcp_server_socket.accept()
                response_line = "HTTP/1.1 200 OK\r\n"
                response_data = (response_line + "\r\n").encode('utf-8')
                new_socket.send(response_data)
                new_socket.close()
            except Exception:
                pass
            finally:
                sleep(0.5)

    def run(self) -> None:
        if not self.running:
            self.running = True
            self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            self.tcp_server_socket.bind(('', 6464))
            self.tcp_server_socket.listen(4)
            self.accept_thread = threading.Thread(target=self.accept, daemon=True)
            self.accept_thread.start()

    def stop(self) -> None:
        if self.running:
            self.running = False
            self.tcp_server_socket.close()


def main() -> None:
    global status_item
    server = HttpServer()
    while True:
        if win_locked():
            server.stop()
            status_item = pystray.MenuItem('STOPPED', None, enabled=False)
        else:
            server.run()
            status_item = pystray.MenuItem('RUNNING', None, enabled=False)
        sleep(3)


# 图片的BASE64编码
base64_img = 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAA5RJREFUWEfNV11oHFUYPWeSGBVsUauiINUgaXY2syD2wRdFsY/+4G9F0YfWtigUWpDZTRWsoM3uIFQoKK0/D4LSahX8eawo9sWHtsJOdjYNJfUHFGu1JOJPbDJHJmS3M7Oz6Z0mgvt47/nOOXfud/eeSxj+1rjjl1nW2XVWiPWiBiGuAnHlfLnwK6jTFCdCCwfCsO/QcW/odxNqng807PoFEVsFPArg8vPhF+bPENhPYc+Y5zQXq1nUQLHivyRwK6QVhsJJGDlNaE+j6jzfrb6rAdutfwXytgsSThdJhwOvdHsWV6YB2/V/AbGqs0ATED8NLXwG9v6oOf4UYdija6HZ66wQd4O6B+BgR61wOvCcq9LjHQbs8thJQDekgEdB7QuqpX0mX8Su1DdD3AzgltSefBvUhm+MjyUM2OWx9wE9nCr6IKgNP2IinMaY8LUNzDec8FyCRNgZeM6LFyLeqrFd/wUQOxOrJl5uNea8geiohRa/TnQ7MRpUnR1LEW+bqPi7IIy0uchpK9St0RGdN1As+68JeDomdjSoOWuXQ7xtouwfifcEgdcbNecZDpSPrLwY/d8BWHnOobaYNpypyYXG3BvDT/2NmdUsuP4TJN5pTUg62fRKA6bEeXAFtz5Jsn0KJDxJu+wfBPBgi4jCmw3P2ZSH2BRbdP03RDwVw39Iu1w/BvDm1mBI3Dledb40Jc2DG6r4d1jCF+dq9A1t1/8exPVtA1bvmvHRwkQeYlPs0Ehz0Apnj7fxwg/RFvwB4NLW4Jz6VphepabCLVx0pffw7HSs7s8OA71zl1xTf+WmU3nJTfClZ09cPdvz189JA6ktgKx1gVf83IQwL8Z2G3eB4aHUFiSbUOL2pjf8al5yE3zBHdtGaneiCYuuv1/E+hjB20HN2WhCmBdjl/23AGyIHfkDLFT8+yl8lJdsOfAiHuBCZ0Z/xaZ5bzm0I44zc+pb3e0yWi6RrjztyyhCZF7H/6WF9HUcaWUFEkm1pleqLMVLwa1XSZbjHEwHktZklyS8l/9YOxq7i7/lMVLc3rhCF4W7AGxJ1KUScmcozUzEbEDhaOCV3jUxYbv1x0FrBFAxKd6ZjLNjeXYyhog6pMMiD2bFckoPRW8JCqVOo+xIxBGm+8MkMyGbrD8Lw67J+v/7NGutI/Y4fSyRGxf/GFME3lvy4zSuEYXXfvXfS+I+QANZz3OAkxI+nuHMJ5O1tVMmG/YvWfCH9OaIJDgAAAAASUVORK5CYII='
status_item = pystray.MenuItem("RUNNING", None, enabled=False)

if __name__ == '__main__':
    tray_logo = PIL.Image.open(io.BytesIO(base64.b64decode(base64_img)))  # 转换图片格式至托盘图标
    # 设置菜单的两个项 一个显示运行状态 一个用于退出程序
    icon = pystray.Icon("SleepChecker", tray_logo, menu=pystray.Menu(
        status_item,
        pystray.MenuItem("Exit", pystray.Icon.stop)))
    # 另起一个线程用于启动服务器
    threading.Thread(target=main, daemon=True).start()
    icon.run()
    sys.exit(0)
