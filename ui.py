import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import os
import platform
import socket
import webbrowser
import threading
import time
import webview

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aip - 信息源时序队列")
        self.root.geometry("400x300")
        self.root.resizable(True, True)
        
        # 尝试设置图标
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
            
        self.process = None
        self.webview_window = None
        self.is_service_running = False

        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="信息源时序队列", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # 控制按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))

        # 启动按钮
        self.start_button = ttk.Button(button_frame, text="启动服务", command=self.start_service, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        # 停止按钮
        self.stop_button = ttk.Button(button_frame, text="停止服务", command=self.stop_service, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))

        # 打开浏览器按钮
        self.browser_button = ttk.Button(button_frame, text="打开浏览器", command=self.open_browser, state=tk.DISABLED)
        self.browser_button.pack(side=tk.LEFT)

        # 状态框架
        status_frame = ttk.LabelFrame(main_frame, text="服务状态", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 20))

        # 服务状态标签
        self.status_label = ttk.Label(status_frame, text="服务未启动", foreground="red")
        self.status_label.pack()

        # IP地址框架
        ip_frame = ttk.LabelFrame(main_frame, text="访问地址", padding="10")
        ip_frame.pack(fill=tk.X, pady=(0, 20))

        # IP地址标签
        self.ip_label = ttk.Label(ip_frame, text=f"http://{self.get_local_ip()}:5000", cursor="hand2")
        self.ip_label.pack()
        self.ip_label.bind("<Button-1>", self.copy_ip_to_clipboard)

        # 提示信息
        tip_label = ttk.Label(main_frame, text="点击IP地址可复制到剪贴板", font=("Arial", 9), foreground="gray")
        tip_label.pack()

        # 设置关闭窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def is_redis_running(self):
        try:
            socket.create_connection(('localhost', 6379), timeout=1)
            return True
        except socket.error:
            return False

    def is_service_running(self):
        try:
            socket.create_connection(('localhost', 5000), timeout=1)
            return True
        except socket.error:
            return False

    def start_service(self):
        if not self.is_redis_running():
            if platform.system() == 'Windows' and platform.architecture()[0] == '64bit':
                try:
                    subprocess.Popen([os.path.join('redis', 'redis-server.exe')])
                    messagebox.showinfo("Redis", "Redis 服务器启动成功！")
                except Exception as e:
                    messagebox.showerror("错误", f"启动 Redis 服务器失败: {e}")
                    return
            else:
                messagebox.showwarning("Redis", "请手动启动 Redis 服务器。")
                return

        if self.process is None:
            try:
                self.process = subprocess.Popen(["python", "app.py"])
                self.is_service_running = True
                
                # 更新UI状态
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                self.browser_button.config(state=tk.NORMAL)
                self.status_label.config(text="服务运行中", foreground="green")
                
                # 等待服务启动
                threading.Thread(target=self.wait_for_service, daemon=True).start()
                
                messagebox.showinfo("服务", "服务启动成功！")
                
            except Exception as e:
                messagebox.showerror("错误", f"启动服务失败: {e}")

    def wait_for_service(self):
        """等待服务启动完成"""
        max_attempts = 30
        attempts = 0
        
        while attempts < max_attempts:
            if self.is_service_running():
                # 服务已启动，可以打开WebView
                self.root.after(1000, self.open_webview)
                break
            time.sleep(1)
            attempts += 1

    def open_webview(self):
        """打开WebView窗口"""
        if self.webview_window is None:
            try:
                self.webview_window = webview.create_window(
                    '信息源时序队列', 
                    'http://localhost:5000',
                    width=1200,
                    height=800,
                    resizable=True,
                    text_select=True
                )
                webview.start(debug=True)
            except Exception as e:
                messagebox.showerror("错误", f"打开WebView失败: {e}")

    def stop_service(self):
        if self.process is not None:
            self.process.terminate()
            self.process = None
            self.is_service_running = False
            
            # 关闭WebView窗口
            if self.webview_window:
                try:
                    webview.windows_clear()
                except:
                    pass
                self.webview_window = None
            
            # 更新UI状态
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.browser_button.config(state=tk.DISABLED)
            self.status_label.config(text="服务已停止", foreground="red")
            
            messagebox.showinfo("服务", "服务已停止！")

    def open_browser(self):
        """在默认浏览器中打开"""
        try:
            webbrowser.open('http://localhost:5000')
        except Exception as e:
            messagebox.showerror("错误", f"打开浏览器失败: {e}")

    def on_closing(self):
        if self.process is not None:
            self.process.terminate()
            self.process = None
        if self.webview_window:
            try:
                webview.windows_clear()
            except:
                pass
        self.root.destroy()

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            s.connect(('10.254.254.254', 1))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        return local_ip

    def copy_ip_to_clipboard(self, event):
        self.root.clipboard_clear()
        self.root.clipboard_append(f"http://{self.get_local_ip()}:5000")
        messagebox.showinfo("复制成功", "访问地址已复制到剪贴板！")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop() 