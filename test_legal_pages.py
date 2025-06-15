#!/usr/bin/env python3
"""
測試腳本：驗證服務條款和隱私政策頁面
Test Script: Verify Terms of Service and Privacy Policy pages

執行方式：
python test_legal_pages.py

功能：
- 測試服務條款頁面是否可訪問
- 測試隱私政策頁面是否可訪問
- 驗證頁面在未登入狀態下可正常瀏覽
"""

import requests
import sys
from urllib.parse import urljoin

def test_legal_pages():
    """測試法律文件頁面的可訪問性"""
    
    # 基礎URL - 根據實際運行環境調整
    base_url = "http://localhost:5000"
    
    # 要測試的頁面
    test_pages = {
        "服務條款": "/auth/terms-of-service",
        "隱私政策": "/auth/privacy-policy"
    }
    
    print("🔍 開始測試法律文件頁面...")
    print(f"📍 基礎URL: {base_url}")
    print("-" * 50)
    
    all_passed = True
    
    for page_name, endpoint in test_pages.items():
        try:
            url = urljoin(base_url, endpoint)
            print(f"🧪 測試 {page_name}: {url}")
            
            # 發送GET請求
            response = requests.get(url, timeout=10)
            
            # 檢查狀態碼
            if response.status_code == 200:
                print(f"✅ {page_name} - 狀態碼: {response.status_code} (正常)")
                
                # 檢查頁面內容是否包含預期的關鍵字
                content = response.text
                if page_name == "服務條款":
                    if "服務條款" in content and "Terms of Service" in content:
                        print(f"✅ {page_name} - 內容檢查通過")
                    else:
                        print(f"❌ {page_name} - 內容檢查失敗：缺少預期關鍵字")
                        all_passed = False
                elif page_name == "隱私政策":
                    if "隱私政策" in content and "Privacy Policy" in content:
                        print(f"✅ {page_name} - 內容檢查通過")
                    else:
                        print(f"❌ {page_name} - 內容檢查失敗：缺少預期關鍵字")
                        all_passed = False
                        
            elif response.status_code == 302:
                print(f"⚠️  {page_name} - 狀態碼: {response.status_code} (重定向)")
                print(f"   可能被重定向到登入頁面，請檢查 app.py 中的 public_paths 設定")
                all_passed = False
                
            else:
                print(f"❌ {page_name} - 狀態碼: {response.status_code} (錯誤)")
                all_passed = False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {page_name} - 連接失敗：無法連接到 {base_url}")
            print("   請確保Flask應用程式正在運行 (python run_app.py)")
            all_passed = False
            
        except requests.exceptions.Timeout:
            print(f"❌ {page_name} - 請求超時")
            all_passed = False
            
        except Exception as e:
            print(f"❌ {page_name} - 未知錯誤: {str(e)}")
            all_passed = False
            
        print()
    
    print("-" * 50)
    if all_passed:
        print("🎉 所有測試通過！法律文件頁面運作正常。")
        return True
    else:
        print("⚠️  部分測試失敗，請檢查問題並修復。")
        return False

def test_registration_links():
    """測試註冊頁面的法律文件連結"""
    
    base_url = "http://localhost:5000"
    register_url = urljoin(base_url, "/auth/register")
    
    print("🔍 測試註冊頁面的法律文件連結...")
    
    try:
        response = requests.get(register_url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # 檢查是否包含法律文件連結
            terms_link = 'href="{{ url_for(\'auth.terms_of_service\')'
            privacy_link = 'href="{{ url_for(\'auth.privacy_policy\')'
            
            if "terms_of_service" in content and "privacy_policy" in content:
                print("✅ 註冊頁面包含法律文件連結")
                return True
            else:
                print("❌ 註冊頁面缺少法律文件連結")
                return False
                
        else:
            print(f"❌ 無法訪問註冊頁面，狀態碼: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 測試註冊頁面時發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚌 精靈公車 - 法律文件頁面測試")
    print("=" * 50)
    
    # 測試法律文件頁面
    legal_test_passed = test_legal_pages()
    
    # 測試註冊頁面連結
    registration_test_passed = test_registration_links()
    
    print("\n" + "=" * 50)
    print("📋 測試總結:")
    print(f"   法律文件頁面: {'✅ 通過' if legal_test_passed else '❌ 失敗'}")
    print(f"   註冊頁面連結: {'✅ 通過' if registration_test_passed else '❌ 失敗'}")
    
    if legal_test_passed and registration_test_passed:
        print("\n🎉 所有測試通過！系統運作正常。")
        sys.exit(0)
    else:
        print("\n⚠️  請修復上述問題後重新測試。")
        sys.exit(1)
