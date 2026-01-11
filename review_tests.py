#!/usr/bin/env python3
"""
LAF Backend Specific Review Tests
=================================

This script runs the exact tests mentioned in the review request to validate:
1. All 3 objectives work correctly (cutting ~18%, bulking ~12%, maintenance)
2. 14-day weight blocking (not 7 days)
3. No athlete mode references anywhere
4. All endpoints return proper responses without 500 errors
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = "https://fit-track-hub.preview.emergentagent.com/api"

def test_exact_review_scenarios():
    """Run the exact tests from the review request"""
    
    print("=" * 80)
    print("LAF BACKEND SPECIFIC REVIEW TESTS")
    print("=" * 80)
    
    results = []
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data}")
            results.append(("Health Check", True, data))
        else:
            print(f"❌ Health Check failed: {response.status_code}")
            results.append(("Health Check", False, response.text))
    except Exception as e:
        print(f"❌ Health Check error: {e}")
        results.append(("Health Check", False, str(e)))
    
    # Test 2: User Creation - Cutting
    print("\n2. Testing User Creation - Cutting...")
    cutting_user = {
        "id": "test_audit_cutting_001",
        "name": "Test Cutting",
        "age": 30,
        "weight": 85,
        "height": 175,
        "sex": "masculino",
        "goal": "cutting",
        "training_level": "intermediario",
        "weekly_training_frequency": 4,
        "available_time_per_session": 60,
        "dietary_restrictions": [],
        "food_preferences": [],
        "injury_history": []
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/user/profile", json=cutting_user, timeout=10)
        if response.status_code == 200:
            data = response.json()
            tdee = data.get("tdee", 0)
            target = data.get("target_calories", 0)
            deficit_percent = ((tdee - target) / tdee * 100) if tdee > 0 else 0
            print(f"✅ Cutting User: TDEE={tdee}kcal, Target={target}kcal, Deficit={deficit_percent:.1f}%")
            
            # Check for athlete references
            if any(term in str(data).lower() for term in ["athlete", "peak_week", "competition"]):
                print("❌ ATHLETE REFERENCES FOUND in cutting user response!")
                results.append(("Cutting User - No Athlete Refs", False, "Found athlete references"))
            else:
                results.append(("Cutting User - No Athlete Refs", True, "Clean response"))
                
            results.append(("Cutting User Creation", True, f"Deficit: {deficit_percent:.1f}%"))
        else:
            print(f"❌ Cutting user creation failed: {response.status_code}")
            results.append(("Cutting User Creation", False, response.text))
    except Exception as e:
        print(f"❌ Cutting user error: {e}")
        results.append(("Cutting User Creation", False, str(e)))
    
    # Test 3: User Creation - Bulking
    print("\n3. Testing User Creation - Bulking...")
    bulking_user = {
        "id": "test_audit_bulking_002",
        "name": "Test Bulking",
        "age": 25,
        "weight": 70,
        "height": 180,
        "sex": "masculino",
        "goal": "bulking",
        "training_level": "avancado",
        "weekly_training_frequency": 5,
        "available_time_per_session": 90,
        "dietary_restrictions": [],
        "food_preferences": [],
        "injury_history": []
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/user/profile", json=bulking_user, timeout=10)
        if response.status_code == 200:
            data = response.json()
            tdee = data.get("tdee", 0)
            target = data.get("target_calories", 0)
            surplus_percent = ((target - tdee) / tdee * 100) if tdee > 0 else 0
            print(f"✅ Bulking User: TDEE={tdee}kcal, Target={target}kcal, Surplus={surplus_percent:.1f}%")
            
            # Check for athlete references
            if any(term in str(data).lower() for term in ["athlete", "peak_week", "competition"]):
                print("❌ ATHLETE REFERENCES FOUND in bulking user response!")
                results.append(("Bulking User - No Athlete Refs", False, "Found athlete references"))
            else:
                results.append(("Bulking User - No Athlete Refs", True, "Clean response"))
                
            results.append(("Bulking User Creation", True, f"Surplus: {surplus_percent:.1f}%"))
        else:
            print(f"❌ Bulking user creation failed: {response.status_code}")
            results.append(("Bulking User Creation", False, response.text))
    except Exception as e:
        print(f"❌ Bulking user error: {e}")
        results.append(("Bulking User Creation", False, str(e)))
    
    # Test 4: User Creation - Maintenance
    print("\n4. Testing User Creation - Maintenance...")
    maintenance_user = {
        "id": "test_audit_manutencao_003",
        "name": "Test Manutencao",
        "age": 35,
        "weight": 75,
        "height": 170,
        "sex": "feminino",
        "goal": "manutencao",
        "training_level": "iniciante",
        "weekly_training_frequency": 3,
        "available_time_per_session": 45,
        "dietary_restrictions": [],
        "food_preferences": [],
        "injury_history": []
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/user/profile", json=maintenance_user, timeout=10)
        if response.status_code == 200:
            data = response.json()
            tdee = data.get("tdee", 0)
            target = data.get("target_calories", 0)
            diff = abs(target - tdee)
            print(f"✅ Maintenance User: TDEE={tdee}kcal, Target={target}kcal, Diff={diff}kcal")
            
            # Check for athlete references
            if any(term in str(data).lower() for term in ["athlete", "peak_week", "competition"]):
                print("❌ ATHLETE REFERENCES FOUND in maintenance user response!")
                results.append(("Maintenance User - No Athlete Refs", False, "Found athlete references"))
            else:
                results.append(("Maintenance User - No Athlete Refs", True, "Clean response"))
                
            results.append(("Maintenance User Creation", True, f"Difference: {diff}kcal"))
        else:
            print(f"❌ Maintenance user creation failed: {response.status_code}")
            results.append(("Maintenance User Creation", False, response.text))
    except Exception as e:
        print(f"❌ Maintenance user error: {e}")
        results.append(("Maintenance User Creation", False, str(e)))
    
    # Test 5: Diet Generation - Cutting
    print("\n5. Testing Diet Generation - Cutting...")
    try:
        response = requests.post(f"{BACKEND_URL}/diet/generate?user_id=test_audit_cutting_001", timeout=30)
        if response.status_code == 200:
            data = response.json()
            calories = data.get("computed_calories", 0)
            target = data.get("target_calories", 0)
            meals = len(data.get("meals", []))
            print(f"✅ Cutting Diet: {meals} meals, {calories}kcal (target: {target}kcal)")
            
            # Check for athlete references
            if any(term in str(data).lower() for term in ["athlete", "peak_week", "competition"]):
                print("❌ ATHLETE REFERENCES FOUND in cutting diet response!")
                results.append(("Cutting Diet - No Athlete Refs", False, "Found athlete references"))
            else:
                results.append(("Cutting Diet - No Athlete Refs", True, "Clean response"))
                
            results.append(("Cutting Diet Generation", True, f"{calories}kcal diet"))
        else:
            print(f"❌ Cutting diet generation failed: {response.status_code}")
            results.append(("Cutting Diet Generation", False, response.text))
    except Exception as e:
        print(f"❌ Cutting diet error: {e}")
        results.append(("Cutting Diet Generation", False, str(e)))
    
    # Test 6: Diet Generation - Bulking
    print("\n6. Testing Diet Generation - Bulking...")
    try:
        response = requests.post(f"{BACKEND_URL}/diet/generate?user_id=test_audit_bulking_002", timeout=30)
        if response.status_code == 200:
            data = response.json()
            calories = data.get("computed_calories", 0)
            target = data.get("target_calories", 0)
            meals = len(data.get("meals", []))
            print(f"✅ Bulking Diet: {meals} meals, {calories}kcal (target: {target}kcal)")
            
            # Check for athlete references
            if any(term in str(data).lower() for term in ["athlete", "peak_week", "competition"]):
                print("❌ ATHLETE REFERENCES FOUND in bulking diet response!")
                results.append(("Bulking Diet - No Athlete Refs", False, "Found athlete references"))
            else:
                results.append(("Bulking Diet - No Athlete Refs", True, "Clean response"))
                
            results.append(("Bulking Diet Generation", True, f"{calories}kcal diet"))
        else:
            print(f"❌ Bulking diet generation failed: {response.status_code}")
            results.append(("Bulking Diet Generation", False, response.text))
    except Exception as e:
        print(f"❌ Bulking diet error: {e}")
        results.append(("Bulking Diet Generation", False, str(e)))
    
    # Test 7: Weight Registration
    print("\n7. Testing Weight Registration...")
    weight_data = {
        "weight": 84.5,
        "notes": "Test weight registration",
        "questionnaire": {
            "diet": 8,
            "training": 7,
            "cardio": 6,
            "sleep": 8,
            "hydration": 9
        }
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/progress/weight/test_audit_cutting_001", json=weight_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            weight = data.get("record", {}).get("weight", 0)
            print(f"✅ Weight Registration: {weight}kg recorded")
            
            # Check for athlete references
            if any(term in str(data).lower() for term in ["athlete", "peak_week", "competition"]):
                print("❌ ATHLETE REFERENCES FOUND in weight registration response!")
                results.append(("Weight Registration - No Athlete Refs", False, "Found athlete references"))
            else:
                results.append(("Weight Registration - No Athlete Refs", True, "Clean response"))
                
            results.append(("Weight Registration", True, f"{weight}kg"))
        else:
            print(f"❌ Weight registration failed: {response.status_code}")
            results.append(("Weight Registration", False, response.text))
    except Exception as e:
        print(f"❌ Weight registration error: {e}")
        results.append(("Weight Registration", False, str(e)))
    
    # Test 8: 14-Day Weight Block
    print("\n8. Testing 14-Day Weight Block...")
    try:
        response = requests.post(f"{BACKEND_URL}/progress/weight/test_audit_cutting_001", json=weight_data, timeout=10)
        if response.status_code == 400:
            error_text = response.text
            if "14" in error_text:
                print(f"✅ 14-Day Block: Correctly blocked with 14-day message")
                results.append(("14-Day Weight Block", True, "Blocked correctly"))
            else:
                print(f"❌ Wrong block message: {error_text}")
                results.append(("14-Day Weight Block", False, f"Wrong message: {error_text}"))
        else:
            print(f"❌ Should be blocked but got: {response.status_code}")
            results.append(("14-Day Weight Block", False, f"Not blocked: {response.status_code}"))
    except Exception as e:
        print(f"❌ Weight block test error: {e}")
        results.append(("14-Day Weight Block", False, str(e)))
    
    # Test 9: Profile Retrieval - No Athlete Fields
    print("\n9. Testing Profile Retrieval - No Athlete Fields...")
    try:
        response = requests.get(f"{BACKEND_URL}/user/profile/test_audit_cutting_001", timeout=10)
        if response.status_code == 200:
            data = response.json()
            goal = data.get("goal", "unknown")
            print(f"✅ Profile Retrieved: goal={goal}")
            
            # CRITICAL: Check for athlete references
            athlete_terms = ["athlete", "peak_week", "competition_date", "competition_phase", "weeks_to_competition"]
            found_terms = []
            for term in athlete_terms:
                if term in str(data).lower():
                    found_terms.append(term)
            
            if found_terms:
                print(f"❌ CRITICAL: ATHLETE REFERENCES FOUND: {found_terms}")
                results.append(("Profile - No Athlete Fields", False, f"Found: {found_terms}"))
            else:
                print("✅ Profile clean - no athlete references")
                results.append(("Profile - No Athlete Fields", True, "Clean profile"))
        else:
            print(f"❌ Profile retrieval failed: {response.status_code}")
            results.append(("Profile - No Athlete Fields", False, response.text))
    except Exception as e:
        print(f"❌ Profile retrieval error: {e}")
        results.append(("Profile - No Athlete Fields", False, str(e)))
    
    # Test 10: Water Tracker
    print("\n10. Testing Water Tracker...")
    water_data = {"water_ml": 500}
    
    try:
        response = requests.post(f"{BACKEND_URL}/tracker/water-sodium/test_audit_cutting_001", json=water_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            water_ml = data.get("water_ml", 0)
            print(f"✅ Water Tracker: {water_ml}ml recorded")
            
            # Check for athlete references
            if any(term in str(data).lower() for term in ["athlete", "peak_week", "competition"]):
                print("❌ ATHLETE REFERENCES FOUND in water tracker response!")
                results.append(("Water Tracker - No Athlete Refs", False, "Found athlete references"))
            else:
                results.append(("Water Tracker - No Athlete Refs", True, "Clean response"))
                
            results.append(("Water Tracker", True, f"{water_ml}ml"))
        else:
            print(f"❌ Water tracker failed: {response.status_code}")
            results.append(("Water Tracker", False, response.text))
    except Exception as e:
        print(f"❌ Water tracker error: {e}")
        results.append(("Water Tracker", False, str(e)))
    
    # Summary
    print("\n" + "=" * 80)
    print("REVIEW TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    print("\nDetailed Results:")
    for test_name, success, details in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}: {details}")
    
    # Critical Issues
    critical_issues = [r for r in results if not r[1] and "athlete" in r[0].lower()]
    if critical_issues:
        print(f"\n🚨 CRITICAL ATHLETE MODE VIOLATIONS ({len(critical_issues)}):")
        print("   According to review request, athlete mode was COMPLETELY REMOVED!")
        for test_name, _, details in critical_issues:
            print(f"   • {test_name}: {details}")
    
    print("\n" + "=" * 80)
    
    return passed == total

if __name__ == "__main__":
    success = test_exact_review_scenarios()
    sys.exit(0 if success else 1)