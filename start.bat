@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 检查是否存在便携版Python
if exist "python\python.exe" (
    set PYTHON_PATH=python\python.exe
) else (
    :: 检查系统是否安装了Python
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_PATH=python
    ) else (
        echo 未检测到Python环境！
        echo 请确保以下任一条件满足：
        echo 1. 项目目录下存在python文件夹（包含便携版Python）
        echo 2. 系统已安装Python并添加到环境变量
        echo.
        echo 按任意键退出...
        pause >nul
        exit /b 1
    )
)

:: 启动程序
echo 正在启动程序...
"%PYTHON_PATH%" ui.py

endlocal