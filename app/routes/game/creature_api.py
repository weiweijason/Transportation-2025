from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models.creature import Creature, ElementType
from app.routes.game.auth import jwt_or_session_required

# 修改藍圖前綴為 /game/api 以符合前端預期
creature_bp = Blueprint('game_creature', __name__, url_prefix='/game/api')

# 精靈捕捉 API
@creature_bp.route('/catch-creature', methods=['POST'])
@login_required
def catch_creature():
    data = request.json
    creature_id = data.get('creatureId')
    creature_name = data.get('creatureName')
    creature_type = data.get('creatureType')
    creature_rarity = data.get('creatureRarity')
    creature_power = data.get('creaturePower')
    creature_img = data.get('creatureImg')
    
    if not all([creature_id, creature_name, creature_type, creature_rarity, creature_power]):
        return jsonify({'success': False, 'message': '缺少必要資訊'}), 400
        
    # 創建新精靈
    new_creature = Creature(
        name=creature_name,
        type=creature_type,
        rarity=creature_rarity,
        power=creature_power,
        image_url=creature_img,
        level=1,
        experience=0,
        user_id=current_user.id
    )
    
    # 儲存到資料庫
    new_creature.save()
    
    # 回傳成功資訊
    return jsonify({
        'success': True,
        'message': f'成功捕捉到 {creature_name}!',
        'creature': {
            'id': new_creature.id,
            'name': new_creature.name,
            'type': new_creature.type,
            'rarity': new_creature.rarity,
            'power': new_creature.power,
            'imageUrl': new_creature.image_url,
            'level': new_creature.level,
            'experience': new_creature.experience
        }
    })

# 新增：互動捕捉 API
@creature_bp.route('/capture-interactive', methods=['POST'])
@login_required
def capture_interactive_api():
    """精靈互動捕捉 API"""
    try:
        # 記錄請求開始
        current_app.logger.info(f"接收到捕捉請求，用戶ID: {current_user.id}")
        
        data = request.json
        creature_id = data.get('creatureId')
        
        # 記錄請求參數
        current_app.logger.info(f"捕捉請求參數: 精靈ID={creature_id}")
        
        if not creature_id:
            return jsonify({
                'success': False,
                'message': '缺少精靈ID'
            }), 400
        
        # 獲取 Firebase 服務
        from app.services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        # 檢查精靈是否存在
        try:
            creature_ref = firebase_service.firestore_db.collection('route_creatures').document(creature_id)
            creature_doc = creature_ref.get()
            
            if not creature_doc.exists:
                return jsonify({
                    'success': False,
                    'message': '找不到指定精靈，可能已被移除或過期'
                }), 404
                
            current_app.logger.info(f"找到精靈: {creature_id}")
        except Exception as creature_error:
            current_app.logger.error(f"檢查精靈時發生錯誤: {creature_error}")
            return jsonify({
                'success': False,
                'message': f'檢查精靈時發生錯誤: {str(creature_error)}'
            }), 500
        
        # 檢查用戶 player_id
        try:
            user_data = firebase_service.get_user_info(current_user.id)
            
            player_id = None
            if user_data and 'player_id' in user_data:
                player_id = user_data.get('player_id')
                current_app.logger.info(f"用戶 {current_user.id} 的 player_id: {player_id}")
            
            # 如果用戶沒有 player_id，生成一個並更新用戶資料
            if not player_id:
                import string
                import random
                player_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                
                # 更新用戶資料
                update_result = firebase_service.update_user_info(current_user.id, {'player_id': player_id})
                current_app.logger.info(f"已為用戶 {current_user.id} 生成新的 player_id: {player_id}, 更新結果: {update_result}")
            
            # 使用子集合檢查是否已經捕捉過該精靈
            try:
                # 檢查 captured_players 子集合中是否已包含此玩家
                player_capture_ref = creature_ref.collection('captured_players').document(player_id)
                player_capture_doc = player_capture_ref.get()
                
                if player_capture_doc.exists:
                    current_app.logger.info(f"用戶 {player_id} 已經捕捉過精靈 {creature_id}")
                    return jsonify({
                        'success': False,
                        'message': '你已經捕捉過這隻精靈了'
                    }), 409  # 衝突狀態碼
            except Exception as check_error:
                current_app.logger.error(f"檢查玩家捕捉狀態失敗: {check_error}")
                import traceback
                current_app.logger.error(f"檢查玩家捕捉狀態失敗詳情: {traceback.format_exc()}")
                # 即使檢查失敗，也讓捕捉繼續進行，假設用戶尚未捕捉
                current_app.logger.info(f"忽略檢查錯誤，繼續捕捉流程")
                
        except Exception as user_error:
            current_app.logger.error(f"檢查用戶時發生錯誤: {user_error}")
            return jsonify({
                'success': False,
                'message': f'檢查用戶資料時發生錯誤: {str(user_error)}'
            }), 500
        
        # 使用 Firebase 服務捕捉精靈
        try:
            current_app.logger.info(f"開始捕捉精靈，精靈ID: {creature_id}, 用戶ID: {current_user.id}")
            result = firebase_service.catch_route_creature(
                creature_id=creature_id,
                user_id=current_user.id
            )
            
            current_app.logger.info(f"捕捉結果: {result}")
              # 處理結果中的 Sentinel 對象 (Firebase 伺服器時間戳記)
            # 如果結果中包含精靈資料且有 captured_at 字段是 Sentinel 對象
            if result.get('success') and 'creature' in result:
                creature_data = result['creature']
                if 'captured_at' in creature_data:
                    # 檢查是否為 Sentinel 對象 (無法 JSON 序列化)
                    if hasattr(creature_data['captured_at'], '__class__') and 'Sentinel' in creature_data['captured_at'].__class__.__name__:
                        # 將 Sentinel 替換為當前時間的字符串表示
                        from datetime import datetime
                        creature_data['captured_at'] = datetime.now().isoformat()
                
                # 觸發成就檢查 - 精靈捕捉相關成就
                try:
                    current_app.logger.info(f"觸發精靈捕捉成就檢查，用戶ID: {current_user.id}")
                    triggered_achievements = firebase_service.trigger_achievement_check(
                        current_user.id, 
                        'creature_captured',
                        {
                            'creature_id': creature_id,
                            'element_type': creature_data.get('element_type', 'normal'),
                            'rarity': creature_data.get('rarity', 1)
                        }
                    )
                    
                    # 將新獲得的成就添加到回應中
                    if triggered_achievements:
                        result['new_achievements'] = triggered_achievements
                        current_app.logger.info(f"用戶獲得新成就: {[ach.get('achievement_name', ach.get('achievement_id')) for ach in triggered_achievements]}")
                        
                except Exception as achievement_error:
                    current_app.logger.error(f"觸發成就檢查失敗: {achievement_error}")
                    # 不影響捕捉結果，僅記錄錯誤
            
            return jsonify(result)
        except Exception as catch_error:
            current_app.logger.error(f"捕捉精靈時發生錯誤: {catch_error}")
            # 詳細記錄異常
            import traceback
            error_details = traceback.format_exc()
            current_app.logger.error(f"捕捉精靈詳細錯誤: \n{error_details}")
            
            return jsonify({
                'success': False,
                'message': f'捕捉精靈時發生錯誤: {str(catch_error)}'
            }), 500
            
    except Exception as e:
        # 詳細記錄異常
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error(f"捕捉精靈時發生異常: {str(e)}\n{error_details}")
        
        # 返回用戶友好的錯誤訊息
        return jsonify({
            'success': False,
            'message': f'捕捉精靈時發生錯誤: {str(e)}'
        }), 500