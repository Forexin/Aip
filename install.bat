@echo off
chcp 65001 >nul
echo 正在安装项目依赖包...
echo.

:: 检查是否存在便携版Python
if exist "python\python.exe" (
    set PYTHON_PATH=python\python.exe
    echo 使用便携版Python: %PYTHON_PATH%
) else (
    :: 检查系统是否安装了Python
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_PATH=python
        echo 使用系统Python: %PYTHON_PATH%
    ) else (
        echo 错误：未检测到Python环境！
        echo 请确保以下任一条件满足：
        echo 1. 项目目录下存在python文件夹（包含便携版Python）
        echo 2. 系统已安装Python并添加到环境变量
        echo.
        pause
        exit /b 1
    )
)

echo.
echo 开始安装依赖包...
"%PYTHON_PATH%" -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo 依赖包安装完成！
    echo 现在可以运行 start.bat 启动程序了。
) else (
    echo.
    echo 依赖包安装失败，请检查网络连接或手动安装。
)

echo.
pause 