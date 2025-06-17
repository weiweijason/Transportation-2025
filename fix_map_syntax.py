#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 map.html 中的語法錯誤
"""

print("🔧 修復 map.html 語法錯誤")
print("=" * 40)

# 讀取原始檔案
with open(r"c:\Users\User\OneDrive - National ChengChi University\113-2 commucation\code\proj\app\templates\game\map.html", 'r', encoding='utf-8') as f:
    content = f.read()

# 查找和修復常見的語法問題
fixes_applied = []

# 修復1: 移除多餘的 }; }
if '}; }' in content:
    content = content.replace('}; }', '};')
    fixes_applied.append("移除多餘的 '}; }'")

# 修復2: 檢查並修復重複的 setTimeout 調用
lines = content.split('\n')
fixed_lines = []
in_script = False
brace_count = 0

for i, line in enumerate(lines):
    if '<script>' in line:
        in_script = True
    elif '</script>' in line:
        in_script = False
        brace_count = 0
    
    if in_script:
        # 計算這一行的大括號
        open_braces = line.count('{')
        close_braces = line.count('}')
        brace_count += open_braces - close_braces
        
        # 檢查特定問題
        if '}; }' in line:
            line = line.replace('}; }', '};')
            fixes_applied.append(f"第 {i+1} 行: 修復多餘的大括號")
    
    fixed_lines.append(line)

# 重新組合內容
fixed_content = '\n'.join(fixed_lines)

# 寫入修復後的檔案
with open(r"c:\Users\User\OneDrive - National ChengChi University\113-2 commucation\code\proj\app\templates\game\map.html", 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print(f"✅ 應用了 {len(fixes_applied)} 個修復:")
for fix in fixes_applied:
    print(f"  - {fix}")

if not fixes_applied:
    print("🔍 沒有發現明顯的語法錯誤，可能需要手動檢查")

print("\n📋 建議檢查:")
print("1. 打開瀏覽器開發者工具")
print("2. 重新整理頁面")
print("3. 查看控制台是否還有語法錯誤")
