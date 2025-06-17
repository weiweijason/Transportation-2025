#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript 語法檢查工具
"""
import re

def extract_js_from_html(html_file):
    """從 HTML 檔案中提取 JavaScript 代碼"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到所有 <script> 標籤中的 JavaScript 代碼
    js_blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    
    js_code = ""
    for block in js_blocks:
        # 跳過僅包含 src 的腳本標籤
        if 'src=' not in block and block.strip():
            js_code += block + "\n"
    
    return js_code

def check_brackets(js_code):
    """檢查大括號是否匹配"""
    stack = []
    bracket_map = {'(': ')', '[': ']', '{': '}'}
    opening = set(bracket_map.keys())
    closing = set(bracket_map.values())
    
    for i, char in enumerate(js_code):
        if char in opening:
            stack.append((char, i))
        elif char in closing:
            if not stack:
                return f"第 {i} 位置: 多餘的閉合括號 '{char}'"
            last_opening, pos = stack.pop()
            if bracket_map[last_opening] != char:
                return f"第 {pos}-{i} 位置: 括號不匹配 '{last_opening}' 和 '{char}'"
    
    if stack:
        char, pos = stack[-1]
        return f"第 {pos} 位置: 未閉合的括號 '{char}'"
    
    return "括號匹配正確"

# 檢查 map.html
html_file = r"c:\Users\User\OneDrive - National ChengChi University\113-2 commucation\code\proj\app\templates\game\map.html"

print("🔍 JavaScript 語法檢查報告")
print("=" * 40)

try:
    js_code = extract_js_from_html(html_file)
    
    if js_code:
        print(f"📄 提取到 {len(js_code)} 字符的 JavaScript 代碼")
        
        # 檢查括號匹配
        bracket_result = check_brackets(js_code)
        print(f"🔧 括號檢查結果: {bracket_result}")
        
        # 檢查一些常見的語法問題
        lines = js_code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line:
                # 檢查常見問題
                if line.endswith('; }'):
                    print(f"⚠️  第 {i} 行: 可能的語法問題 - '{line}'")
                if '};  }' in line:
                    print(f"❌ 第 {i} 行: 多餘的大括號 - '{line}'")
                if line.count('{') != line.count('}') and not any(x in line for x in ['if', 'function', 'for', 'while']):
                    print(f"⚠️  第 {i} 行: 括號數量可能不匹配 - '{line}'")
        
        print("\n✅ 語法檢查完成")
    else:
        print("❌ 未找到 JavaScript 代碼")

except Exception as e:
    print(f"❌ 檢查失敗: {e}")
