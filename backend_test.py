#!/usr/bin/env python3
"""
LAF Backend Comprehensive Testing Suite
Testa TODOS os endpoints e cenários solicitados na auditoria completa
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configuration
BASE_URL = "https://fit-final.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class LAFTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS.copy()
        self.auth_token = None
        self.test_results = []
        self.user_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        if method.upper() == "GET":
            return requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            return requests.post(url, headers=headers, json=data, params=params)
        elif method.upper() == "PUT":
            return requests.put(url, headers=headers, json=data)
        elif method.upper() == "PATCH":
            return requests.patch(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            return requests.delete(url, headers=headers)
            
    def test_authentication(self):
        """Test all authentication endpoints"""
        print("\n🔐 TESTING AUTHENTICATION ENDPOINTS")
        
        # 1. Test Signup
        signup_data = {
            "email": f"test-{int(time.time())}@laf.com",
            "password": "TestPassword123!"
        }
        
        response = self.make_request("POST", "/auth/signup", signup_data)
        if response.status_code == 200:
            result = response.json()
            self.auth_token = result.get("access_token")  # Fixed: use access_token
            self.user_id = result.get("user_id")
            self.log_test("AUTH - Signup", True, f"User created: {self.user_id}", result)
        else:
            self.log_test("AUTH - Signup", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
            
        # 2. Test Login
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response.status_code == 200:
            result = response.json()
            self.auth_token = result.get("access_token")  # Fixed: use access_token
            self.log_test("AUTH - Login", True, "Login successful", result)
        else:
            self.log_test("AUTH - Login", False, f"Status: {response.status_code}, Response: {response.text}")
            
        # 3. Test Token Validation
        response = self.make_request("GET", "/auth/validate")
        if response.status_code == 200:
            self.log_test("AUTH - Validate Token", True, "Token valid", response.json())
        else:
            self.log_test("AUTH - Validate Token", False, f"Status: {response.status_code}, Response: {response.text}")
            
        return True
        
    def test_user_profile_all_scenarios(self):
        """Test user profile with ALL combinations requested"""
        print("\n👤 TESTING USER PROFILE - ALL SCENARIOS")
        
        # Test scenarios: All goals × All restrictions × All training levels
        test_scenarios = [
            {
                "name": "Cutting + Vegetariano + Iniciante",
                "goal": "cutting",
                "dietary_restrictions": ["vegetariano"],
                "training_level": "iniciante",
                "weekly_training_frequency": 3,
                "weight": 70,
                "height": 170,
                "age": 25,
                "sex": "masculino"
            },
            {
                "name": "Bulking + Sem Lactose + Avançado", 
                "goal": "bulking",
                "dietary_restrictions": ["sem_lactose"],
                "training_level": "avancado",
                "weekly_training_frequency": 5,
                "weight": 80,
                "height": 180,
                "age": 30,
                "sex": "masculino"
            },
            {
                "name": "Manutenção + Sem Glúten + Intermediário",
                "goal": "manutencao", 
                "dietary_restrictions": ["sem_gluten"],
                "training_level": "intermediario",
                "weekly_training_frequency": 4,
                "weight": 65,
                "height": 165,
                "age": 28,
                "sex": "feminino"
            },
            {
                "name": "Cutting + Diabético + Avançado",
                "goal": "cutting",
                "dietary_restrictions": ["diabetico"],
                "training_level": "avancado", 
                "weekly_training_frequency": 6,
                "weight": 75,
                "height": 175,
                "age": 35,
                "sex": "feminino"
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n📋 Testing scenario: {scenario['name']}")
            
            # Create profile
            profile_data = {
                "id": self.user_id,
                "name": f"Test User {scenario['name']}",
                "age": scenario["age"],
                "sex": scenario["sex"],
                "height": scenario["height"],
                "weight": scenario["weight"],
                "target_weight": scenario["weight"] - 5 if scenario["goal"] == "cutting" else scenario["weight"] + 5,
                "training_level": scenario["training_level"],
                "weekly_training_frequency": scenario["weekly_training_frequency"],
                "available_time_per_session": 60,
                "goal": scenario["goal"],
                "dietary_restrictions": scenario["dietary_restrictions"],
                "food_preferences": ["frango", "arroz", "batata_doce"],
                "meal_count": 6
            }
            
            response = self.make_request("POST", "/user/profile", profile_data)
            if response.status_code == 200:
                result = response.json()
                
                # Validate TDEE calculation
                tdee = result.get("tdee", 0)
                target_calories = result.get("target_calories", 0)
                macros = result.get("macros", {})
                
                # Check goal-specific calorie adjustments
                if scenario["goal"] == "cutting":
                    expected_ratio = target_calories / tdee
                    calorie_check = 0.75 <= expected_ratio <= 0.85  # Should be ~80% (20% deficit)
                elif scenario["goal"] == "bulking":
                    expected_ratio = target_calories / tdee  
                    calorie_check = 1.10 <= expected_ratio <= 1.15  # Should be ~112% (12% surplus)
                else:  # manutencao
                    expected_ratio = target_calories / tdee
                    calorie_check = 0.95 <= expected_ratio <= 1.05  # Should be ~100%
                    
                details = f"TDEE: {tdee}kcal, Target: {target_calories}kcal, Ratio: {expected_ratio:.2f}, Macros: P{macros.get('protein', 0)}g C{macros.get('carbs', 0)}g F{macros.get('fat', 0)}g"
                
                if calorie_check and tdee > 0 and target_calories > 0:
                    self.log_test(f"PROFILE - {scenario['name']}", True, details, result)
                else:
                    self.log_test(f"PROFILE - {scenario['name']}", False, f"Calorie calculation error: {details}")
            else:
                self.log_test(f"PROFILE - {scenario['name']}", False, f"Status: {response.status_code}, Response: {response.text}")
                
        # Test GET profile
        response = self.make_request("GET", f"/user/profile/{self.user_id}")
        if response.status_code == 200:
            self.log_test("PROFILE - Get Profile", True, "Profile retrieved successfully", response.json())
        else:
            self.log_test("PROFILE - Get Profile", False, f"Status: {response.status_code}")
            
        # Test PUT profile (update)
        update_data = {
            "weight": 72.5,
            "goal": "bulking"
        }
        response = self.make_request("PUT", f"/user/profile/{self.user_id}", update_data)
        if response.status_code == 200:
            result = response.json()
            new_weight = result.get("weight")
            new_goal = result.get("goal")
            if new_weight == 72.5 and new_goal == "bulking":
                self.log_test("PROFILE - Update Profile", True, f"Weight updated to {new_weight}kg, Goal: {new_goal}")
            else:
                self.log_test("PROFILE - Update Profile", False, f"Update not reflected: weight={new_weight}, goal={new_goal}")
        else:
            self.log_test("PROFILE - Update Profile", False, f"Status: {response.status_code}")
            
    def test_user_settings(self):
        """Test user settings endpoints"""
        print("\n⚙️ TESTING USER SETTINGS")
        
        # Test GET settings
        response = self.make_request("GET", f"/user/settings/{self.user_id}")
        if response.status_code == 200:
            self.log_test("SETTINGS - Get Settings", True, "Settings retrieved", response.json())
        else:
            self.log_test("SETTINGS - Get Settings", False, f"Status: {response.status_code}")
            
        # Test PATCH settings - meal_count configurations
        for meal_count in [4, 5, 6]:
            settings_data = {
                "meal_count": meal_count,
                "notifications_enabled": True,
                "language": "pt-BR"
            }
            
            response = self.make_request("PATCH", f"/user/settings/{self.user_id}", settings_data)
            if response.status_code == 200:
                result = response.json()
                saved_meal_count = result.get("meal_count")
                if saved_meal_count == meal_count:
                    self.log_test(f"SETTINGS - meal_count {meal_count}", True, f"Meal count set to {meal_count}")
                else:
                    self.log_test(f"SETTINGS - meal_count {meal_count}", False, f"Expected {meal_count}, got {saved_meal_count}")
            else:
                self.log_test(f"SETTINGS - meal_count {meal_count}", False, f"Status: {response.status_code}")
                
    def test_diet_generation_comprehensive(self):
        """Test diet generation with ALL requested scenarios"""
        print("\n🍽️ TESTING DIET GENERATION - COMPREHENSIVE")
        
        # Test all meal count configurations (4, 5, 6)
        for meal_count in [4, 5, 6]:
            print(f"\n📊 Testing {meal_count} meals configuration")
            
            # Set meal_count in settings first
            settings_data = {"meal_count": meal_count}
            self.make_request("PATCH", f"/user/settings/{self.user_id}", settings_data)
            
            # Generate diet
            response = self.make_request("POST", f"/diet/generate?user_id={self.user_id}")
            if response.status_code == 200:
                result = response.json()
                meals = result.get("meals", [])
                computed_calories = result.get("computed_calories", 0)
                computed_macros = result.get("computed_macros", {})
                
                # Validate meal count
                actual_meal_count = len(meals)
                meal_count_ok = actual_meal_count == meal_count
                
                # Validate each meal has total_calories
                meals_have_calories = all(meal.get("total_calories", 0) > 0 for meal in meals)
                
                # Validate realistic portions (multiples of 10)
                realistic_portions = True
                for meal in meals:
                    for food in meal.get("foods", []):
                        grams = food.get("grams", 0)
                        if grams % 10 != 0:
                            realistic_portions = False
                            break
                    if not realistic_portions:
                        break
                        
                details = f"Meals: {actual_meal_count}/{meal_count}, Calories: {computed_calories}kcal, Realistic portions: {realistic_portions}, Meals have calories: {meals_have_calories}"
                
                if meal_count_ok and meals_have_calories and realistic_portions:
                    self.log_test(f"DIET - {meal_count} meals", True, details, result)
                else:
                    self.log_test(f"DIET - {meal_count} meals", False, details)
            else:
                self.log_test(f"DIET - {meal_count} meals", False, f"Status: {response.status_code}, Response: {response.text}")
                
        # Test GET diet
        response = self.make_request("GET", f"/diet/{self.user_id}")
        if response.status_code == 200:
            self.log_test("DIET - Get Diet", True, "Diet retrieved successfully", response.json())
        else:
            self.log_test("DIET - Get Diet", False, f"Status: {response.status_code}")
            
    def test_dietary_restrictions_critical(self):
        """Test critical dietary restrictions validation"""
        print("\n🚨 TESTING DIETARY RESTRICTIONS - CRITICAL VALIDATION")
        
        restriction_tests = [
            {
                "name": "Vegetariano",
                "restrictions": ["vegetariano"],
                "forbidden_foods": ["frango", "carne", "peixe", "tilapia", "patinho"],
                "allowed_foods": ["ovos", "queijo", "feijao", "tofu"]
            },
            {
                "name": "Sem Lactose", 
                "restrictions": ["sem_lactose"],
                "forbidden_foods": ["leite", "queijo", "iogurte", "cottage", "whey"],
                "allowed_foods": ["frango", "arroz", "ovos"]
            },
            {
                "name": "Sem Glúten",
                "restrictions": ["sem_gluten"], 
                "forbidden_foods": ["pao", "aveia", "macarrao", "trigo"],
                "allowed_foods": ["arroz", "batata", "tapioca", "frango"]
            },
            {
                "name": "Diabético",
                "restrictions": ["diabetico"],
                "forbidden_foods": ["mel", "banana", "tapioca", "acucar"],
                "allowed_foods": ["frango", "arroz_integral", "broccoli"]
            }
        ]
        
        for test_case in restriction_tests:
            print(f"\n🔍 Testing {test_case['name']} restrictions")
            
            # Create profile with restriction
            profile_data = {
                "id": self.user_id,
                "name": f"Test {test_case['name']}",
                "age": 30,
                "sex": "masculino", 
                "height": 175,
                "weight": 75,
                "training_level": "intermediario",
                "weekly_training_frequency": 4,
                "available_time_per_session": 60,
                "goal": "bulking",
                "dietary_restrictions": test_case["restrictions"],
                "meal_count": 6
            }
            
            # Create profile
            self.make_request("POST", "/user/profile", profile_data)
            
            # Generate diet
            response = self.make_request("POST", f"/diet/generate?user_id={self.user_id}")
            if response.status_code == 200:
                result = response.json()
                meals = result.get("meals", [])
                
                # Check for forbidden foods
                violations = []
                all_foods = []
                
                for meal in meals:
                    for food in meal.get("foods", []):
                        food_key = food.get("key", "").lower()
                        food_name = food.get("name", "").lower()
                        all_foods.append(food_name)
                        
                        # Check if any forbidden food appears
                        for forbidden in test_case["forbidden_foods"]:
                            if forbidden.lower() in food_key or forbidden.lower() in food_name:
                                violations.append(f"{food_name} (forbidden: {forbidden})")
                                
                if len(violations) == 0:
                    self.log_test(f"RESTRICTIONS - {test_case['name']}", True, f"No violations found. Foods: {', '.join(all_foods[:10])}")
                else:
                    self.log_test(f"RESTRICTIONS - {test_case['name']}", False, f"VIOLATIONS: {', '.join(violations)}")
            else:
                self.log_test(f"RESTRICTIONS - {test_case['name']}", False, f"Diet generation failed: {response.status_code}")
                
    def test_food_substitution(self):
        """Test food substitution functionality"""
        print("\n🔄 TESTING FOOD SUBSTITUTION")
        
        # First ensure we have a diet
        response = self.make_request("GET", f"/diet/{self.user_id}")
        if response.status_code != 200:
            # Generate diet first
            self.make_request("POST", f"/diet/generate?user_id={self.user_id}")
            response = self.make_request("GET", f"/diet/{self.user_id}")
            
        if response.status_code == 200:
            diet = response.json()
            meals = diet.get("meals", [])
            
            if meals and len(meals) > 0:
                # Find first food to substitute
                first_meal = meals[0]
                foods = first_meal.get("foods", [])
                
                if foods and len(foods) > 0:
                    first_food = foods[0]
                    food_key = first_food.get("key")
                    
                    if food_key:
                        # Test GET substitutes
                        response = self.make_request("GET", f"/diet/{self.user_id}/substitutes/{food_key}")
                        if response.status_code == 200:
                            result = response.json()
                            substitutes = result.get("substitutes", [])
                            substitute_count = len(substitutes)
                            
                            self.log_test("SUBSTITUTION - Get Substitutes", True, f"Found {substitute_count} substitutes for {first_food.get('name')}")
                            
                            # Test actual substitution if we have substitutes
                            if substitutes and len(substitutes) > 0:
                                new_food_key = substitutes[0].get("key")
                                
                                substitution_data = {
                                    "meal_index": 0,
                                    "food_index": 0, 
                                    "new_food_key": new_food_key
                                }
                                
                                response = self.make_request("PUT", f"/diet/{self.user_id}/substitute", substitution_data)
                                if response.status_code == 200:
                                    # Verify substitution worked
                                    response = self.make_request("GET", f"/diet/{self.user_id}")
                                    if response.status_code == 200:
                                        updated_diet = response.json()
                                        updated_food = updated_diet["meals"][0]["foods"][0]
                                        new_key = updated_food.get("key")
                                        
                                        if new_key == new_food_key:
                                            self.log_test("SUBSTITUTION - Execute Substitution", True, f"Successfully substituted {first_food.get('name')} → {updated_food.get('name')}")
                                        else:
                                            self.log_test("SUBSTITUTION - Execute Substitution", False, f"Substitution not applied: expected {new_food_key}, got {new_key}")
                                    else:
                                        self.log_test("SUBSTITUTION - Execute Substitution", False, "Could not verify substitution")
                                else:
                                    self.log_test("SUBSTITUTION - Execute Substitution", False, f"Status: {response.status_code}")
                            else:
                                self.log_test("SUBSTITUTION - Execute Substitution", False, "No substitutes available")
                        else:
                            self.log_test("SUBSTITUTION - Get Substitutes", False, f"Status: {response.status_code}")
                    else:
                        self.log_test("SUBSTITUTION - Get Substitutes", False, "No food key found")
                else:
                    self.log_test("SUBSTITUTION - Get Substitutes", False, "No foods in first meal")
            else:
                self.log_test("SUBSTITUTION - Get Substitutes", False, "No meals in diet")
        else:
            self.log_test("SUBSTITUTION - Get Substitutes", False, "Could not get diet")
            
    def test_workout_generation(self):
        """Test workout generation with different frequencies"""
        print("\n💪 TESTING WORKOUT GENERATION")
        
        # Test different training frequencies
        frequencies = [2, 3, 4, 5, 6]
        
        for freq in frequencies:
            print(f"\n🏋️ Testing {freq}x/week training frequency")
            
            # Update profile with new frequency
            update_data = {
                "weekly_training_frequency": freq,
                "training_level": "avancado"  # Test advanced level
            }
            self.make_request("PUT", f"/user/profile/{self.user_id}", update_data)
            
            # Generate workout
            response = self.make_request("POST", f"/workout/generate?user_id={self.user_id}")
            if response.status_code == 200:
                result = response.json()
                workouts = result.get("workouts", [])
                workout_count = len(workouts)
                
                # Validate workout count matches frequency
                frequency_match = workout_count == freq
                
                # Validate sets limit (≤ 4 sets per exercise)
                sets_valid = True
                max_sets_found = 0
                
                for workout in workouts:
                    exercises = workout.get("exercises", [])
                    for exercise in exercises:
                        sets = exercise.get("sets", 0)
                        max_sets_found = max(max_sets_found, sets)
                        if sets > 4:
                            sets_valid = False
                            break
                    if not sets_valid:
                        break
                        
                details = f"Workouts: {workout_count}/{freq}, Max sets: {max_sets_found}, Sets valid: {sets_valid}"
                
                if frequency_match and sets_valid:
                    self.log_test(f"WORKOUT - {freq}x frequency", True, details)
                else:
                    self.log_test(f"WORKOUT - {freq}x frequency", False, details)
            else:
                self.log_test(f"WORKOUT - {freq}x frequency", False, f"Status: {response.status_code}")
                
        # Test GET workout
        response = self.make_request("GET", f"/workout/{self.user_id}")
        if response.status_code == 200:
            self.log_test("WORKOUT - Get Workout", True, "Workout retrieved successfully")
        else:
            self.log_test("WORKOUT - Get Workout", False, f"Status: {response.status_code}")
            
    def test_training_cycle_system(self):
        """Test new training cycle automatic system endpoints"""
        print("\n🔄 TESTING TRAINING CYCLE SYSTEM")
        
        # Test setup training cycle
        setup_data = {"weekly_training_frequency": 4}
        response = self.make_request("POST", f"/training-cycle/setup/{self.user_id}", setup_data)
        if response.status_code == 200:
            result = response.json()
            first_day_type = result.get("first_day_type")
            if first_day_type == "rest":  # Day 0 should always be rest
                self.log_test("TRAINING CYCLE - Setup", True, f"Setup successful, first day: {first_day_type}")
            else:
                self.log_test("TRAINING CYCLE - Setup", False, f"Expected rest, got {first_day_type}")
        else:
            self.log_test("TRAINING CYCLE - Setup", False, f"Status: {response.status_code}")
            
        # Test get status
        response = self.make_request("GET", f"/training-cycle/status/{self.user_id}")
        if response.status_code == 200:
            result = response.json()
            day_type = result.get("day_type")
            calorie_multiplier = result.get("calorie_multiplier")
            carb_multiplier = result.get("carb_multiplier")
            
            details = f"Day type: {day_type}, Cal mult: {calorie_multiplier}, Carb mult: {carb_multiplier}"
            self.log_test("TRAINING CYCLE - Status", True, details)
        else:
            self.log_test("TRAINING CYCLE - Status", False, f"Status: {response.status_code}")
            
        # Test start session
        response = self.make_request("POST", f"/training-cycle/start-session/{self.user_id}")
        if response.status_code == 200:
            self.log_test("TRAINING CYCLE - Start Session", True, "Session started successfully")
            
            # Test finish session
            finish_data = {"duration": "60:00", "exercises_completed": 8}
            response = self.make_request("POST", f"/training-cycle/finish-session/{self.user_id}", finish_data)
            if response.status_code == 200:
                self.log_test("TRAINING CYCLE - Finish Session", True, "Session finished successfully")
            else:
                self.log_test("TRAINING CYCLE - Finish Session", False, f"Status: {response.status_code}")
        else:
            self.log_test("TRAINING CYCLE - Start Session", False, f"Status: {response.status_code}")
            
        # Test week preview
        response = self.make_request("GET", f"/training-cycle/week-preview/{self.user_id}")
        if response.status_code == 200:
            result = response.json()
            days = result.get("days", [])
            if len(days) == 7:
                self.log_test("TRAINING CYCLE - Week Preview", True, f"7 days returned: {[d.get('day_type') for d in days]}")
            else:
                self.log_test("TRAINING CYCLE - Week Preview", False, f"Expected 7 days, got {len(days)}")
        else:
            self.log_test("TRAINING CYCLE - Week Preview", False, f"Status: {response.status_code}")
            
    def test_progress_weight_tracking(self):
        """Test progress and weight tracking with 14-day blocking"""
        print("\n📊 TESTING PROGRESS & WEIGHT TRACKING")
        
        # Test can-update check (should be true for first time)
        response = self.make_request("GET", f"/progress/weight/{self.user_id}/can-update")
        if response.status_code == 200:
            result = response.json()
            can_update = result.get("can_update", False)
            self.log_test("PROGRESS - Can Update Check", True, f"Can update: {can_update}")
            
            if can_update:
                # Test weight registration with questionnaire
                checkin_data = {
                    "weight": 75.5,
                    "questionnaire": {
                        "diet": 8,
                        "training": 7,
                        "cardio": 6,
                        "sleep": 7,
                        "hydration": 8,
                        "energy": 7,
                        "hunger": 5,
                        "followedDiet": "yes",
                        "followedTraining": "mostly",
                        "followedCardio": "yes",
                        "boredFoods": "",
                        "observations": "Feeling good overall"
                    }
                }
                
                response = self.make_request("POST", f"/progress/checkin/{self.user_id}", checkin_data)
                if response.status_code == 200:
                    result = response.json()
                    self.log_test("PROGRESS - Weight Registration", True, "Weight registered successfully", result)
                    
                    # Test 14-day blocking (should now be blocked)
                    response = self.make_request("GET", f"/progress/can-update/{self.user_id}")
                    if response.status_code == 200:
                        result = response.json()
                        can_update_after = result.get("can_update", True)
                        if not can_update_after:
                            self.log_test("PROGRESS - 14-day Blocking", True, "Correctly blocked after registration")
                        else:
                            self.log_test("PROGRESS - 14-day Blocking", False, "Should be blocked but isn't")
                    else:
                        self.log_test("PROGRESS - 14-day Blocking", False, f"Status: {response.status_code}")
                else:
                    self.log_test("PROGRESS - Weight Registration", False, f"Status: {response.status_code}")
            else:
                self.log_test("PROGRESS - Weight Registration", False, "Cannot update weight at this time")
        else:
            self.log_test("PROGRESS - Can Update Check", False, f"Status: {response.status_code}")
            
        # Test weight history
        response = self.make_request("GET", f"/progress/weight/{self.user_id}")
        if response.status_code == 200:
            result = response.json()
            records = result.get("records", [])
            self.log_test("PROGRESS - Weight History", True, f"Found {len(records)} weight records")
        else:
            self.log_test("PROGRESS - Weight History", False, f"Status: {response.status_code}")
            
    def test_goal_switching(self):
        """Test goal switching functionality"""
        print("\n🎯 TESTING GOAL SWITCHING")
        
        goals_to_test = ["cutting", "bulking", "manutencao"]
        
        for goal in goals_to_test:
            response = self.make_request("POST", f"/user/{self.user_id}/switch-goal/{goal}")
            if response.status_code == 200:
                result = response.json()
                new_goal = result.get("new_goal")
                success = result.get("success", False)
                
                if success and new_goal == goal:
                    self.log_test(f"GOAL SWITCH - {goal}", True, f"Successfully switched to {goal}")
                else:
                    self.log_test(f"GOAL SWITCH - {goal}", False, f"Switch failed: success={success}, goal={new_goal}")
            else:
                self.log_test(f"GOAL SWITCH - {goal}", False, f"Status: {response.status_code}")
                
    def test_water_tracking(self):
        """Test water tracking system"""
        print("\n💧 TESTING WATER TRACKING")
        
        # Test water registration - correct endpoint is /tracker/water-sodium/{user_id}
        water_data = {"water_ml": 500}
        response = self.make_request("POST", f"/tracker/water-sodium/{self.user_id}", water_data)
        if response.status_code == 200:
            result = response.json()
            total_water = result.get("water_ml", 0)
            self.log_test("WATER - Registration", True, f"Water registered: {total_water}ml total")
        else:
            self.log_test("WATER - Registration", False, f"Status: {response.status_code}")
            
        # Test water retrieval
        response = self.make_request("GET", f"/tracker/water-sodium/{self.user_id}")
        if response.status_code == 200:
            result = response.json()
            self.log_test("WATER - Retrieval", True, "Water data retrieved successfully")
        else:
            self.log_test("WATER - Retrieval", False, f"Status: {response.status_code}")
            
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 STARTING LAF COMPREHENSIVE BACKEND TESTING")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Authentication must work first
            if not self.test_authentication():
                print("❌ Authentication failed - stopping tests")
                return
                
            # Run all test suites
            self.test_user_profile_all_scenarios()
            self.test_user_settings()
            self.test_diet_generation_comprehensive()
            self.test_dietary_restrictions_critical()
            self.test_food_substitution()
            self.test_workout_generation()
            self.test_training_cycle_system()
            self.test_progress_weight_tracking()
            self.test_goal_switching()
            self.test_water_tracking()
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {e}")
            
        # Generate final report
        end_time = time.time()
        duration = end_time - start_time
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 FINAL TEST REPORT")
        print("=" * 60)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
                    
        print("\n🎯 CRITICAL VALIDATIONS:")
        
        # Check for critical issues
        critical_issues = []
        
        # Check dietary restrictions
        restriction_failures = [r for r in self.test_results if "RESTRICTIONS" in r["test"] and not r["success"]]
        if restriction_failures:
            critical_issues.append(f"🚨 DIETARY RESTRICTIONS VIOLATIONS: {len(restriction_failures)} failures")
            
        # Check meal count functionality
        meal_count_failures = [r for r in self.test_results if "meals" in r["test"] and not r["success"]]
        if meal_count_failures:
            critical_issues.append(f"🚨 MEAL COUNT ISSUES: {len(meal_count_failures)} failures")
            
        # Check workout sets limit
        workout_failures = [r for r in self.test_results if "WORKOUT" in r["test"] and not r["success"]]
        if workout_failures:
            critical_issues.append(f"🚨 WORKOUT GENERATION ISSUES: {len(workout_failures)} failures")
            
        if critical_issues:
            print("🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   • {issue}")
        else:
            print("✅ No critical issues found!")
            
        # Success criteria
        if success_rate >= 95:
            print(f"\n🎉 SUCCESS: {success_rate:.1f}% success rate meets 95% minimum requirement!")
        else:
            print(f"\n⚠️  WARNING: {success_rate:.1f}% success rate below 95% minimum requirement")
            
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "critical_issues": critical_issues,
            "duration": duration
        }

if __name__ == "__main__":
    tester = LAFTester()
    results = tester.run_comprehensive_test()