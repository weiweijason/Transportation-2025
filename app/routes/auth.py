from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.services.firebase_service import FirebaseService, FirebaseUser
import time  # 新增這個導入，用於記錄登入時間戳
import random  # 新增這個導入，用於隨機選擇初始精靈

# 創建認證藍圖
auth = Blueprint('auth', __name__, url_prefix='/auth')

# 實例化Firebase服務
firebase_service = FirebaseService()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """處理用戶登入"""
    # 如果用戶已登入，重定向到主頁
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # 處理POST請求（用戶提交登入表單）
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
          # 驗證表單數據
        if not email or not password:
            flash('請填寫完整的登入資訊', 'danger')
            return render_template('auth/login.html')
        
        # 嘗試登入
        result = firebase_service.login_user(email, password)
        
        if result['status'] == 'success':
            # 登入成功，儲存用戶信息到會話
            flask_user = result['flask_user']
            
            # 使用 Flask-Login 登入用戶
            login_success = login_user(flask_user, remember=True)
            
            if login_success:
                # 登入成功
                session.permanent = True  # 確保會話是永久的
                session['user'] = {
                    'uid': result['user']['localId'],
                    'email': email,
                    'username': result['user_data'].get('username', 'User'),
                    'token': result['user']['idToken'],
                    'last_login': int(time.time())  # 添加登錄時間戳
                }
                
                # 保存會話
                session.modified = True
                
                print(f"成功登入用戶 {email} (ID: {flask_user.id})")
                flash('登入成功！', 'success')
                
                # 檢查是否有下一頁參數
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('main.index'))
            else:
                # Flask-Login登入失敗
                flash('登入過程中發生錯誤，請稍後再試', 'danger')
        else:
            # 登入失敗
            flash(result['message'], 'danger')
    
    return render_template('auth/login.html')

