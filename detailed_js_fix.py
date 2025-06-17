#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細的 JavaScript 語法修復工具
"""

print("🔧 詳細 JavaScript 語法檢查和修復")
print("=" * 50)

# 讀取檔案
file_path = r"c:\Users\User\OneDrive - National ChengChi University\113-2 commucation\code\proj\app\templates\game\map.html"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 分析 JavaScript 代碼部分
in_script = False
js_lines = []
js_line_numbers = []
brace_stack = []
paren_stack = []

for i, line in enumerate(lines):
    if '<script>' in line and 'src=' not in line:
        in_script = True
        print(f"📄 開始 JavaScript 區塊於第 {i+1} 行")
        continue
    elif '</script>' in line:
        in_script = False
        print(f"📄 結束 JavaScript 區塊於第 {i+1} 行")
        continue
    
    if in_script:
        js_lines.append(line)
        js_line_numbers.append(i+1)

print(f"\n📊 分析 {len(js_lines)} 行 JavaScript 代碼")

# 詳細分析每一行
problems = []
for idx, (line_num, line) in enumerate(zip(js_line_numbers, js_lines)):
    stripped = line.strip()
    if not stripped or stripped.startswith('//'):
        continue
    
    # 計算括號
    open_braces = line.count('{')
    close_braces = line.count('}')
    open_parens = line.count('(')
    close_parens = line.count(')')
    
    # 檢查常見問題
    if '}; }' in line:
        problems.append((line_num, "多餘的大括號", line.strip()))
    
    if '};  }' in line:
        problems.append((line_num, "多餘的大括號（空格）", line.strip()))
    
    # 檢查不匹配的大括號
    net_braces = open_braces - close_braces
    if abs(net_braces) > 1 and not any(keyword in line for keyword in ['function', 'if', 'for', 'while', 'try', 'catch']):
        problems.append((line_num, f"可能的大括號不匹配 (差異: {net_braces})", line.strip()))

# 報告問題
if problems:
    print("\n❌ 發現的問題:")
    for line_num, problem, code in problems:
        print(f"  第 {line_num} 行: {problem}")
        print(f"    代碼: {code}")
        print()
    
    # 嘗試修復
    print("🔧 嘗試修復...")
    fixed_lines = lines.copy()
    
    for line_num, problem, code in problems:
        if "多餘的大括號" in problem:
            original_line = fixed_lines[line_num - 1]
            if '}; }' in original_line:
                fixed_lines[line_num - 1] = original_line.replace('}; }', '};')
                print(f"✅ 修復第 {line_num} 行: 移除多餘的大括號")
            elif '};  }' in original_line:
                fixed_lines[line_num - 1] = original_line.replace('};  }', '};')
                print(f"✅ 修復第 {line_num} 行: 移除多餘的大括號")
    
    # 寫回檔案
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("\n✅ 修復完成，檔案已更新")
else:
    print("\n✅ 沒有發現明顯的語法問題")

print("\n📋 建議測試:")
print("1. 重新整理瀏覽器頁面")
print("2. 檢查開發者工具控制台")
print("3. 確認地圖功能是否正常")
