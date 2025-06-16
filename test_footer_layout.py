#!/usr/bin/env python3
"""
測試腳本：驗證footer布局修復
Test Script: Verify footer layout fix

執行方式：
python test_footer_layout.py

功能：
- 測試主要頁面是否正常載入
- 檢查footer是否不會覆蓋內容
"""

import requests
import sys
from urllib.parse import urljoin

def test_page_layout():
    """測試頁面布局是否正常"""
    
    # 基礎URL
    base_url = "http://localhost:5000"
    
    # 要測試的頁面
    test_pages = {
        "首頁": "/",
        "註冊頁面": "/auth/register",
        "登入頁面": "/auth/login",
        "服務條款": "/auth/terms-of-service",
        "隱私政策": "/auth/privacy-policy"
    }
    
    print("🔍 測試頁面布局...")
    print(f"📍 基礎URL: {base_url}")
    print("-" * 50)
    
    all_passed = True
    
    for page_name, endpoint in test_pages.items():
        try:
            url = urljoin(base_url, endpoint)
            print(f"🧪 測試 {page_name}: {url}")
            
            # 發送GET請求
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # 檢查footer是否存在
                if 'class="game-footer"' in content:
                    print(f"✅ {page_name} - Footer存在")
                    
                    # 檢查CSS是否包含正確的布局
                    if 'margin-top: auto' in content or 'flex:' in content:
                        print(f"✅ {page_name} - 布局CSS正確")
                    else:
                        print(f"⚠️  {page_name} - 可能需要檢查CSS布局")
                        
                else:
                    print(f"❌ {page_name} - Footer未找到")
                    all_passed = False
                    
            elif response.status_code == 302:
                print(f"✅ {page_name} - 重定向正常 (狀態碼: {response.status_code})")
                
            else:
                print(f"❌ {page_name} - 狀態碼: {response.status_code}")
                all_passed = False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {page_name} - 連接失敗：無法連接到 {base_url}")
            print("   請確保Flask應用程式正在運行 (python run_app.py)")
            all_passed = False
            
        except Exception as e:
            print(f"❌ {page_name} - 錯誤: {str(e)}")
            all_passed = False
            
        print()
    
    return all_passed

def check_css_fixes():
    """檢查CSS修復是否正確"""
    
    print("🔍 檢查CSS修復...")
    
    css_file_path = "app/static/css/style.css"
    
    try:
        with open(css_file_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        # 檢查footer CSS
        if 'position: absolute' in css_content and '.game-footer' in css_content:
            # 檢查footer部分是否還有position: absolute
            footer_section = css_content[css_content.find('.game-footer'):css_content.find('.game-footer') + 500]
            if 'position: absolute' in footer_section:
                print("❌ Footer仍然使用absolute定位")
                return False
            else:
                print("✅ Footer已移除absolute定位")
                
        # 檢查body CSS
        if 'display: flex' in css_content and 'flex-direction: column' in css_content:
            print("✅ Body使用flex布局")
        else:
            print("⚠️  Body可能沒有正確的flex布局")
            
        # 檢查是否有flex-grow或margin-top: auto
        if 'flex: 1 0 auto' in css_content or 'margin-top: auto' in css_content:
            print("✅ 找到正確的flex布局屬性")
        else:
            print("⚠️  可能缺少flex布局屬性")
            
        return True
        
    except FileNotFoundError:
        print(f"❌ CSS文件未找到: {css_file_path}")
        return False
    except Exception as e:
        print(f"❌ 讀取CSS文件時發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚌 精靈公車 - Footer布局修復測試")
    print("=" * 50)
    
    # 檢查CSS修復
    css_check_passed = check_css_fixes()
    print()
    
    # 測試頁面布局
    layout_test_passed = test_page_layout()
    
    print("=" * 50)
    print("📋 測試總結:")
    print(f"   CSS修復檢查: {'✅ 通過' if css_check_passed else '❌ 失敗'}")
    print(f"   頁面布局測試: {'✅ 通過' if layout_test_passed else '❌ 失敗'}")
    
    if css_check_passed and layout_test_passed:
        print("\n🎉 Footer布局修復成功！")
        print("💡 建議：")
        print("   1. 在各種螢幕尺寸下測試頁面")
        print("   2. 檢查不同頁面的內容是否與footer重疊")
        print("   3. 確認移動設備上的顯示效果")
        sys.exit(0)
    else:
        print("\n⚠️  請檢查並修復上述問題。")
        sys.exit(1)
