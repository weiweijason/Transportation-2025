#!/usr/bin/env python3
"""
修復 arena-manager.js 語法錯誤
"""

def fix_arena_manager_js():
    file_path = "app/static/js/modules/arena-manager.js"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        print(f"檢查 {file_path}...")
        print(f"總行數: {len(lines)}")
        
        # 檢查括號匹配
        open_braces = 0
        open_parens = 0
        
        for i, line in enumerate(lines, 1):
            open_braces += line.count('{')
            open_braces -= line.count('}')
            open_parens += line.count('(')
            open_parens -= line.count(')')
            
            # 如果在某一行出現不匹配，記錄
            if i > 460:  # 接近問題區域
                print(f"行 {i}: 大括號平衡: {open_braces}, 圓括號平衡: {open_parens}")
                print(f"    內容: {line.strip()}")
        
        print(f"\n最終檢查:")
        print(f"大括號平衡: {open_braces}")
        print(f"圓括號平衡: {open_parens}")
        
        # 如果大括號不平衡，在文件末尾添加缺失的括號
        if open_braces > 0:
            print(f"需要添加 {open_braces} 個閉括號")
            content += '\n' + '}' * open_braces
            
            # 寫回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ 已修復括號不匹配問題")
            return True
        else:
            print("✅ 括號匹配正確")
            return True
            
    except Exception as e:
        print(f"❌ 修復失敗: {e}")
        return False

if __name__ == "__main__":
    fix_arena_manager_js()