@auth.route('/login-for-setup', methods=['GET', 'POST'])
def login_for_setup():
    """處理新註冊用戶的登入，登入後引導至頭像設定頁面"""
    # 如果用戶已登入，重定向到頭像設定頁面
    if current_user.is_authenticated:
        # 將用戶信息存入會話，以便頭像設定頁面使用
        user_data = firebase_service.get_user_info(current_user.id)
        if user_data:
            session['new_user_info'] = {
                'uid': current_user.id,
                'email': user_data.get('email', ''),
                'username': user_data.get('username', 'User'),
                'player_id': user_data.get('player_id', '')
            }
            session.modified = True
        return redirect(url_for('auth.user_setup'))
    
    # 處理POST請求（用戶提交登入表單）
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
          # 驗證表單數據
        if not email or not password:
            flash('請填寫完整的登入資訊', 'danger')
            return render_template('auth/login_for_setup.html')
        
        # 嘗試登入
        result = firebase_service.login_user(email, password)
        
        if result['status'] == 'success':
            # 登入成功，儲存用戶信息到會話
            flask_user = result['flask_user']
            
            # 使用 Flask-Login 登入用戶
            login_success = login_user(flask_user, remember=True)
            
            if login_success:
                # 登入成功
                session.permanent = True  # 確保會話是永久的
                session['user'] = {
                    'uid': result['user']['localId'],
                    'email': email,
                    'username': result['user_data'].get('username', 'User'),
                    'token': result['user']['idToken'],
                    'last_login': int(time.time())  # 添加登錄時間戳
                }
                
                # 為頭像設定頁面準備用戶信息
                session['new_user_info'] = {
                    'uid': result['user']['localId'],
                    'email': email,
                    'username': result['user_data'].get('username', 'User'),
                    'player_id': result['user_data'].get('player_id', '')
                }
                
                # 保存會話
                session.modified = True
                
                print(f"成功登入用戶 {email} (ID: {flask_user.id})")
                flash('登入成功！請設定您的頭像', 'success')
                
                # 引導至頭像設定頁面
                return redirect(url_for('auth.user_setup'))
            else:
                # Flask-Login登入失敗
                flash('登入過程中發生錯誤，請稍後再試', 'danger')
        else:
            # 登入失敗
            flash(result['message'], 'danger')
    
    return render_template('auth/login_for_setup.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """處理用戶註冊"""
    # 如果用戶已登入，重定向到主頁
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # 處理POST請求（用戶提交註冊表單）
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 驗證表單數據
        if not username or not email or not password:
            flash('請填寫完整的註冊資訊', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('兩次輸入的密碼不一致', 'danger')
            return render_template('auth/register.html')
        
        # 嘗試註冊
        result = firebase_service.register_user(email, password, username)
        
        if result['status'] == 'success':
            # 註冊成功，儲存用戶資訊到會話中，以供初始化設定使用
            user = result.get('user', {})
            player_id = result.get('player_id', '未生成ID')
            user_id = user.get('localId', '')  # 確保從結果中獲取正確的user_id
            print(f"註冊成功: 用戶ID={user_id}, 玩家ID={player_id}, 用戶名={username}")
            
            # 儲存必要信息到會話，供初始化頁面使用
            session['new_user_info'] = {
                'uid': user_id,
                'email': email,
                'username': username,
                'player_id': player_id
            }
            session.modified = True
            
            # 提示用戶並重定向到專門的登入頁面
            flash('註冊成功！請登入以設定您的個人資料', 'success')
            return redirect(url_for('auth.login_for_setup'))
        else:
            # 註冊失敗
            flash(result['message'], 'danger')
    
    return render_template('auth/register.html')

@auth.route('/user-setup', methods=['GET', 'POST'])
def user_setup():
    """處理新用戶初始化設定"""
    # 檢查是否有新用戶信息在會話中，或者用戶已登入
    if 'new_user_info' not in session and not current_user.is_authenticated:
        flash('請先完成註冊流程並登入', 'warning')
        return redirect(url_for('auth.register'))
    
    # 如果用戶已登入，但會話中沒有新用戶信息，則從當前用戶獲取信息
    if current_user.is_authenticated and 'new_user_info' not in session:
        user_data = firebase_service.get_user_info(current_user.id)
        if user_data:
            session['new_user_info'] = {
                'uid': current_user.id,
                'email': user_data.get('email', ''),
                'username': user_data.get('username', 'User'),
                'player_id': user_data.get('player_id', '')
            }
            session.modified = True
    
    new_user_info = session.get('new_user_info')
    print(f"用戶設置頁面: 用戶ID={new_user_info.get('uid')}, 用戶名={new_user_info.get('username')}")
    
    if request.method == 'POST':
        # 處理用戶提交的初始化設定
        avatar_id = request.form.get('avatar_id')
        print(f"用戶選擇的頭像ID: {avatar_id}")
        
        # 確認用戶ID是否存在
        user_id = new_user_info.get('uid')
        if not user_id:
            print("錯誤: 會話中的用戶ID為空")
            flash('用戶ID無效，請重新註冊', 'danger')
            return redirect(url_for('auth.register'))
          # 更新用戶資料到 Firebase
        try:
            print(f"嘗試更新用戶 {user_id} 的頭像為 {avatar_id}")            # 將 avatar_id 映射到較短的圖片 URL (避免長 URL 可能導致的問題)
            avatar_images = {
                "1": "avatar_url_1",  # 使用較短的鍵名
                "2": "avatar_url_2",
                "3": "avatar_url_3",
                "4": "avatar_url_4",
                "5": "avatar_url_5",
                "6": "avatar_url_6",
                "7": "avatar_url_7",
                "8": "avatar_url_8",
                "9": "avatar_url_9",
                "10": "avatar_url_10"
            }
            
            # 映射回實際的 URL
            url_mapping = {
                "avatar_url_1": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c769d000e8e2515f6/view?project=681c5c6b002355634f3c&mode=admin",
                "avatar_url_2": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76a2002589aa244a/view?project=681c5c6b002355634f3c&mode=admin",
                "avatar_url_3": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76aa0030f3d8e5f1/view?project=681c5c6b002355634f3c&mode=admin",
                "avatar_url_4": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76af001cac084ee3/view?project=681c5c6b002355634f3c&mode=admin",
                "avatar_url_5": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76b8000b6f6ff334/view?project=681c5c6b002355634f3c&mode=admin",
                "avatar_url_6": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76bc00200e74dfaa/view?project=681c5c6b002355634f3c&mode=admin",
                "avatar_url_7": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76c100023ff731b5/view?project=681c5c6b002355634f3c&mode=admin",
                "avatar_url_8": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76c60019ba53529d/view?project=681c5c6b002355634f3c&mode=admin",
                "avatar_url_9": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76cb0027c008c539/view?project=681c5c6b002355634f3c&mode=admin",
                "avatar_url_10": "https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/681c76d000263718b58e/view?project=681c5c6b002355634f3c&mode=admin"
            }
              
            # 取得對應的短鍵名，如果沒有對應則保持預設
            avatar_key = avatar_images.get(avatar_id, "default.png")
            
            # 取得實際的 URL
            avatar_url = url_mapping.get(avatar_key, avatar_key)
            
            print(f"映射頭像ID {avatar_id} 到鍵名 {avatar_key}")
            print(f"實際存儲 URL: {avatar_url}")
            print(f"URL 長度: {len(avatar_url)}")
            
            # 直接設置完整的更新數據
            update_data = {
                'avatar_id': avatar_id,
                'avatar': avatar_url  # 更新實際的頭像 URL
            }
            
            print(f"更新數據: {update_data}")
            
            # 更新用戶頭像 (同時更新 avatar_id 和 avatar 欄位)
            update_result = firebase_service.update_user_profile(
                user_id=user_id,
                data=update_data
            )
            
            print(f"更新結果: {update_result}")
            
            if update_result['status'] == 'success':
                # 清除會話中的臨時用戶資訊
                session.pop('new_user_info', None)
                
                # 提示用戶並重定向到新手導覽頁面
                flash('個人設定已完成！開始您的冒險之旅吧！', 'success')
                return redirect(url_for('auth.tutorial'))
            else:
                error_msg = update_result.get('message', '更新資料時發生錯誤，請重試')
                print(f"更新資料失敗: {error_msg}")
                flash(error_msg, 'danger')
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"更新用戶資料時發生異常: {e}\n{error_details}")
            flash(f'發生錯誤：{str(e)}', 'danger')
    
    # GET 請求，顯示初始化設定頁面
    return render_template('auth/user_setup.html', user_info=new_user_info)

@auth.route('/tutorial')
def tutorial():
    """新手導覽介紹頁面"""
    # 檢查是否有新用戶信息在會話中，或者用戶已登入
    if 'new_user_info' not in session and not current_user.is_authenticated:
        flash('請先完成註冊流程並登入', 'warning')
        return redirect(url_for('auth.register'))
      # 預定義道館資訊 - 這些道館將作為可能的基地道館
    gyms = [
        {
            'id': 'tutorial-gym-1',
            'name': '中正紀念堂基地',
            'lat': 25.03556,
            'lng': 121.51972,
            'description': '中正紀念堂基地道館，位於臺北市中正區，著名的歷史地標。',
            'level': 5
        },
        {
            'id': 'tutorial-gym-2',
            'name': '國立故宮博物院基地',
            'lat': 25.1021,
            'lng': 121.5482,
            'description': '國立故宮博物院基地道館，位於臺北市士林區，世界級文化殿堂。',
            'level': 5
        },
        {
            'id': 'tutorial-gym-3',
            'name': '台北車站基地',
            'lat': 25.047778,
            'lng': 121.517222,
            'description': '台北車站基地道館，位於臺北市中正區，重要的交通樞紐。',
            'level': 5
        },
        {
            'id': 'tutorial-gym-4',
            'name': '國父紀念館基地',
            'lat': 25.040000,
            'lng': 121.560000,
            'description': '國父紀念館基地道館，位於臺北市信義區，重要的紀念場所。',
            'level': 5
        },
        {
            'id': 'tutorial-gym-5',
            'name': '台北101基地',
            'lat': 25.033611,
            'lng': 121.564444,
            'description': '台北101基地道館，位於臺北市信義區，台北市的摩天地標。',
            'level': 5
        }
    ]
      # 固定初始精靈為蒙昧(Obnuxis) - 所有玩家都使用相同的初始精靈
    creature_id = f"tutorial_obnuxis_{int(time.time())}_{random.randint(1000, 9999)}"
    
    default_creature = {
        'id': creature_id,
        'name': '蒙昧',
        'en_name': 'Obnuxis',
        'type': '暗系',
        'element_type': 'dark',
        'element_color': '#8e44ad',  # 暗系紫色
        'image': 'https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/68390f3c001270e4def2/view?project=681c5c6b002355634f3c&mode=admin',
        'lat': 25.03556 + (random.random() - 0.5) * 0.01,  # 隨機在中正紀念堂附近
        'lng': 121.51972 + (random.random() - 0.5) * 0.01,
        'power': random.randint(500, 550),  # ATK範圍：500-550
        'hp': random.randint(2700, 2800),   # HP範圍：2700-2800
        'attack': random.randint(500, 550), # ATK範圍：500-550
        'defense': random.randint(200, 250), # 適當的防禦值
        'species': '蒙昧',
        'rarity': 'SSR'
    }
    
    # 在 Firebase 中創建這隻精靈，但將其標記為教學精靈
    try:
        if current_user.is_authenticated:
            firebase_service.save_tutorial_creature(current_user.id, default_creature)
    except Exception as e:
        print(f"保存教學精靈時出錯: {e}")
    
    # 確定要傳遞給模板的用戶信息
    user_info = None
    if 'new_user_info' in session:
        user_info = session.get('new_user_info')
    elif current_user.is_authenticated:
        user_info = {
            'uid': current_user.id,
            'email': current_user.email,
            'username': current_user.username,
            'player_id': getattr(current_user, 'player_id', None)
        }
    
    return render_template('auth/tutorial.html', 
                           gyms=gyms, 
                           default_creature=default_creature,
                           user_info=user_info)

@auth.route('/logout')
@login_required
def logout():
    """處理用戶登出"""
    # 使用 Flask-Login 登出用戶
    logout_user()
    
    # 清除會話中的用戶信息
    session.pop('user', None)
    
    flash('您已成功登出', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/get-custom-token', methods=['GET'])
@login_required
def get_custom_token():
    """獲取 Firebase 自定義認證令牌
    
    此端點為前端提供一個自定義令牌，用於在前端自動登入到 Firebase
    """
    try:
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': '用戶未登入'
            }), 401
        
        # 獲取當前用戶的 Firebase UID
        user_id = current_user.id
        
        # 使用 Firebase Admin SDK 生成自定義令牌
        from firebase_admin import auth as firebase_admin_auth
        custom_token = firebase_admin_auth.create_custom_token(user_id)
        
        return jsonify({
            'success': True,
            'token': custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"生成自定義令牌失敗: {e}\n{error_details}")
        
        return jsonify({
            'success': False,
            'message': f'生成令牌失敗: {str(e)}'
        }), 500

@auth.route('/tutorial/capture-creature/<creature_id>', methods=['POST'])
def tutorial_capture_creature(creature_id):
    """處理教學模式中的精靈捕捉"""
    if not current_user.is_authenticated:
        return jsonify({
            'success': False,
            'message': '請先登入'
        }), 401
    
    print(f"收到捕捉請求，精靈 ID: {creature_id}")
    
    try:
        # 捕捉精靈
        result = firebase_service.capture_tutorial_creature(current_user.id, creature_id)
        
        if result['status'] == 'success':
            return jsonify({
                'success': True,
                'message': '捕捉成功！',
                'creature': result.get('creature', {}),
                'already_captured': result.get('already_captured', False)
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            })
    except Exception as e:
        print(f"捕捉教學精靈時出錯: {e}")
        return jsonify({
            'success': False,
            'message': f'捕捉失敗: {str(e)}'
        })

@auth.route('/tutorial/set-base-gym', methods=['POST'])
def tutorial_set_base_gym():
    """設定使用者的基地道館"""
    print(f">>> DEBUG: 收到基地道館設定請求")
    print(f">>> DEBUG: 用戶認證狀態: {current_user.is_authenticated}")
    print(f">>> DEBUG: 會話數據: {session}")    # 檢查是否是新手導覽模式或已登入用戶
    is_tutorial_mode = (session.get('tutorial_mode') or 
                       session.get('new_user_info') or 
                       request.headers.get('X-Tutorial-Mode') == 'true')
    
    if not current_user.is_authenticated and not is_tutorial_mode:
        print(f">>> DEBUG: 用戶未認證且非新手導覽模式")
        return jsonify({
            'success': False,
            'message': '請先登入'
        }), 401
    
    try:
        # 獲取前端傳來的道館資料
        gym_data = request.json
        print(f">>> DEBUG: 收到的道館資料: {gym_data}")
          # 取得用戶ID（從已登入用戶或新手導覽會話）
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id
            print(f">>> DEBUG: 使用已登入用戶ID: {user_id}")
        elif session.get('new_user_info'):
            user_id = session.get('new_user_info').get('uid')
            print(f">>> DEBUG: 使用新手導覽用戶ID: {user_id}")
        elif request.headers.get('X-Tutorial-User-ID'):
            user_id = request.headers.get('X-Tutorial-User-ID')
            print(f">>> DEBUG: 使用標頭中的新手導覽用戶ID: {user_id}")
        
        if not user_id:
            print(f">>> DEBUG: 無法取得用戶ID")
            return jsonify({
                'success': False,
                'message': '無法取得用戶信息'
            }), 400
        
        print(f">>> DEBUG: 當前用戶ID: {user_id}")
        
        if not gym_data:
            print(f">>> DEBUG: 道館資料為空")
            return jsonify({
                'success': False,
                'message': '無效的道館資料'
            })
        
        # 儲存基地道館
        print(f">>> DEBUG: 開始呼叫 Firebase Service")
        result = firebase_service.save_user_base_gym(user_id, gym_data)
        print(f">>> DEBUG: Firebase Service 回應: {result}")
        
        if result['status'] == 'success':
            print(f">>> DEBUG: 基地道館設定成功")
            return jsonify({
                'success': True,
                'message': '成功設定基地道館'
            })
        else:
            print(f">>> DEBUG: 基地道館設定失敗: {result['message']}")
            return jsonify({
                'success': False,
                'message': result['message']
            })
            
    except Exception as e:
        print(f">>> DEBUG: 設定基地道館時出錯: {e}")
        import traceback
        print(f">>> DEBUG: 錯誤堆疊: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'設定基地道館失敗: {str(e)}'
        })

@auth.route('/tutorial/interactive-capture/<creature_id>')
def tutorial_interactive_capture(creature_id):
    """處理教學模式中的互動式精靈捕捉頁面"""
    # 檢查用戶是否已登入
    if not current_user.is_authenticated:
        flash('請先登入', 'warning')
        return redirect(url_for('auth.login'))
      # 在教學模式中使用固定的蒙昧精靈
    creature = {
        'id': creature_id,
        'name': '蒙昧',
        'en_name': 'Obnuxis',
        'type': '暗系',
        'element_type': 'dark',
        'power': random.randint(500, 550),  # ATK範圍：500-550
        'hp': random.randint(2700, 2800),   # HP範圍：2700-2800
        'attack': random.randint(500, 550), # ATK範圍：500-550
        'rarity': 'SSR',
        'image': 'https://fra.cloud.appwrite.io/v1/storage/buckets/681c5c8d00308c6d7719/files/68390f3c001270e4def2/view?project=681c5c6b002355634f3c&mode=admin',
    }
    
    return render_template('auth/tutorial_capture.html', creature=creature)