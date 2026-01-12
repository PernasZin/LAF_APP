#!/usr/bin/env python3
"""
Debug specific issues found in the comprehensive test
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://diet-fixer.preview.emergentagent.com/api"

def test_auth_debug():
    """Debug authentication issue"""
    print("🔍 DEBUGGING AUTHENTICATION")
    
    timestamp = int(time.time())
    test_email = f"debug_user_{timestamp}@laf.com"
    test_password = "DebugPassword123!"
    
    # Signup
    signup_data = {"email": test_email, "password": test_password}
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"Signup Status: {response.status_code}")
    print(f"Signup Response: {response.text}")
    
    if response.status_code < 400:
        signup_result = response.json()
        print(f"Signup Keys: {list(signup_result.keys())}")
        
        # Login
        login_data = {"email": test_email, "password": test_password}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text}")
        
        if response.status_code < 400:
            login_result = response.json()
            print(f"Login Keys: {list(login_result.keys())}")
            
            # Get token
            token = login_result.get("access_token")
            if token:
                print(f"Token found: {token[:50]}...")
                
                # Validate token
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{BASE_URL}/auth/validate", headers=headers)
                print(f"Validate Status: {response.status_code}")
                print(f"Validate Response: {response.text}")
                
                return login_result.get("user_id"), token
            else:
                print("❌ No token in login response")
    
    return None, None

def test_diet_generation_debug(user_id, token):
    """Debug diet generation meal count issue"""
    print(f"\n🔍 DEBUGGING DIET GENERATION for user {user_id}")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Create profile first
    profile_data = {
        "id": user_id,
        "name": "Debug User",
        "age": 30,
        "sex": "masculino",
        "height": 175.0,
        "weight": 80.0,
        "training_level": "intermediario",
        "weekly_training_frequency": 4,
        "available_time_per_session": 60,
        "goal": "cutting",
        "dietary_restrictions": [],
        "food_preferences": [],
        "meal_count": 4
    }
    
    response = requests.post(f"{BASE_URL}/user/profile", json=profile_data, headers=headers)
    print(f"Profile Creation Status: {response.status_code}")
    
    # Set meal_count to 4 in settings
    settings_data = {"meal_count": 4}
    response = requests.patch(f"{BASE_URL}/user/settings/{user_id}", json=settings_data, headers=headers)
    print(f"Settings Update Status: {response.status_code}")
    print(f"Settings Response: {response.text}")
    
    # Check settings
    response = requests.get(f"{BASE_URL}/user/settings/{user_id}", headers=headers)
    print(f"Settings Get Status: {response.status_code}")
    if response.status_code < 400:
        settings = response.json()
        print(f"Current meal_count in settings: {settings.get('meal_count')}")
    
    # Generate diet
    response = requests.post(f"{BASE_URL}/diet/generate?user_id={user_id}", headers=headers)
    print(f"Diet Generation Status: {response.status_code}")
    print(f"Diet Generation Response: {response.text}")
    
    if response.status_code < 400:
        diet = response.json()
        meals = diet.get("meals", [])
        print(f"Generated meals count: {len(meals)}")
        print(f"Expected: 4, Got: {len(meals)}")
        
        for i, meal in enumerate(meals):
            print(f"  Meal {i+1}: {meal.get('name')} - {meal.get('total_calories', 0)}kcal")

def test_workout_generation_debug(user_id, token):
    """Debug workout generation issue"""
    print(f"\n🔍 DEBUGGING WORKOUT GENERATION for user {user_id}")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Generate workout
    response = requests.post(f"{BASE_URL}/workout/generate?user_id={user_id}", headers=headers)
    print(f"Workout Generation Status: {response.status_code}")
    print(f"Workout Generation Response: {response.text}")
    
    if response.status_code < 400:
        workout = response.json()
        workouts = workout.get("workouts", [])
        print(f"Generated workouts count: {len(workouts)}")
        
        for i, day_workout in enumerate(workouts):
            exercises = day_workout.get("exercises", [])
            print(f"  Day {i+1}: {day_workout.get('name')} - {len(exercises)} exercises")

if __name__ == "__main__":
    user_id, token = test_auth_debug()
    
    if user_id and token:
        test_diet_generation_debug(user_id, token)
        test_workout_generation_debug(user_id, token)
    else:
        print("❌ Authentication failed, cannot test other endpoints")