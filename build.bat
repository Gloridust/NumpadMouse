@echo off
echo 正在编译 NumpadMouse...
echo.

REM 检查是否安装了所需的包
echo 检查依赖包...
pip install -r requirements.txt

echo.
echo 开始编译...
python setup.py build

echo.
echo 编译完成！
echo 可执行文件位于 build 目录中
pause