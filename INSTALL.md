# AIP 安装说明

## 系统要求

### Windows
- Python 3.8+
- Windows 10/11

### Linux
- Python 3.8+
- tkinter支持 (通常需要安装 python3-tk)
- WebKit2GTK (用于pywebview)

### macOS
- Python 3.8+
- macOS 10.14+

## 安装步骤

### 1. 安装Python依赖
```bash
pip install -r requirements.txt
```

### 2. 系统特定依赖

#### Windows
Windows用户通常不需要额外安装系统依赖，pywebview会自动使用Edge WebView2。

#### Linux (Ubuntu/Debian)
```bash
# 安装tkinter支持
sudo apt-get install python3-tk

# 安装WebKit2GTK (用于pywebview)
sudo apt-get install python3-gi python3-gi-cairo gir1.2-webkit2-4.0
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# 安装tkinter支持
sudo yum install tkinter

# 安装WebKit2GTK
sudo yum install webkit2gtk3-devel
```

#### macOS
```bash
# 安装WebKit2GTK
brew install webkit2gtk
```

### 3. 验证安装
```bash
python -c "import webview; print('pywebview安装成功')"
```

## 常见问题

### Q: 提示"No module named 'webview'"
A: 运行 `pip install pywebview==4.4.1`

### Q: Linux上pywebview无法启动
A: 确保安装了WebKit2GTK依赖：
```bash
sudo apt-get install python3-gi python3-gi-cairo gir1.2-webkit2-4.0
```

### Q: tkinter无法导入
A: Linux用户需要安装tkinter支持：
```bash
sudo apt-get install python3-tk
```

### Q: Windows上WebView无法显示
A: 确保系统已安装Edge WebView2运行时

## 启动项目

### 方法1: 使用桌面应用
```bash
python ui.py
```

### 方法2: 直接启动Web服务
```bash
python app.py
```

### 方法3: 使用批处理文件 (Windows)
```bash
start.bat
```


