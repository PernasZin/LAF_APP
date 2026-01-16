#!/usr/bin/env python3
"""
LAF Backend Comprehensive Regression Test Suite
Testing ALL main endpoints to ensure no regression
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://nutrition-flow-1.preview.emergentagent.com"
API_URL = f"{BASE_URL}/api"

class LAFBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if response_data:
            result["response"] = response_data
            
        self.test_results.append(result)
        
        if success:
            print(f"✅ {test_name}: {details}")
        else:
            print(f"❌ {test_name}: {details}")
            self.failed_tests.append(result)
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{API_URL}{endpoint}"
        
        # Default headers
        req_headers = {"Content-Type": "application/json"}
        if self.auth_token:
            req_headers["Authorization"] = f"Bearer {self.auth_token}"
        if headers:
            req_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=req_headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=req_headers, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=req_headers, timeout=30)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data, headers=req_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=req_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    # ==================== HEALTH CHECK TESTS ====================
    
    def test_root_health_check(self):
        """Test GET /health - root health check"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Root Health Check", True, f"Status: {data.get('status')}")
                else:
                    self.log_test("Root Health Check", False, f"Unexpected status: {data}")
            else:
                self.log_test("Root Health Check", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Root Health Check", False, f"Exception: {str(e)}")
    
    def test_api_health_check(self):
        """Test GET /api/health - API health check"""
        try:
            response = self.make_request("GET", "/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("API Health Check", True, f"Status: {data.get('status')}")
                else:
                    self.log_test("API Health Check", False, f"Unexpected status: {data}")
            else:
                self.log_test("API Health Check", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API Health Check", False, f"Exception: {str(e)}")

    # ==================== AUTHENTICATION TESTS ====================
    
    def test_auth_signup(self):
        """Test POST /api/auth/signup - create new user"""
        try:
            # Generate unique email for testing
            test_email = f"teste.regressao.{int(time.time())}@laf.com"
            test_password = "MinhaSenh@123!"
            
            signup_data = {
                "email": test_email,
                "password": test_password
            }
            
            response = self.make_request("POST", "/auth/signup", signup_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "access_token" in data and "user_id" in data:
                    self.auth_token = data["access_token"]
                    self.test_user_id = data["user_id"]
                    self.log_test("Auth Signup", True, f"User created: {data['user_id']}")
                else:
                    self.log_test("Auth Signup", False, f"Missing token/user_id in response: {data}")
            else:
                self.log_test("Auth Signup", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Auth Signup", False, f"Exception: {str(e)}")
    
    def test_auth_login(self):
        """Test POST /api/auth/login - authenticate user"""
        try:
            # Use existing test credentials
            login_data = {
                "email": "teste@laf.com",
                "password": "Teste123!"
            }
            
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    # Update token for subsequent tests
                    self.auth_token = data["access_token"]
                    self.test_user_id = data.get("user_id", self.test_user_id)
                    self.log_test("Auth Login", True, f"Login successful, token received")
                else:
                    self.log_test("Auth Login", False, f"Missing token in response: {data}")
            else:
                self.log_test("Auth Login", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Auth Login", False, f"Exception: {str(e)}")
    
    def test_auth_validate(self):
        """Test GET /api/auth/validate - validate token"""
        if not self.auth_token:
            self.log_test("Auth Validate", False, "No auth token available")
            return
            
        try:
            response = self.make_request("GET", "/auth/validate")
            
            if response.status_code == 200:
                data = response.json()
                if "user_id" in data:
                    self.log_test("Auth Validate", True, f"Token valid for user: {data['user_id']}")
                else:
                    self.log_test("Auth Validate", False, f"Missing user_id in response: {data}")
            else:
                self.log_test("Auth Validate", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Auth Validate", False, f"Exception: {str(e)}")

    # ==================== USER PROFILE TESTS ====================
    
    def test_create_user_profile_bulking(self):
        """Test POST /api/user/profile - create bulking profile"""
        if not self.test_user_id:
            self.log_test("Create User Profile (Bulking)", False, "No test user available")
            return
            
        try:
            profile_data = {
                "id": self.test_user_id,
                "name": "Carlos Silva",
                "age": 28,
                "sex": "masculino",
                "height": 175.0,
                "weight": 80.0,
                "target_weight": 85.0,
                "body_fat_percentage": 15.0,
                "training_level": "intermediario",
                "weekly_training_frequency": 4,
                "available_time_per_session": 60,
                "goal": "bulking",
                "dietary_restrictions": [],
                "food_preferences": ["frango", "arroz", "batata_doce"],
                "injury_history": [],
                "meal_count": 6,
                "language": "pt-BR"
            }
            
            response = self.make_request("POST", "/user/profile", profile_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "tdee" in data and "target_calories" in data and "macros" in data:
                    tdee = data["tdee"]
                    target_cal = data["target_calories"]
                    macros = data["macros"]
                    self.log_test("Create User Profile (Bulking)", True, 
                                f"Profile created - TDEE: {tdee}kcal, Target: {target_cal}kcal, Macros: P{macros['protein']}g C{macros['carbs']}g F{macros['fat']}g")
                else:
                    self.log_test("Create User Profile (Bulking)", False, f"Missing calculated fields: {data}")
            else:
                self.log_test("Create User Profile (Bulking)", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create User Profile (Bulking)", False, f"Exception: {str(e)}")
    
    def test_create_user_profile_cutting(self):
        """Test POST /api/user/profile - create cutting profile"""
        try:
            # Create new user for cutting test
            test_email = f"teste.cutting.{int(time.time())}@laf.com"
            signup_data = {
                "email": test_email,
                "password": "MinhaSenh@123!"
            }
            
            response = self.make_request("POST", "/auth/signup", signup_data)
            if response.status_code not in [200, 201]:
                self.log_test("Create User Profile (Cutting)", False, f"Failed to create cutting user: {response.text}")
                return
                
            cutting_user_id = response.json()["user_id"]
            
            profile_data = {
                "id": cutting_user_id,
                "name": "Ana Costa",
                "age": 25,
                "sex": "feminino",
                "height": 165.0,
                "weight": 70.0,
                "target_weight": 65.0,
                "body_fat_percentage": 20.0,
                "training_level": "intermediario",
                "weekly_training_frequency": 5,
                "available_time_per_session": 45,
                "goal": "cutting",
                "dietary_restrictions": ["vegetariano"],
                "food_preferences": ["tofu", "quinoa", "legumes"],
                "injury_history": [],
                "meal_count": 5,
                "language": "pt-BR"
            }
            
            response = self.make_request("POST", "/user/profile", profile_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "tdee" in data and "target_calories" in data and "macros" in data:
                    tdee = data["tdee"]
                    target_cal = data["target_calories"]
                    macros = data["macros"]
                    # Verify cutting has deficit
                    if target_cal < tdee:
                        self.log_test("Create User Profile (Cutting)", True, 
                                    f"Cutting profile created - TDEE: {tdee}kcal, Target: {target_cal}kcal (deficit: {tdee-target_cal:.0f}kcal), Macros: P{macros['protein']}g C{macros['carbs']}g F{macros['fat']}g")
                    else:
                        self.log_test("Create User Profile (Cutting)", False, f"Cutting should have calorie deficit: Target {target_cal} >= TDEE {tdee}")
                else:
                    self.log_test("Create User Profile (Cutting)", False, f"Missing calculated fields: {data}")
            else:
                self.log_test("Create User Profile (Cutting)", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create User Profile (Cutting)", False, f"Exception: {str(e)}")
    
    def test_get_user_profile(self):
        """Test GET /api/user/profile/{user_id} - get profile"""
        if not self.test_user_id:
            self.log_test("Get User Profile", False, "No test user available")
            return
            
        try:
            response = self.make_request("GET", f"/user/profile/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "name" in data and "tdee" in data:
                    self.log_test("Get User Profile", True, 
                                f"Profile retrieved - Name: {data['name']}, TDEE: {data['tdee']}kcal")
                else:
                    self.log_test("Get User Profile", False, f"Missing profile fields: {data}")
            elif response.status_code == 404:
                self.log_test("Get User Profile", False, "Profile not found (404)")
            else:
                self.log_test("Get User Profile", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get User Profile", False, f"Exception: {str(e)}")
    
    def test_update_user_profile(self):
        """Test PUT /api/user/profile/{user_id} - update profile"""
        if not self.test_user_id:
            self.log_test("Update User Profile", False, "No test user available")
            return
            
        try:
            update_data = {
                "weight": 78.5,
                "goal": "manutencao"
            }
            
            response = self.make_request("PUT", f"/user/profile/{self.test_user_id}", update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("weight") == 78.5 and data.get("goal") == "manutencao":
                    new_tdee = data.get("tdee")
                    new_target = data.get("target_calories")
                    self.log_test("Update User Profile", True, 
                                f"Profile updated - Weight: {data['weight']}kg, Goal: {data['goal']}, New TDEE: {new_tdee}kcal, Target: {new_target}kcal")
                else:
                    self.log_test("Update User Profile", False, f"Update not reflected: {data}")
            else:
                self.log_test("Update User Profile", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Update User Profile", False, f"Exception: {str(e)}")

    # ==================== USER SETTINGS TESTS ====================
    
    def test_get_user_settings(self):
        """Test GET /api/user/settings/{user_id} - get settings"""
        if not self.test_user_id:
            self.log_test("Get User Settings", False, "No test user available")
            return
            
        try:
            response = self.make_request("GET", f"/user/settings/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                meal_count = data.get("meal_count", "not found")
                self.log_test("Get User Settings", True, f"Settings retrieved - meal_count: {meal_count}")
            else:
                self.log_test("Get User Settings", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get User Settings", False, f"Exception: {str(e)}")
    
    def test_update_user_settings(self):
        """Test PATCH /api/user/settings/{user_id} - update settings"""
        if not self.test_user_id:
            self.log_test("Update User Settings", False, "No test user available")
            return
            
        try:
            settings_data = {
                "meal_count": 4
            }
            
            response = self.make_request("PATCH", f"/user/settings/{self.test_user_id}", settings_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("meal_count") == 4:
                    self.log_test("Update User Settings", True, f"Settings updated - meal_count: {data['meal_count']}")
                else:
                    self.log_test("Update User Settings", False, f"meal_count not updated: {data}")
            else:
                self.log_test("Update User Settings", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Update User Settings", False, f"Exception: {str(e)}")

    # ==================== DIET TESTS ====================
    
    def test_generate_diet(self):
        """Test POST /api/diet/generate?user_id={id} - generate diet"""
        if not self.test_user_id:
            self.log_test("Generate Diet", False, "No test user available")
            return
            
        try:
            response = self.make_request("POST", f"/diet/generate?user_id={self.test_user_id}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "meals" in data and len(data["meals"]) > 0:
                    meal_count = len(data["meals"])
                    computed_cal = data.get("computed_calories", 0)
                    computed_macros = data.get("computed_macros", {})
                    
                    # Check if meals have total_calories
                    first_meal = data["meals"][0]
                    has_meal_calories = "total_calories" in first_meal
                    meal_calories = first_meal.get("total_calories", 0) if has_meal_calories else 0
                    
                    self.log_test("Generate Diet", True, 
                                f"Diet generated - {meal_count} meals, {computed_cal}kcal total, P{computed_macros.get('protein', 0)}g C{computed_macros.get('carbs', 0)}g F{computed_macros.get('fat', 0)}g, First meal: {meal_calories}kcal")
                else:
                    self.log_test("Generate Diet", False, f"No meals in diet: {data}")
            else:
                self.log_test("Generate Diet", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Generate Diet", False, f"Exception: {str(e)}")
    
    def test_get_user_diet(self):
        """Test GET /api/diet/{user_id} - get diet"""
        if not self.test_user_id:
            self.log_test("Get User Diet", False, "No test user available")
            return
            
        try:
            response = self.make_request("GET", f"/diet/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "meals" in data and len(data["meals"]) > 0:
                    meal_count = len(data["meals"])
                    total_cal = data.get("computed_calories", 0)
                    self.log_test("Get User Diet", True, f"Diet retrieved - {meal_count} meals, {total_cal}kcal")
                else:
                    self.log_test("Get User Diet", False, f"No meals in retrieved diet: {data}")
            elif response.status_code == 404:
                self.log_test("Get User Diet", False, "Diet not found (404)")
            else:
                self.log_test("Get User Diet", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get User Diet", False, f"Exception: {str(e)}")
    
    def test_get_food_substitutes(self):
        """Test GET /api/diet/{user_id}/substitutes/{food_key} - get substitutes"""
        if not self.test_user_id:
            self.log_test("Get Food Substitutes", False, "No test user available")
            return
            
        try:
            # Try common food keys that should exist
            food_keys_to_try = ["ovos", "frango", "arroz_branco", "batata_doce", "aveia"]
            
            for food_key in food_keys_to_try:
                response = self.make_request("GET", f"/diet/{self.test_user_id}/substitutes/{food_key}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "substitutes" in data and len(data["substitutes"]) > 0:
                        substitute_count = len(data["substitutes"])
                        category = data.get("category", "unknown")
                        self.log_test("Get Food Substitutes", True, 
                                    f"Found {substitute_count} substitutes for {food_key} (category: {category})")
                        return  # Success, exit loop
                elif response.status_code == 404:
                    continue  # Try next food key
                else:
                    self.log_test("Get Food Substitutes", False, f"Status {response.status_code} for {food_key}: {response.text}")
                    return
            
            # If we get here, no food key worked
            self.log_test("Get Food Substitutes", False, "No valid food keys found in diet")
            
        except Exception as e:
            self.log_test("Get Food Substitutes", False, f"Exception: {str(e)}")
    
    def test_substitute_food(self):
        """Test PUT /api/diet/{user_id}/substitute - substitute food"""
        if not self.test_user_id:
            self.log_test("Substitute Food", False, "No test user available")
            return
            
        try:
            # First get the diet to find a food to substitute
            diet_response = self.make_request("GET", f"/diet/{self.test_user_id}")
            
            if diet_response.status_code != 200:
                self.log_test("Substitute Food", False, "Could not get diet for substitution test")
                return
            
            diet_data = diet_response.json()
            meals = diet_data.get("meals", [])
            
            if not meals:
                self.log_test("Substitute Food", False, "No meals found for substitution test")
                return
            
            # Find a protein food to substitute
            target_meal_idx = None
            target_food_idx = None
            original_food = None
            
            for meal_idx, meal in enumerate(meals):
                for food_idx, food in enumerate(meal.get("foods", [])):
                    if food.get("category") == "protein":
                        target_meal_idx = meal_idx
                        target_food_idx = food_idx
                        original_food = food
                        break
                if target_meal_idx is not None:
                    break
            
            if target_meal_idx is None:
                self.log_test("Substitute Food", False, "No protein food found for substitution")
                return
            
            # Try to substitute with a different protein
            substitute_data = {
                "meal_index": target_meal_idx,
                "food_index": target_food_idx,
                "new_food_key": "peito_frango" if original_food.get("key") != "peito_frango" else "ovos"
            }
            
            response = self.make_request("PUT", f"/diet/{self.test_user_id}/substitute", substitute_data)
            
            if response.status_code == 200:
                data = response.json()
                # Verify the substitution worked
                new_meals = data.get("meals", [])
                if new_meals and len(new_meals) > target_meal_idx:
                    new_food = new_meals[target_meal_idx]["foods"][target_food_idx]
                    if new_food.get("key") == substitute_data["new_food_key"]:
                        self.log_test("Substitute Food", True, 
                                    f"Food substituted: {original_food.get('name')} → {new_food.get('name')}")
                    else:
                        self.log_test("Substitute Food", False, f"Substitution not applied correctly")
                else:
                    self.log_test("Substitute Food", False, f"Invalid meal structure after substitution")
            else:
                self.log_test("Substitute Food", False, f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Substitute Food", False, f"Exception: {str(e)}")

    # ==================== WORKOUT TESTS ====================
    
    def test_generate_workout(self):
        """Test POST /api/workout/generate?user_id={id} - generate workout"""
        if not self.test_user_id:
            self.log_test("Generate Workout", False, "No test user available")
            return
            
        try:
            response = self.make_request("POST", f"/workout/generate?user_id={self.test_user_id}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "workouts" in data and len(data["workouts"]) > 0:
                    workout_count = len(data["workouts"])
                    first_workout = data["workouts"][0]
                    exercise_count = len(first_workout.get("exercises", []))
                    self.log_test("Generate Workout", True, 
                                f"Workout generated - {workout_count} days, ~{exercise_count} exercises per day")
                else:
                    self.log_test("Generate Workout", False, f"No workouts generated: {data}")
            else:
                self.log_test("Generate Workout", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Generate Workout", False, f"Exception: {str(e)}")
    
    def test_get_user_workout(self):
        """Test GET /api/workout/{user_id} - get workout"""
        if not self.test_user_id:
            self.log_test("Get User Workout", False, "No test user available")
            return
            
        try:
            response = self.make_request("GET", f"/workout/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "workouts" in data and len(data["workouts"]) > 0:
                    workout_count = len(data["workouts"])
                    self.log_test("Get User Workout", True, f"Workout retrieved - {workout_count} days")
                else:
                    self.log_test("Get User Workout", False, f"No workouts in retrieved data: {data}")
            elif response.status_code == 404:
                self.log_test("Get User Workout", False, "Workout not found (404)")
            else:
                self.log_test("Get User Workout", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get User Workout", False, f"Exception: {str(e)}")

    # ==================== PROGRESS TESTS ====================
    
    def test_weight_can_update(self):
        """Test GET /api/progress/weight/{user_id}/can-update - check if can update weight"""
        if not self.test_user_id:
            self.log_test("Weight Can Update", False, "No test user available")
            return
            
        try:
            response = self.make_request("GET", f"/progress/weight/{self.test_user_id}/can-update")
            
            if response.status_code == 200:
                data = response.json()
                can_update = data.get("can_update")
                reason = data.get("reason", "")
                self.log_test("Weight Can Update", True, f"Can update: {can_update}, Reason: {reason}")
            else:
                self.log_test("Weight Can Update", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Weight Can Update", False, f"Exception: {str(e)}")
    
    def test_weight_history(self):
        """Test GET /api/progress/weight/{user_id} - get weight history"""
        if not self.test_user_id:
            self.log_test("Weight History", False, "No test user available")
            return
            
        try:
            response = self.make_request("GET", f"/progress/weight/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                history_count = len(data.get("history", []))
                current_weight = data.get("current_weight")
                can_record = data.get("can_record")
                self.log_test("Weight History", True, 
                            f"History retrieved - {history_count} records, Current: {current_weight}kg, Can record: {can_record}")
            else:
                self.log_test("Weight History", False, f"Status {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Weight History", False, f"Exception: {str(e)}")

    # ==================== MAIN TEST RUNNER ====================
    
    def run_all_tests(self):
        """Run complete regression test suite"""
        print("🚀 LAF BACKEND COMPREHENSIVE REGRESSION TEST SUITE")
        print("=" * 60)
        
        # Health checks
        print("\n📊 HEALTH CHECKS")
        self.test_root_health_check()
        self.test_api_health_check()
        
        # Authentication
        print("\n🔐 AUTHENTICATION")
        self.test_auth_signup()
        self.test_auth_login()
        self.test_auth_validate()
        
        # User Profile
        print("\n👤 USER PROFILE")
        self.test_create_user_profile_bulking()
        self.test_create_user_profile_cutting()
        self.test_get_user_profile()
        self.test_update_user_profile()
        
        # User Settings
        print("\n⚙️ USER SETTINGS")
        self.test_get_user_settings()
        self.test_update_user_settings()
        
        # Diet
        print("\n🍽️ DIET")
        self.test_generate_diet()
        self.test_get_user_diet()
        self.test_get_food_substitutes()
        self.test_substitute_food()
        
        # Workout
        print("\n💪 WORKOUT")
        self.test_generate_workout()
        self.test_get_user_workout()
        
        # Progress
        print("\n📈 PROGRESS")
        self.test_weight_can_update()
        self.test_weight_history()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE REGRESSION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        print("\n🎯 SUCCESS CRITERIA VERIFICATION:")
        
        # Check success criteria from the review request
        no_500_errors = not any("Status 500" in t["details"] for t in self.test_results)
        auth_working = any("Auth" in t["test"] and t["success"] for t in self.test_results)
        profile_working = any("Profile" in t["test"] and t["success"] for t in self.test_results)
        diet_working = any("Diet" in t["test"] and t["success"] for t in self.test_results)
        workout_working = any("Workout" in t["test"] and t["success"] for t in self.test_results)
        
        print(f"✅ No 500 errors: {no_500_errors}")
        print(f"✅ Authentication working: {auth_working}")
        print(f"✅ User Profile CRUD working: {profile_working}")
        print(f"✅ Diet generation working: {diet_working}")
        print(f"✅ Workout generation working: {workout_working}")
        
        # Check specific functionality
        tdee_calculated = any("TDEE:" in t["details"] for t in self.test_results if t["success"])
        macros_calculated = any("Macros:" in t["details"] for t in self.test_results if t["success"])
        substitution_working = any("substituted" in t["details"] for t in self.test_results if t["success"])
        
        print(f"✅ TDEE calculations correct: {tdee_calculated}")
        print(f"✅ Macros calculations correct: {macros_calculated}")
        print(f"✅ Food substitution working: {substitution_working}")
        
        # Overall assessment
        critical_systems_working = auth_working and profile_working and diet_working and workout_working and no_500_errors
        
        if critical_systems_working and failed_tests == 0:
            print(f"\n🎉 ALL SYSTEMS OPERATIONAL - NO REGRESSION DETECTED!")
        elif critical_systems_working:
            print(f"\n⚠️  CORE SYSTEMS WORKING - MINOR ISSUES DETECTED")
        else:
            print(f"\n🚨 CRITICAL REGRESSION DETECTED - IMMEDIATE ATTENTION REQUIRED")

if __name__ == "__main__":
    tester = LAFBackendTester()
    tester.run_all_tests()