#!/usr/bin/env python3
"""
CSV Parametric Comparator GUI Launcher

Khởi động ứng dụng GUI để so sánh file CSV
"""

import sys
import os

# Thêm current directory vào Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from csv_gui import main

    if __name__ == "__main__":
        print("🚀 Khởi động CSV Parametric Comparator GUI...")
        main()

except ImportError as e:
    print(f"❌ Lỗi import: {e}")
    print("Vui lòng đảm bảo các file cần thiết có trong cùng thư mục:")
    print("  - csv_gui.py")
    print("  - csv_processor.py")

except Exception as e:
    print(f"❌ Lỗi khởi động: {e}")
    import traceback

    traceback.print_exc()
