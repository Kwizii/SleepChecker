# SleepChecker

目的：在电脑使用时启动一个HTTP服务器，在锁屏后关闭这个服务器。配合Tasker可以实现根据电脑锁屏状态来决定手机息屏。\
原理：电脑在息屏时会创建`LogonUI.exe`的进程，用是否存在这个进程判断是否开启HTTP服务器用于Tasker请求。\
注意：服务器启动的默认端口为`6464`(固定IP和端口给Tasker请求),如果有冲突可以在代码中修改后重新打包。另外，如果设备无法成功请求该服务器，请检查是否是电脑防火墙的原因。

### 重新打包EXE(需要pip安装pyinstaller或这nuitka)

使用pyinstaller打包(生成后的应用目录在`dist`,注意将logo.png图片和exe放到一起,托盘图标需要这个文件):

```
pyinstaller -F -w -y --clean -n SleepChecker -i .\logo.ico .\main.py
```

或使用nuitka打包

```
python -m nuitka --disable-console --windows-icon-from-ico=./logo.ico --enable-plugin=pyside6 --onefile main.py
```