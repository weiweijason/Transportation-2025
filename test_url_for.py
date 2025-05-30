from app import create_app

app = create_app(load_tdx=False)
with app.app_context():
    print("=== Game related routes ===")
    for rule in app.url_map.iter_rules():
        if 'game' in rule.endpoint:
            print(f'{rule.rule} -> {rule.endpoint}')
    
    print("\n=== Testing url_for ===")
    from flask import url_for
    try:
        catch_url = url_for('game.catch')
        print(f'url_for("game.catch") = {catch_url}')
    except Exception as e:
        print(f'Error with game.catch: {e}')
    
    try:
        community_url = url_for('community.friends')
        print(f'url_for("community.friends") = {community_url}')
    except Exception as e:
        print(f'Error with community.friends: {e}')
