import os
import time
import logging
import requests
import platform
import threading
from flask import Flask, render_template

app = Flask(__name__)

file_url = 'ALL_SCRAPED_URLS.txt'

PORT = 8080
HOST='0.0.0.0'

def load_urls():
    try:
        with open(file_url, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        return urls
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {file_url}.")
        return []

@app.route('/')
def index():
    """Route chính để hiển thị trang web."""
    image_urls = load_urls()
    return render_template('index.html', urls=image_urls)
def clear_terminal():
    os.system('cls' if platform.system() == "Windows" else 'clear')
def get_ip():
    """Lấy IP công cộng, xử lý lỗi mạng."""
    url = "https://api.ipify.org"
    try:
        response = requests.get(url, timeout=5)
        # Nếu có lỗi 4xx/5xx, sẽ raise HTTPError
        response.raise_for_status() 
        return response.text.strip()
    
    except requests.exceptions.RequestException as e:
        # Bắt tất cả các lỗi liên quan đến requests (ConnectionError, Timeout, HTTPError, v.v.)
        print(f"Lỗi khi lấy IP: {e}")
        return None # Trả về None nếu không thành công

def run_flask_server():
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.run(host=HOST, port=PORT, debug=True, use_reloader=False)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_flask_server, daemon=True)
    server_thread.start()
    
    # Đợi một chút để server kịp khởi tạo (tránh lỗi đua tranh)
    time.sleep(1)
    
    # 2. Lấy IP
    public_ip = get_ip()
    
    # 3. XÓA TERMINAL và IN THÔNG BÁO TÙY CHỈNH
    #clear_terminal() 
    
    print('=' * 60)
    print(f"| 🎉 ỨNG DỤNG FLASK ĐANG CHẠY THÀNH CÔNG 🎉")
    print('=' * 60)
    print(f"| 🌐 Public IP (Thế giới): http://{public_ip}:{PORT}")
    print(f"| 🏠 Local Host (Cục bộ): http://127.0.0.1:{PORT}")
    print(f"| 🚦 Trạng thái: Đang lắng nghe trên cổng {PORT}")
    print('=' * 60)
    print("  (Nhấn Ctrl+C để dừng server)")
    
    # 4. Giữ luồng chính chạy
    # Luồng chính sẽ bị chặn ở đây, giữ cho luồng server (server_thread) hoạt động
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServer đã dừng.")
