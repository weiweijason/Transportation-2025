from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session
from flask_login import login_required, current_user
from app.config.firebase_config import FIREBASE_CONFIG
import firebase_admin
from firebase_admin import firestore

# 創建 bylin 藍圖
bylin = Blueprint('bylin', __name__, url_prefix='/bylin')

@bylin.route('/myelf')
@login_required
def myelf():
    """我的精靈頁面"""
    return render_template('bylin/myelf.html', firebase_config=FIREBASE_CONFIG)

@bylin.route('/myarena')
@login_required
def myarena():
    """我的擂台頁面"""
    return render_template('bylin/myarena.html', firebase_config=FIREBASE_CONFIG)

@bylin.route('/backpack')
@login_required
def backpack():
    """我的背包頁面"""
    return render_template('bylin/mybag.html', firebase_config=FIREBASE_CONFIG)

@bylin.route('/api/backpack', methods=['GET'])
@login_required
def get_backpack():
    """獲取使用者背包資料的API"""
    try:
        # 獲取使用者ID
        user_id = session.get('user', {}).get('uid')
        if not user_id:
            return jsonify({'success': False, 'message': '使用者未登入'})
        
        # 初始化 Firestore 客戶端
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = firestore.client()
        
        # 獲取使用者背包子集合
        backpack_ref = db.collection('users').document(user_id).collection('user_backpack')
        backpack_docs = backpack_ref.get()
        
        # 組織背包資料
        backpack_data = {
            'magic-circle': {},
            'potion': {}
        }
        
        for doc in backpack_docs:
            item_id = doc.id
            item_data = doc.to_dict()
            count = item_data.get('count', 0)
            
            # 根據道具類型分類
            if item_id in ['normal', 'advanced', 'premium']:
                backpack_data['magic-circle'][item_id] = count
            elif item_id in ['normal_drink', 'advanced_drink', 'premium_drink']:
                # 移除 _drink 後綴以符合前端期望的格式
                key = item_id.replace('_drink', '')
                backpack_data['potion'][key] = count
        
        return jsonify({
            'success': True,
            'backpack': backpack_data
        })
        
    except Exception as e:
        print(f"獲取背包資料錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'獲取背包資料失敗: {str(e)}'
        })

@bylin.route('/use-item', methods=['POST'])
@login_required
def use_item():
    """使用道具的API"""
    try:
        data = request.get_json()
        item_type = data.get('type')
        item_key = data.get('key')
        
        if not item_type or not item_key:
            return jsonify({'success': False, 'message': '缺少必要參數'})
        
        # 獲取使用者ID
        user_id = session.get('user', {}).get('uid')
        if not user_id:
            return jsonify({'success': False, 'message': '使用者未登入'})
        
        # 初始化 Firestore 客戶端
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = firestore.client()
        
        # 轉換道具鍵名以符合 Firebase 格式
        firebase_key = item_key
        if item_type == 'potion':
            firebase_key = f"{item_key}_drink"
        
        # 獲取當前道具數量
        item_ref = db.collection('users').document(user_id).collection('user_backpack').document(firebase_key)
        item_doc = item_ref.get()
        
        if not item_doc.exists:
            return jsonify({'success': False, 'message': '道具不存在'})
        
        current_count = item_doc.to_dict().get('count', 0)
        
        if current_count <= 0:
            return jsonify({'success': False, 'message': '道具數量不足'})
        
        # 減少道具數量
        new_count = current_count - 1
        item_ref.update({'count': new_count})
        
        return jsonify({
            'success': True,
            'message': '道具使用成功',
            'new_count': new_count
        })
        
    except Exception as e:
        print(f"使用道具錯誤: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'使用道具時發生錯誤: {str(e)}'
        })

@bylin.route('/magic-circle-details')
@login_required
def magic_circle_details():
    """魔法陣詳情頁面"""
    return render_template('bylin/magic_circle_details.html', firebase_config=FIREBASE_CONFIG)

@bylin.route('/potion-details')
@login_required
def potion_details():
    """藥水詳情頁面"""
    return render_template('bylin/potion_details.html', firebase_config=FIREBASE_CONFIG)
