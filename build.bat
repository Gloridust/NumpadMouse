@echo off
echo 正在安装/更新依赖包...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo 正在构建可执行文件...
python setup.py build

echo.
echo 构建完成！可执行文件位于 build 文件夹中。
pause