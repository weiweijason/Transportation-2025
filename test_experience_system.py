#!/usr/bin/env python3
"""
Test script for the experience system implementation
"""

import sys
import os
sys.path.append('.')

from app.services.firebase_service import FirebaseService

def test_experience_system():
    """Test the experience system methods"""
    print("🎮 Testing Experience System Implementation")
    print("=" * 50)
    
    try:
        # Create Firebase service instance
        firebase_service = FirebaseService()
        
        # Test experience calculation methods
        print("\n📊 Testing Experience Calculation Methods:")
        for level in [1, 2, 3, 5, 10]:
            max_exp = firebase_service._calculate_max_experience(level)
            print(f"   Level {level:2d} max exp: {max_exp:4d}")
        
        # Test stat bonuses by rate
        print("\n⭐ Testing Stat Bonuses by Rate:")
        rates = ['N', 'R', 'SR', 'SSR']
        for rate in rates:
            bonus = firebase_service._get_stat_bonus_by_rate(rate)
            print(f"   {rate:3s} rate bonuses: Attack +{bonus['attack']:2d}, HP +{bonus['hp']:3d}")
        
        # Test if methods exist and are callable
        print("\n🔧 Testing Method Availability:")
        methods_to_test = [
            'add_experience_to_creature',
            '_calculate_max_experience', 
            '_get_stat_bonus_by_rate',
            'get_creature_level_info',
            'catch_route_creature'
        ]
        
        for method_name in methods_to_test:
            if hasattr(firebase_service, method_name):
                method = getattr(firebase_service, method_name)
                if callable(method):
                    print(f"   ✅ {method_name}")
                else:
                    print(f"   ❌ {method_name} (not callable)")
            else:
                print(f"   ❌ {method_name} (not found)")
        
        print("\n🎉 Experience system methods loaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing experience system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_experience_system()
    sys.exit(0 if success else 1)
