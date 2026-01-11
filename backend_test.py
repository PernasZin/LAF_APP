#!/usr/bin/env python3
"""
LAF Backend Comprehensive Testing Suite
Tests all critical endpoints and user flows as requested
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Base URL from frontend .env
BASE_URL = "https://fit-track-hub.preview.emergentagent.com/api"

class LAFBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_user_id = None
        self.auth_token = None
        self.test_results = []
        
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
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{self.base_url}{endpoint}"
        
        # Add auth header if we have token
        if self.auth_token and headers is None:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
        elif self.auth_token and headers:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=30)
            else:
                return False, f"Unsupported method: {method}", 0
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return response.status_code < 400, response_data, response.status_code
            
        except Exception as e:
            return False, f"Request failed: {str(e)}", 0
    
    def test_authentication_flow(self):
        """Test complete authentication flow"""
        print("🔐 TESTING AUTHENTICATION FLOW")
        
        # Generate unique test email
        timestamp = int(time.time())
        test_email = f"test_user_{timestamp}@laf.com"
        test_password = "TestPassword123"
        
        # 1. Test Signup
        signup_data = {
            "email": test_email,
            "password": test_password
        }
        
        success, response, status = self.make_request("POST", "/auth/signup", signup_data)
        
        if success and isinstance(response, dict) and "access_token" in response:
            self.auth_token = response["access_token"]
            self.test_user_id = response.get("user_id")
            self.log_test("AUTH - Signup", True, f"User created with ID: {self.test_user_id}")
        else:
            self.log_test("AUTH - Signup", False, f"Status: {status}", response)
            return False
        
        # 2. Test Login
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        success, response, status = self.make_request("POST", "/auth/login", login_data)
        
        if success and isinstance(response, dict) and "token" in response:
            self.log_test("AUTH - Login", True, "Login successful")
        else:
            self.log_test("AUTH - Login", False, f"Status: {status}", response)
        
        # 3. Test Token Validation
        success, response, status = self.make_request("GET", "/auth/validate")
        
        if success and isinstance(response, dict) and response.get("user_id"):
            self.log_test("AUTH - Token Validation", True, f"Token valid for user: {response.get('user_id')}")
        else:
            self.log_test("AUTH - Token Validation", False, f"Status: {status}", response)
        
        return True
    
    def test_user_profile_flow(self):
        """Test user profile CRUD operations"""
        print("👤 TESTING USER PROFILE FLOW")
        
        if not self.test_user_id:
            self.log_test("PROFILE - Setup", False, "No test user ID available")
            return False
        
        # 1. Create Profile
        profile_data = {
            "id": self.test_user_id,
            "name": "João Silva",
            "age": 30,
            "sex": "masculino",
            "height": 175.0,
            "weight": 80.0,
            "target_weight": 75.0,
            "body_fat_percentage": 15.0,
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "goal": "cutting",
            "dietary_restrictions": ["lactose"],
            "food_preferences": ["frango", "arroz", "batata_doce"],
            "injury_history": []
        }
        
        success, response, status = self.make_request("POST", "/user/profile", profile_data)
        
        if success and isinstance(response, dict) and response.get("tdee"):
            tdee = response.get("tdee")
            target_calories = response.get("target_calories")
            macros = response.get("macros", {})
            self.log_test("PROFILE - Create", True, 
                         f"TDEE: {tdee}kcal, Target: {target_calories}kcal, Macros: P{macros.get('protein')}g C{macros.get('carbs')}g F{macros.get('fat')}g")
        else:
            self.log_test("PROFILE - Create", False, f"Status: {status}", response)
            return False
        
        # 2. Get Profile
        success, response, status = self.make_request("GET", f"/user/profile/{self.test_user_id}")
        
        if success and isinstance(response, dict) and response.get("name") == "João Silva":
            self.log_test("PROFILE - Get", True, f"Profile retrieved: {response.get('name')}, TDEE: {response.get('tdee')}")
        else:
            self.log_test("PROFILE - Get", False, f"Status: {status}", response)
        
        # 3. Update Profile
        update_data = {
            "weight": 78.0,
            "goal": "bulking"
        }
        
        success, response, status = self.make_request("PUT", f"/user/profile/{self.test_user_id}", update_data)
        
        if success and isinstance(response, dict):
            new_weight = response.get("weight")
            new_goal = response.get("goal")
            new_target_calories = response.get("target_calories")
            self.log_test("PROFILE - Update", True, 
                         f"Weight: {new_weight}kg, Goal: {new_goal}, New Target: {new_target_calories}kcal")
        else:
            self.log_test("PROFILE - Update", False, f"Status: {status}", response)
        
        return True
    
    def test_user_settings_flow(self):
        """Test user settings endpoints - CRITICAL for meal_count"""
        print("⚙️ TESTING USER SETTINGS FLOW")
        
        if not self.test_user_id:
            self.log_test("SETTINGS - Setup", False, "No test user ID available")
            return False
        
        # 1. Get Settings (should return defaults)
        success, response, status = self.make_request("GET", f"/user/settings/{self.test_user_id}")
        
        if success and isinstance(response, dict):
            meal_count = response.get("meal_count", 6)
            self.log_test("SETTINGS - Get", True, f"Default meal_count: {meal_count}")
        else:
            self.log_test("SETTINGS - Get", False, f"Status: {status}", response)
        
        # 2. Update Settings (change meal_count to 4)
        settings_data = {
            "meal_count": 4,
            "notifications_enabled": True,
            "language": "pt-BR"
        }
        
        success, response, status = self.make_request("PATCH", f"/user/settings/{self.test_user_id}", settings_data)
        
        if success:
            self.log_test("SETTINGS - Update", True, "Settings updated successfully")
        else:
            self.log_test("SETTINGS - Update", False, f"Status: {status}", response)
        
        # 3. Verify Settings Persistence
        success, response, status = self.make_request("GET", f"/user/settings/{self.test_user_id}")
        
        if success and isinstance(response, dict):
            meal_count = response.get("meal_count")
            if meal_count == 4:
                self.log_test("SETTINGS - Persistence", True, f"meal_count correctly saved as {meal_count}")
            else:
                self.log_test("SETTINGS - Persistence", False, f"Expected meal_count=4, got {meal_count}")
        else:
            self.log_test("SETTINGS - Persistence", False, f"Status: {status}", response)
        
        return True
    
    def test_diet_generation_flow(self):
        """Test diet generation and management - CRITICAL"""
        print("🍽️ TESTING DIET GENERATION FLOW")
        
        if not self.test_user_id:
            self.log_test("DIET - Setup", False, "No test user ID available")
            return False
        
        # 1. Generate Diet (should use meal_count=4 from settings)
        success, response, status = self.make_request("POST", f"/diet/generate?user_id={self.test_user_id}")
        
        if success and isinstance(response, dict) and "meals" in response:
            meals = response.get("meals", [])
            meal_count = len(meals)
            computed_calories = response.get("computed_calories")
            computed_macros = response.get("computed_macros", {})
            
            # Check if meal count matches settings (should be 4)
            expected_meals = 4  # We set this in settings test
            if meal_count == expected_meals:
                self.log_test("DIET - Generate", True, 
                             f"Diet generated with {meal_count} meals, {computed_calories}kcal, P{computed_macros.get('protein')}g C{computed_macros.get('carbs')}g F{computed_macros.get('fat')}g")
            else:
                self.log_test("DIET - Generate", False, 
                             f"Expected {expected_meals} meals, got {meal_count}")
            
            # Validate meal structure and calories per meal
            for i, meal in enumerate(meals):
                if not meal.get("foods") or len(meal.get("foods", [])) == 0:
                    self.log_test("DIET - Meal Structure", False, f"Meal {i} has no foods")
                    return False
                
                # Check if each meal has calories field
                if "total_calories" not in meal:
                    self.log_test("DIET - Meal Calories", False, f"Meal {i} missing total_calories field")
                else:
                    self.log_test("DIET - Meal Calories", True, f"Meal {i} ({meal.get('name', 'Unknown')}) has {meal['total_calories']} calories")
            
        else:
            self.log_test("DIET - Generate", False, f"Status: {status}", response)
            return False
        
        # 2. Get Diet
        success, response, status = self.make_request("GET", f"/diet/{self.test_user_id}")
        
        if success and isinstance(response, dict) and "meals" in response:
            self.log_test("DIET - Get", True, f"Diet retrieved with {len(response.get('meals', []))} meals")
        else:
            self.log_test("DIET - Get", False, f"Status: {status}", response)
        
        return True
    
    def test_food_substitution_flow(self):
        """Test food substitution functionality - REPORTED BUG"""
        print("🔄 TESTING FOOD SUBSTITUTION FLOW")
        
        if not self.test_user_id:
            self.log_test("SUBSTITUTION - Setup", False, "No test user ID available")
            return False
        
        # 1. Get current diet to find a food to substitute
        success, response, status = self.make_request("GET", f"/diet/{self.test_user_id}")
        
        if not success or not isinstance(response, dict) or "meals" not in response:
            self.log_test("SUBSTITUTION - Get Diet", False, "Could not retrieve diet for substitution test")
            return False
        
        meals = response.get("meals", [])
        if not meals or not meals[0].get("foods"):
            self.log_test("SUBSTITUTION - Find Food", False, "No foods found in diet")
            return False
        
        # Find a protein food to substitute
        target_food = None
        meal_index = 0
        food_index = 0
        
        for i, meal in enumerate(meals):
            for j, food in enumerate(meal.get("foods", [])):
                if food.get("category") == "protein":
                    target_food = food
                    meal_index = i
                    food_index = j
                    break
            if target_food:
                break
        
        if not target_food:
            self.log_test("SUBSTITUTION - Find Protein", False, "No protein food found for substitution")
            return False
        
        food_key = target_food.get("key")
        original_name = target_food.get("name")
        
        self.log_test("SUBSTITUTION - Target Food", True, 
                     f"Found {original_name} ({food_key}) in meal {meal_index}")
        
        # 2. Get substitutes for the food
        success, response, status = self.make_request("GET", f"/diet/{self.test_user_id}/substitutes/{food_key}")
        
        if success and isinstance(response, dict) and "substitutes" in response:
            substitutes = response.get("substitutes", [])
            if substitutes:
                substitute = substitutes[0]  # Use first substitute
                substitute_key = substitute.get("key")
                substitute_name = substitute.get("name")
                
                self.log_test("SUBSTITUTION - Get Substitutes", True, 
                             f"Found {len(substitutes)} substitutes, using {substitute_name}")
                
                # 3. Perform substitution
                substitution_data = {
                    "meal_index": meal_index,
                    "food_index": food_index,
                    "new_food_key": substitute_key
                }
                
                success, response, status = self.make_request("PUT", f"/diet/{self.test_user_id}/substitute", substitution_data)
                
                if success and isinstance(response, dict):
                    self.log_test("SUBSTITUTION - Execute", True, 
                                 f"Substituted {original_name} → {substitute_name}")
                    
                    # 4. Verify substitution was applied
                    success, response, status = self.make_request("GET", f"/diet/{self.test_user_id}")
                    
                    if success and isinstance(response, dict):
                        new_meals = response.get("meals", [])
                        if (meal_index < len(new_meals) and 
                            food_index < len(new_meals[meal_index].get("foods", [])) and
                            new_meals[meal_index]["foods"][food_index].get("key") == substitute_key):
                            
                            self.log_test("SUBSTITUTION - Verify", True, 
                                         f"Substitution verified: food is now {substitute_name}")
                        else:
                            self.log_test("SUBSTITUTION - Verify", False, 
                                         "Substitution not found in updated diet")
                    else:
                        self.log_test("SUBSTITUTION - Verify", False, "Could not retrieve diet to verify substitution")
                
                else:
                    self.log_test("SUBSTITUTION - Execute", False, f"Status: {status}", response)
            else:
                self.log_test("SUBSTITUTION - Get Substitutes", False, "No substitutes found")
        else:
            self.log_test("SUBSTITUTION - Get Substitutes", False, f"Status: {status}", response)
        
        return True
    
    def test_workout_generation_flow(self):
        """Test workout generation"""
        print("🏋️ TESTING WORKOUT GENERATION FLOW")
        
        if not self.test_user_id:
            self.log_test("WORKOUT - Setup", False, "No test user ID available")
            return False
        
        # 1. Generate Workout
        success, response, status = self.make_request("POST", f"/workout/generate?user_id={self.test_user_id}")
        
        if success and isinstance(response, dict) and "workouts" in response:
            workouts = response.get("workouts", [])
            workout_count = len(workouts)
            
            # Should match weekly_training_frequency from profile (4)
            expected_workouts = 4
            if workout_count == expected_workouts:
                self.log_test("WORKOUT - Generate", True, 
                             f"Generated {workout_count} workouts matching frequency")
            else:
                self.log_test("WORKOUT - Generate", False, 
                             f"Expected {expected_workouts} workouts, got {workout_count}")
            
            # Check workout structure
            for i, workout in enumerate(workouts):
                if not workout.get("exercises") or len(workout.get("exercises", [])) == 0:
                    self.log_test("WORKOUT - Structure", False, f"Workout {i} has no exercises")
                else:
                    exercise_count = len(workout.get("exercises", []))
                    self.log_test("WORKOUT - Structure", True, f"Workout {i} has {exercise_count} exercises")
        else:
            self.log_test("WORKOUT - Generate", False, f"Status: {status}", response)
            return False
        
        # 2. Get Workout
        success, response, status = self.make_request("GET", f"/workout/{self.test_user_id}")
        
        if success and isinstance(response, dict) and "workouts" in response:
            self.log_test("WORKOUT - Get", True, f"Workout retrieved with {len(response.get('workouts', []))} workouts")
        else:
            self.log_test("WORKOUT - Get", False, f"Status: {status}", response)
        
        return True
    
    def test_meal_count_configuration_scenario(self):
        """Test critical scenario: meal_count configuration affects diet generation"""
        print("🔧 TESTING MEAL COUNT CONFIGURATION SCENARIO")
        
        if not self.test_user_id:
            self.log_test("MEAL_COUNT - Setup", False, "No test user ID available")
            return False
        
        # Test different meal counts
        for meal_count in [4, 5, 6]:
            print(f"  Testing meal_count = {meal_count}")
            
            # 1. Update settings
            settings_data = {"meal_count": meal_count}
            success, response, status = self.make_request("PATCH", f"/user/settings/{self.test_user_id}", settings_data)
            
            if not success:
                self.log_test(f"MEAL_COUNT - Set {meal_count}", False, f"Failed to set meal_count to {meal_count}")
                continue
            
            # 2. Generate new diet
            success, response, status = self.make_request("POST", f"/diet/generate?user_id={self.test_user_id}")
            
            if success and isinstance(response, dict) and "meals" in response:
                actual_meals = len(response.get("meals", []))
                if actual_meals == meal_count:
                    self.log_test(f"MEAL_COUNT - Generate {meal_count}", True, 
                                 f"Diet correctly generated with {actual_meals} meals")
                else:
                    self.log_test(f"MEAL_COUNT - Generate {meal_count}", False, 
                                 f"Expected {meal_count} meals, got {actual_meals}")
            else:
                self.log_test(f"MEAL_COUNT - Generate {meal_count}", False, f"Status: {status}", response)
        
        return True
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 STARTING LAF BACKEND COMPREHENSIVE TESTING")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test flows
        self.test_authentication_flow()
        self.test_user_profile_flow()
        self.test_user_settings_flow()
        self.test_diet_generation_flow()
        self.test_food_substitution_flow()
        self.test_workout_generation_flow()
        self.test_meal_count_configuration_scenario()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  - {test['test']}: {test['details']}")
        
        print("\n🎯 CRITICAL ISSUES FOUND:")
        critical_issues = []
        
        # Check for critical failures
        auth_failed = any(not t["success"] for t in self.test_results if "AUTH" in t["test"])
        diet_failed = any(not t["success"] for t in self.test_results if "DIET" in t["test"])
        substitution_failed = any(not t["success"] for t in self.test_results if "SUBSTITUTION" in t["test"])
        meal_count_failed = any(not t["success"] for t in self.test_results if "MEAL_COUNT" in t["test"])
        
        if auth_failed:
            critical_issues.append("🔐 Authentication system has issues")
        if diet_failed:
            critical_issues.append("🍽️ Diet generation system has issues")
        if substitution_failed:
            critical_issues.append("🔄 Food substitution system has issues")
        if meal_count_failed:
            critical_issues.append("⚙️ Meal count configuration system has issues")
        
        if critical_issues:
            for issue in critical_issues:
                print(f"  {issue}")
        else:
            print("  No critical issues found! 🎉")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = LAFBackendTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with error code if tests failed
    exit(0 if failed == 0 else 1)