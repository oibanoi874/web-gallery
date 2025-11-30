import os
import time
import logging
import requests
import platform
import threading
from flask import Flask, render_template, request

# --- Cấu hình Ứng dụng ---
app = Flask(__name__)

file_url = 'ALL_SCRAPED_URLS.txt'
PORT = 8080
HOST = '0.0.0.0'

# --- 1. Hàm Hỗ trợ ---

def clear_terminal():
    """Xóa nội dung hiển thị trên terminal."""
    os.system('cls' if platform.system() == "Windows" else 'clear')

def get_public_ip():
    """
    Truy vấn API để lấy IP công cộng và trả về (return) địa chỉ IP dưới dạng chuỗi.
    Trả về 'UNKNOWN' nếu có lỗi.
    """
    url = "https://api.ipify.org"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() 
        return response.text.strip()
    
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy IP: {e}")
        return 'UNKNOWN' 

def load_urls():
    """Tải danh sách URL từ file."""
    try:
        with open(file_url, 'r') as f:
            # Chỉ lấy các dòng không trống
            urls = [line.strip() for line in f if line.strip()] 
        return urls
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {file_url}.")
        return []

# --- 2. Route Chính ---

@app.route('/')
def index():
    """Route chính để hiển thị trang web và in ra IP của người dùng."""
    
    # Lấy IP của người dùng truy cập (Ưu tiên X-Forwarded-For nếu qua proxy)
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # IN LOG TRUY CẬP RA TERMINAL
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[ACCESS LOG] {timestamp} | IP: {user_ip} | Truy cập Route: /")
    
    # Trả về nội dung trang web
    image_urls = load_urls()
    return render_template('index.html', urls=image_urls)

# --- 3. Hàm Chạy Server trong Luồng Riêng ---

def run_flask_server():
    """
    Hàm khởi động Flask server. Chạy trong luồng riêng để không chặn luồng chính
    và tắt Debug/Reloader để tránh lỗi 'signal only works in main thread'.
    """
    # Vô hiệu hóa logger mặc định của Werkzeug để terminal sạch sẽ
    log = logging.getLogger('werkzeug')
    log.disabled = True
    
    app.run(
        host=HOST, 
        port=PORT, 
        # Tắt Debug và Reloader khi dùng Threading
        debug=False, 
        use_reloader=False 
    ) 

# --- 4. Khối Main (Khởi chạy Đa luồng) ---

if __name__ == '__main__':
    
    # 1. Bắt đầu luồng Flask server
    server_thread = threading.Thread(target=run_flask_server, daemon=True)
    server_thread.start()
    
    # Đợi một chút để server kịp khởi tạo
    time.sleep(1)
    
    # 2. Lấy IP công cộng (trong luồng chính)
    public_ip = get_public_ip()
    
    # 3. XÓA TERMINAL và IN THÔNG BÁO TÙY CHỈNH
    clear_terminal() 
    
    print('=' * 60)
    print(f"| 🎉 ỨNG DỤNG FLASK ĐANG CHẠY THÀNH CÔNG 🎉")
    print('=' * 60)
    print(f"| 🌐 Public URL: http://{public_ip}:{PORT}")
    print(f"| 🏠 Local Host: http://127.0.0.1:{PORT}")
    print(f"| 🚦 Trạng thái: Đang lắng nghe trên cổng {PORT}")
    print('=' * 60)
    print("  (Nhấn Ctrl+C để dừng server)")
    
    # 4. Giữ luồng chính chạy
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServer đã dừng.")
