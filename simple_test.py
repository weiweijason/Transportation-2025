from app import create_app

print("開始測試...")
try:
    app = create_app(load_tdx=False)
    print("應用程序創建成功")
    
    with app.app_context():
        from flask import url_for
        print("測試 url_for...")
        url = url_for('community.friends')
        print(f"Success: {url}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
