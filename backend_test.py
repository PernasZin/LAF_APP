#!/usr/bin/env python3
"""
LAF App Backend Testing Suite
=============================
Tests all backend endpoints for the LAF (Lifestyle and Fitness) application.

Test Coverage:
1. Authentication endpoints (signup, login, validate)
2. User Profile endpoints (GET, PUT)
3. Diet endpoints (generate, get)
4. Workout endpoints (generate, get, history)

Backend URL: https://translate-fit.preview.emergentagent.com/api
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List

# Configuration
BASE_URL = "https://translate-fit.preview.emergentagent.com/api"
TIMEOUT = 30

class LAFBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        
        # Test data storage
        self.test_user_id = None
        self.test_token = None
        self.test_email = None
        self.test_password = "testpass123"
        
        # Results tracking
        self.results = {
            "auth": {},
            "profile": {},
            "diet": {},
            "workout": {}
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    headers: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Default headers
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=default_headers, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=default_headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=default_headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=default_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            # Log request details
            self.log(f"{method.upper()} {endpoint} -> {response.status_code}")
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "success": 200 <= response.status_code < 300,
                "headers": dict(response.headers)
            }
            
        except requests.exceptions.Timeout:
            self.log(f"Request timeout for {method} {endpoint}", "ERROR")
            return {"status_code": 408, "data": {"error": "Request timeout"}, "success": False}
        except requests.exceptions.ConnectionError:
            self.log(f"Connection error for {method} {endpoint}", "ERROR")
            return {"status_code": 503, "data": {"error": "Connection error"}, "success": False}
        except Exception as e:
            self.log(f"Request error for {method} {endpoint}: {str(e)}", "ERROR")
            return {"status_code": 500, "data": {"error": str(e)}, "success": False}
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        self.log("=== TESTING AUTHENTICATION ENDPOINTS ===")
        
        # Generate unique test email
        self.test_email = f"test_{uuid.uuid4().hex[:8]}@laf.com"
        
        # Test 1: POST /api/auth/signup
        self.log("Testing POST /api/auth/signup")
        signup_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = self.make_request("POST", "/auth/signup", signup_data)
        self.results["auth"]["signup"] = response
        
        if response["success"]:
            self.test_user_id = response["data"].get("user_id")
            self.test_token = response["data"].get("access_token")
            self.log(f"✅ Signup successful - User ID: {self.test_user_id}")
            
            # Validate response structure
            required_fields = ["access_token", "token_type", "expires_in", "user_id", "email"]
            missing_fields = [f for f in required_fields if f not in response["data"]]
            if missing_fields:
                self.log(f"⚠️ Missing fields in signup response: {missing_fields}", "WARN")
        else:
            self.log(f"❌ Signup failed: {response['data']}", "ERROR")
            return False
            
        # Test 2: POST /api/auth/login
        self.log("Testing POST /api/auth/login")
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        self.results["auth"]["login"] = response
        
        if response["success"]:
            self.log("✅ Login successful")
            # Update token from login
            self.test_token = response["data"].get("access_token")
        else:
            self.log(f"❌ Login failed: {response['data']}", "ERROR")
            
        # Test 3: GET /api/auth/validate
        self.log("Testing GET /api/auth/validate")
        headers = {"Authorization": f"Bearer {self.test_token}"}
        
        response = self.make_request("GET", "/auth/validate", headers=headers)
        self.results["auth"]["validate"] = response
        
        if response["success"]:
            self.log("✅ Token validation successful")
        else:
            self.log(f"❌ Token validation failed: {response['data']}", "ERROR")
            
        return True
    
    def test_profile_endpoints(self):
        """Test user profile endpoints"""
        self.log("=== TESTING USER PROFILE ENDPOINTS ===")
        
        if not self.test_user_id:
            self.log("❌ No test user ID available, skipping profile tests", "ERROR")
            return False
            
        # Create a test profile first
        self.log("Creating test profile")
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
            "dietary_restrictions": ["Sem Lactose"],
            "food_preferences": ["frango", "arroz_branco", "batata_doce", "banana"]
        }
        
        create_response = self.make_request("POST", "/user/profile", profile_data)
        if not create_response["success"]:
            self.log(f"❌ Failed to create test profile: {create_response['data']}", "ERROR")
            return False
        
        # Test 1: GET /api/user/profile/{user_id}
        self.log(f"Testing GET /api/user/profile/{self.test_user_id}")
        
        response = self.make_request("GET", f"/user/profile/{self.test_user_id}")
        self.results["profile"]["get"] = response
        
        if response["success"]:
            profile = response["data"]
            self.log("✅ Profile retrieval successful")
            
            # Validate profile structure
            required_fields = ["id", "name", "age", "sex", "height", "weight", "tdee", "target_calories", "macros"]
            missing_fields = [f for f in required_fields if f not in profile]
            if missing_fields:
                self.log(f"⚠️ Missing fields in profile: {missing_fields}", "WARN")
            
            # Validate TDEE calculation
            if "tdee" in profile and profile["tdee"] > 0:
                self.log(f"✅ TDEE calculated: {profile['tdee']} kcal")
            else:
                self.log("⚠️ TDEE not calculated or invalid", "WARN")
                
            # Validate macros
            if "macros" in profile and isinstance(profile["macros"], dict):
                macros = profile["macros"]
                if all(k in macros for k in ["protein", "carbs", "fat"]):
                    self.log(f"✅ Macros calculated: P:{macros['protein']}g C:{macros['carbs']}g F:{macros['fat']}g")
                else:
                    self.log("⚠️ Incomplete macros calculation", "WARN")
        else:
            self.log(f"❌ Profile retrieval failed: {response['data']}", "ERROR")
            
        # Test 2: PUT /api/user/profile/{user_id}
        self.log(f"Testing PUT /api/user/profile/{self.test_user_id}")
        
        update_data = {
            "weight": 78.0,
            "goal": "bulking"
        }
        
        response = self.make_request("PUT", f"/user/profile/{self.test_user_id}", update_data)
        self.results["profile"]["update"] = response
        
        if response["success"]:
            updated_profile = response["data"]
            self.log("✅ Profile update successful")
            
            # Verify weight was updated
            if updated_profile.get("weight") == 78.0:
                self.log("✅ Weight updated correctly")
            else:
                self.log(f"⚠️ Weight not updated correctly: {updated_profile.get('weight')}", "WARN")
                
            # Verify TDEE was recalculated
            if "tdee" in updated_profile and updated_profile["tdee"] > 0:
                self.log(f"✅ TDEE recalculated: {updated_profile['tdee']} kcal")
            else:
                self.log("⚠️ TDEE not recalculated", "WARN")
        else:
            self.log(f"❌ Profile update failed: {response['data']}", "ERROR")
            
        return True
    
    def test_diet_endpoints(self):
        """Test diet endpoints"""
        self.log("=== TESTING DIET ENDPOINTS ===")
        
        if not self.test_user_id:
            self.log("❌ No test user ID available, skipping diet tests", "ERROR")
            return False
            
        # Test 1: POST /api/diet/generate
        self.log(f"Testing POST /api/diet/generate")
        
        response = self.make_request("POST", f"/diet/generate?user_id={self.test_user_id}")
        self.results["diet"]["generate"] = response
        
        if response["success"]:
            diet_plan = response["data"]
            self.log("✅ Diet generation successful")
            
            # Validate diet structure
            required_fields = ["id", "user_id", "meals", "target_calories", "target_macros", "computed_calories", "computed_macros"]
            missing_fields = [f for f in required_fields if f not in diet_plan]
            if missing_fields:
                self.log(f"⚠️ Missing fields in diet plan: {missing_fields}", "WARN")
            
            # Validate meals count (should be 6 meals)
            meals = diet_plan.get("meals", [])
            if len(meals) == 6:
                self.log("✅ Diet has 6 meals as required")
                
                # Validate meal structure
                meal_names = [meal.get("name", "") for meal in meals]
                expected_meals = ["Café da Manhã", "Lanche Manhã", "Almoço", "Lanche Tarde", "Jantar", "Ceia"]
                
                for expected in expected_meals:
                    if any(expected in name for name in meal_names):
                        self.log(f"✅ Found meal: {expected}")
                    else:
                        self.log(f"⚠️ Missing expected meal: {expected}", "WARN")
                
                # Validate foods in meals
                total_foods = 0
                for i, meal in enumerate(meals):
                    foods = meal.get("foods", [])
                    total_foods += len(foods)
                    if len(foods) > 0:
                        self.log(f"✅ Meal {i+1} ({meal.get('name', 'Unknown')}) has {len(foods)} foods")
                    else:
                        self.log(f"❌ Meal {i+1} is empty", "ERROR")
                
                self.log(f"✅ Total foods in diet: {total_foods}")
            else:
                self.log(f"⚠️ Diet has {len(meals)} meals, expected 6", "WARN")
            
            # Validate calorie accuracy
            target_cal = diet_plan.get("target_calories", 0)
            computed_cal = diet_plan.get("computed_calories", 0)
            if target_cal > 0 and computed_cal > 0:
                cal_diff = abs(target_cal - computed_cal)
                cal_percent_diff = (cal_diff / target_cal) * 100
                self.log(f"✅ Calories: Target {target_cal} vs Computed {computed_cal} (Δ{cal_diff}, {cal_percent_diff:.1f}%)")
                
                if cal_percent_diff <= 15:  # Within 15% tolerance
                    self.log("✅ Calorie accuracy within acceptable range")
                else:
                    self.log(f"⚠️ Calorie difference too high: {cal_percent_diff:.1f}%", "WARN")
            
            # Validate macros accuracy
            target_macros = diet_plan.get("target_macros", {})
            computed_macros = diet_plan.get("computed_macros", {})
            
            for macro in ["protein", "carbs", "fat"]:
                target = target_macros.get(macro, 0)
                computed = computed_macros.get(macro, 0)
                if target > 0 and computed > 0:
                    diff = abs(target - computed)
                    percent_diff = (diff / target) * 100
                    self.log(f"✅ {macro.capitalize()}: Target {target}g vs Computed {computed}g (Δ{diff}g, {percent_diff:.1f}%)")
        else:
            self.log(f"❌ Diet generation failed: {response['data']}", "ERROR")
            
        # Test 2: GET /api/diet/{user_id}
        self.log(f"Testing GET /api/diet/{self.test_user_id}")
        
        response = self.make_request("GET", f"/diet/{self.test_user_id}")
        self.results["diet"]["get"] = response
        
        if response["success"]:
            self.log("✅ Diet retrieval successful")
            
            # Verify it's the same diet we just generated
            retrieved_diet = response["data"]
            if "id" in retrieved_diet:
                self.log(f"✅ Retrieved diet ID: {retrieved_diet['id']}")
            else:
                self.log("⚠️ Retrieved diet missing ID", "WARN")
        else:
            self.log(f"❌ Diet retrieval failed: {response['data']}", "ERROR")
            
        return True
    
    def test_workout_endpoints(self):
        """Test workout endpoints"""
        self.log("=== TESTING WORKOUT ENDPOINTS ===")
        
        if not self.test_user_id:
            self.log("❌ No test user ID available, skipping workout tests", "ERROR")
            return False
            
        # Test 1: POST /api/workout/generate
        self.log(f"Testing POST /api/workout/generate")
        
        response = self.make_request("POST", f"/workout/generate?user_id={self.test_user_id}")
        self.results["workout"]["generate"] = response
        
        workout_id = None
        
        if response["success"]:
            workout_plan = response["data"]
            workout_id = workout_plan.get("id")
            self.log("✅ Workout generation successful")
            
            # Validate workout structure
            required_fields = ["id", "user_id", "workout_days", "weekly_frequency", "training_level"]
            missing_fields = [f for f in required_fields if f not in workout_plan]
            if missing_fields:
                self.log(f"⚠️ Missing fields in workout plan: {missing_fields}", "WARN")
            
            # Validate workout days count
            workout_days = workout_plan.get("workout_days", [])
            expected_frequency = 4  # From our test profile
            
            if len(workout_days) == expected_frequency:
                self.log(f"✅ Workout has {len(workout_days)} days as expected")
                
                # Validate each workout day
                total_exercises = 0
                for i, day in enumerate(workout_days):
                    exercises = day.get("exercises", [])
                    total_exercises += len(exercises)
                    day_name = day.get("name", f"Day {i+1}")
                    
                    if len(exercises) > 0:
                        self.log(f"✅ {day_name} has {len(exercises)} exercises")
                        
                        # Validate exercise structure
                        for j, exercise in enumerate(exercises[:2]):  # Check first 2 exercises
                            required_ex_fields = ["name", "muscle_group", "sets", "reps", "rest"]
                            missing_ex_fields = [f for f in required_ex_fields if f not in exercise]
                            if missing_ex_fields:
                                self.log(f"⚠️ Exercise {j+1} missing fields: {missing_ex_fields}", "WARN")
                            else:
                                self.log(f"✅ Exercise: {exercise['name']} - {exercise['sets']}x{exercise['reps']}")
                    else:
                        self.log(f"❌ {day_name} has no exercises", "ERROR")
                
                self.log(f"✅ Total exercises in workout: {total_exercises}")
            else:
                self.log(f"⚠️ Workout has {len(workout_days)} days, expected {expected_frequency}", "WARN")
        else:
            self.log(f"❌ Workout generation failed: {response['data']}", "ERROR")
            
        # Test 2: GET /api/workout/{user_id}
        self.log(f"Testing GET /api/workout/{self.test_user_id}")
        
        response = self.make_request("GET", f"/workout/{self.test_user_id}")
        self.results["workout"]["get"] = response
        
        if response["success"]:
            self.log("✅ Workout retrieval successful")
            
            # Verify it's the same workout we just generated
            retrieved_workout = response["data"]
            if "id" in retrieved_workout and retrieved_workout["id"] == workout_id:
                self.log(f"✅ Retrieved correct workout ID: {workout_id}")
            else:
                self.log("⚠️ Retrieved workout ID mismatch or missing", "WARN")
        else:
            self.log(f"❌ Workout retrieval failed: {response['data']}", "ERROR")
            
        # Test 3: POST /api/workout/history/{user_id}
        self.log(f"Testing POST /api/workout/history/{self.test_user_id}")
        
        history_data = {
            "workout_day_name": "Treino A - Peito/Tríceps",
            "exercises_completed": 8,
            "total_exercises": 10,
            "duration_minutes": 45,
            "notes": "Bom treino, aumentar peso no supino"
        }
        
        response = self.make_request("POST", f"/workout/history/{self.test_user_id}", history_data)
        self.results["workout"]["history_save"] = response
        
        if response["success"]:
            self.log("✅ Workout history save successful")
            
            # Validate history entry structure
            history_entry = response["data"]
            required_fields = ["id", "user_id", "workout_day_name", "exercises_completed", "completed_at"]
            missing_fields = [f for f in required_fields if f not in history_entry]
            if missing_fields:
                self.log(f"⚠️ Missing fields in history entry: {missing_fields}", "WARN")
            else:
                self.log(f"✅ History entry created with ID: {history_entry['id']}")
        else:
            self.log(f"❌ Workout history save failed: {response['data']}", "ERROR")
            
        # Test 4: GET /api/workout/history/{user_id}
        self.log(f"Testing GET /api/workout/history/{self.test_user_id}")
        
        response = self.make_request("GET", f"/workout/history/{self.test_user_id}")
        self.results["workout"]["history_get"] = response
        
        if response["success"]:
            history_data = response["data"]
            self.log("✅ Workout history retrieval successful")
            
            # Validate history structure
            if "history" in history_data and isinstance(history_data["history"], list):
                history_count = len(history_data["history"])
                self.log(f"✅ Found {history_count} workout history entries")
                
                if history_count > 0:
                    # Check the first entry
                    first_entry = history_data["history"][0]
                    if "workout_day_name" in first_entry:
                        self.log(f"✅ Latest workout: {first_entry['workout_day_name']}")
            
            # Validate stats
            if "stats" in history_data:
                stats = history_data["stats"]
                self.log(f"✅ Workout stats: {stats.get('total_workouts', 0)} total, {stats.get('this_week_count', 0)} this week")
        else:
            self.log(f"❌ Workout history retrieval failed: {response['data']}", "ERROR")
            
        return True
    
    def run_all_tests(self):
        """Run all backend tests"""
        self.log("🚀 STARTING LAF BACKEND TESTING SUITE")
        self.log(f"Backend URL: {self.base_url}")
        
        start_time = time.time()
        
        # Run test suites
        auth_success = self.test_auth_endpoints()
        if auth_success:
            profile_success = self.test_profile_endpoints()
            diet_success = self.test_diet_endpoints()
            workout_success = self.test_workout_endpoints()
        else:
            self.log("❌ Authentication tests failed, skipping other tests", "ERROR")
            profile_success = diet_success = workout_success = False
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate summary
        self.generate_summary(duration)
        
        return {
            "auth": auth_success,
            "profile": profile_success,
            "diet": diet_success,
            "workout": workout_success
        }
    
    def generate_summary(self, duration: float):
        """Generate test summary"""
        self.log("=" * 60)
        self.log("🏁 TEST SUMMARY")
        self.log("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.results.items():
            self.log(f"\n📊 {category.upper()} ENDPOINTS:")
            
            for test_name, result in tests.items():
                total_tests += 1
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                status_code = result["status_code"]
                
                self.log(f"  {test_name}: {status} ({status_code})")
                
                if result["success"]:
                    passed_tests += 1
                else:
                    error_msg = result["data"].get("error", result["data"].get("detail", "Unknown error"))
                    self.log(f"    Error: {error_msg}")
        
        # Overall statistics
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log(f"\n📈 OVERALL RESULTS:")
        self.log(f"  Total Tests: {total_tests}")
        self.log(f"  Passed: {passed_tests}")
        self.log(f"  Failed: {total_tests - passed_tests}")
        self.log(f"  Success Rate: {success_rate:.1f}%")
        self.log(f"  Duration: {duration:.2f} seconds")
        
        if success_rate >= 80:
            self.log("🎉 BACKEND TESTING COMPLETED SUCCESSFULLY!")
        elif success_rate >= 60:
            self.log("⚠️ BACKEND TESTING COMPLETED WITH WARNINGS")
        else:
            self.log("❌ BACKEND TESTING FAILED - CRITICAL ISSUES FOUND")


def main():
    """Main test execution"""
    tester = LAFBackendTester()
    results = tester.run_all_tests()
    
    # Return exit code based on results
    if all(results.values()):
        exit(0)  # All tests passed
    else:
        exit(1)  # Some tests failed


if __name__ == "__main__":
    main()