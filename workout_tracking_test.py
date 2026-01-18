#!/usr/bin/env python3
"""
Workout Day Tracking Test Suite for LAF
Testing the NEW Workout Day Tracking endpoints implemented.
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Get backend URL from environment
BACKEND_URL = "https://workoutcycler.preview.emergentagent.com/api"

class WorkoutTrackingTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_user_id = "046ca077-2173-4a40-8e20-59441d36f2f7"  # Existing user with diet
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def test_workout_status_endpoint(self):
        """Test GET /api/workout/status/{user_id}"""
        print("\n=== TESTING WORKOUT STATUS ENDPOINT ===")
        
        try:
            # Test 1: Get status for today (should default to not trained)
            url = f"{self.base_url}/workout/status/{self.test_user_id}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["date", "trained", "is_training_day", "diet_type", "calorie_multiplier", "carb_multiplier"]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_result("Workout Status - Response Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Validate default state (not trained = rest day)
                if not data["trained"] and data["diet_type"] == "rest":
                    if data["calorie_multiplier"] == 0.95 and data["carb_multiplier"] == 0.80:
                        self.log_result("Workout Status - Default State", True, f"trained=false, diet_type=rest, cal_mult=0.95, carb_mult=0.80")
                    else:
                        self.log_result("Workout Status - Default Multipliers", False, f"Expected cal=0.95, carb=0.80, got cal={data['calorie_multiplier']}, carb={data['carb_multiplier']}")
                else:
                    self.log_result("Workout Status - Default Logic", False, f"Expected trained=false, diet_type=rest, got trained={data['trained']}, diet_type={data['diet_type']}")
                
                # Test 2: Get status with specific date
                url_with_date = f"{self.base_url}/workout/status/{self.test_user_id}?date={self.today}"
                response2 = requests.get(url_with_date)
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    if data2["date"] == self.today:
                        self.log_result("Workout Status - Date Parameter", True, f"Date parameter working: {self.today}")
                    else:
                        self.log_result("Workout Status - Date Parameter", False, f"Expected date {self.today}, got {data2['date']}")
                else:
                    self.log_result("Workout Status - Date Parameter", False, f"HTTP {response2.status_code}")
                
                return True
            else:
                self.log_result("Workout Status - HTTP Response", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Workout Status - Exception", False, str(e))
            return False
    
    def test_finish_workout_endpoint(self):
        """Test POST /api/workout/finish/{user_id}"""
        print("\n=== TESTING FINISH WORKOUT ENDPOINT ===")
        
        try:
            # Test 1: Mark workout as finished for today
            url = f"{self.base_url}/workout/finish/{self.test_user_id}"
            payload = {"date": self.today}
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("diet_type") == "training":
                    self.log_result("Finish Workout - Success Response", True, f"success=true, diet_type=training")
                    
                    # Verify the workout was actually marked as completed
                    status_url = f"{self.base_url}/workout/status/{self.test_user_id}?date={self.today}"
                    status_response = requests.get(status_url)
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data["trained"] and status_data["diet_type"] == "training":
                            if status_data["calorie_multiplier"] == 1.05 and status_data["carb_multiplier"] == 1.15:
                                self.log_result("Finish Workout - Status Update", True, "Workout marked as trained, multipliers updated to training values")
                            else:
                                self.log_result("Finish Workout - Training Multipliers", False, f"Expected cal=1.05, carb=1.15, got cal={status_data['calorie_multiplier']}, carb={status_data['carb_multiplier']}")
                        else:
                            self.log_result("Finish Workout - Status Update", False, f"Expected trained=true, diet_type=training, got trained={status_data['trained']}, diet_type={status_data['diet_type']}")
                    else:
                        self.log_result("Finish Workout - Status Verification", False, f"Could not verify status: HTTP {status_response.status_code}")
                else:
                    self.log_result("Finish Workout - Response Format", False, f"Expected success=true, diet_type=training, got success={data.get('success')}, diet_type={data.get('diet_type')}")
                
                # Test 2: Mark workout without date (should use today)
                url2 = f"{self.base_url}/workout/finish/{self.test_user_id}"
                response2 = requests.post(url2, json={})
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    if data2.get("success"):
                        self.log_result("Finish Workout - No Date Parameter", True, "Works without date parameter")
                    else:
                        self.log_result("Finish Workout - No Date Parameter", False, f"Expected success=true, got {data2}")
                else:
                    self.log_result("Finish Workout - No Date Parameter", False, f"HTTP {response2.status_code}")
                
                return True
            else:
                self.log_result("Finish Workout - HTTP Response", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Finish Workout - Exception", False, str(e))
            return False
    
    def test_adjusted_macros_endpoint(self):
        """Test GET /api/workout/adjusted-macros/{user_id}"""
        print("\n=== TESTING ADJUSTED MACROS ENDPOINT ===")
        
        try:
            # First, ensure user has a diet generated
            diet_url = f"{self.base_url}/diet/{self.test_user_id}"
            diet_response = requests.get(diet_url)
            
            if diet_response.status_code != 200:
                # Try to generate diet first
                profile_url = f"{self.base_url}/user/profile/{self.test_user_id}"
                profile_response = requests.get(profile_url)
                
                if profile_response.status_code == 200:
                    generate_url = f"{self.base_url}/diet/generate?user_id={self.test_user_id}"
                    generate_response = requests.post(generate_url)
                    
                    if generate_response.status_code != 200:
                        self.log_result("Adjusted Macros - Diet Generation", False, f"Could not generate diet: HTTP {generate_response.status_code}")
                        return False
                else:
                    self.log_result("Adjusted Macros - User Profile", False, f"User profile not found: HTTP {profile_response.status_code}")
                    return False
            
            # Get user profile to know base macros
            profile_url = f"{self.base_url}/user/profile/{self.test_user_id}"
            profile_response = requests.get(profile_url)
            
            if profile_response.status_code != 200:
                self.log_result("Adjusted Macros - Profile Access", False, f"Cannot access profile: HTTP {profile_response.status_code}")
                return False
            
            profile_data = profile_response.json()
            base_calories = profile_data.get("target_calories", 0)
            base_macros = profile_data.get("macros", {})
            base_protein = base_macros.get("protein", 0)
            base_carbs = base_macros.get("carbs", 0)
            base_fat = base_macros.get("fat", 0)
            
            # Test 1: Get adjusted macros for training day (today - we marked it as trained)
            url = f"{self.base_url}/workout/adjusted-macros/{self.test_user_id}?date={self.today}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["base_calories", "adjusted_calories", "base_protein", "adjusted_protein", 
                                 "base_carbs", "adjusted_carbs", "base_fat", "adjusted_fat", "diet_type"]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_result("Adjusted Macros - Response Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Validate training day calculations
                expected_calories = base_calories * 1.05
                expected_carbs = base_carbs * 1.15
                
                calories_match = abs(data["adjusted_calories"] - expected_calories) <= 1
                carbs_match = abs(data["adjusted_carbs"] - expected_carbs) <= 1
                protein_unchanged = data["base_protein"] == data["adjusted_protein"]
                fat_unchanged = data["base_fat"] == data["adjusted_fat"]
                
                if calories_match and carbs_match and protein_unchanged and fat_unchanged:
                    self.log_result("Adjusted Macros - Training Day Calculations", True, 
                                  f"Calories: {data['base_calories']} → {data['adjusted_calories']} (+5%), "
                                  f"Carbs: {data['base_carbs']} → {data['adjusted_carbs']} (+15%), "
                                  f"Protein/Fat unchanged")
                else:
                    self.log_result("Adjusted Macros - Training Day Calculations", False,
                                  f"Expected cal={expected_calories}, carbs={expected_carbs}, "
                                  f"got cal={data['adjusted_calories']}, carbs={data['adjusted_carbs']}, "
                                  f"protein_unchanged={protein_unchanged}, fat_unchanged={fat_unchanged}")
                
                # Test 2: Get adjusted macros for rest day (tomorrow - not trained)
                url2 = f"{self.base_url}/workout/adjusted-macros/{self.test_user_id}?date={self.tomorrow}"
                response2 = requests.get(url2)
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    
                    # Validate rest day calculations
                    expected_calories_rest = base_calories * 0.95
                    expected_carbs_rest = base_carbs * 0.80
                    
                    calories_match_rest = abs(data2["adjusted_calories"] - expected_calories_rest) <= 1
                    carbs_match_rest = abs(data2["adjusted_carbs"] - expected_carbs_rest) <= 1
                    
                    if calories_match_rest and carbs_match_rest and data2["diet_type"] == "rest":
                        self.log_result("Adjusted Macros - Rest Day Calculations", True,
                                      f"Calories: {data2['base_calories']} → {data2['adjusted_calories']} (-5%), "
                                      f"Carbs: {data2['base_carbs']} → {data2['adjusted_carbs']} (-20%)")
                    else:
                        self.log_result("Adjusted Macros - Rest Day Calculations", False,
                                      f"Expected cal={expected_calories_rest}, carbs={expected_carbs_rest}, "
                                      f"got cal={data2['adjusted_calories']}, carbs={data2['adjusted_carbs']}")
                else:
                    self.log_result("Adjusted Macros - Rest Day Request", False, f"HTTP {response2.status_code}")
                
                return True
            else:
                self.log_result("Adjusted Macros - HTTP Response", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Adjusted Macros - Exception", False, str(e))
            return False
    
    def test_user_creation_scenario(self):
        """Test creating a new user and generating diet first"""
        print("\n=== TESTING NEW USER SCENARIO ===")
        
        try:
            # Create new user profile
            new_user_data = {
                "id": "test-workout-user-123",
                "name": "Test Workout User",
                "age": 28,
                "sex": "masculino",
                "height": 175,
                "weight": 75,
                "target_weight": 70,
                "training_level": "intermediario",
                "weekly_training_frequency": 4,
                "available_time_per_session": 60,
                "goal": "cutting",
                "dietary_restrictions": [],
                "food_preferences": []
            }
            
            profile_url = f"{self.base_url}/user/profile"
            profile_response = requests.post(profile_url, json=new_user_data)
            
            if profile_response.status_code == 200:
                self.log_result("New User - Profile Creation", True, "Profile created successfully")
                
                # Generate diet
                diet_url = f"{self.base_url}/diet/generate?user_id=test-workout-user-123"
                diet_response = requests.post(diet_url)
                
                if diet_response.status_code == 200:
                    self.log_result("New User - Diet Generation", True, "Diet generated successfully")
                    
                    # Test workout endpoints with new user
                    status_url = f"{self.base_url}/workout/status/test-workout-user-123"
                    status_response = requests.get(status_url)
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if not status_data["trained"] and status_data["diet_type"] == "rest":
                            self.log_result("New User - Workout Status", True, "Default workout status correct")
                            
                            # Test adjusted macros
                            macros_url = f"{self.base_url}/workout/adjusted-macros/test-workout-user-123"
                            macros_response = requests.get(macros_url)
                            
                            if macros_response.status_code == 200:
                                macros_data = macros_response.json()
                                if macros_data["diet_type"] == "rest":
                                    self.log_result("New User - Adjusted Macros", True, "Adjusted macros working for new user")
                                else:
                                    self.log_result("New User - Adjusted Macros", False, f"Expected rest day, got {macros_data['diet_type']}")
                            else:
                                self.log_result("New User - Adjusted Macros", False, f"HTTP {macros_response.status_code}")
                        else:
                            self.log_result("New User - Workout Status", False, f"Expected default state, got trained={status_data['trained']}")
                    else:
                        self.log_result("New User - Workout Status", False, f"HTTP {status_response.status_code}")
                else:
                    self.log_result("New User - Diet Generation", False, f"HTTP {diet_response.status_code}: {diet_response.text}")
            else:
                self.log_result("New User - Profile Creation", False, f"HTTP {profile_response.status_code}: {profile_response.text}")
                
        except Exception as e:
            self.log_result("New User - Exception", False, str(e))
    
    def run_all_tests(self):
        """Run all workout tracking tests"""
        print("🏋️ STARTING WORKOUT DAY TRACKING TESTS")
        print(f"Backend URL: {self.base_url}")
        print(f"Test User ID: {self.test_user_id}")
        print(f"Test Date: {self.today}")
        
        # Run tests in sequence
        self.test_workout_status_endpoint()
        self.test_finish_workout_endpoint()
        self.test_adjusted_macros_endpoint()
        self.test_user_creation_scenario()
        
        # Summary
        print("\n" + "="*50)
        print("🎯 WORKOUT TRACKING TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"] and not result["success"]:
                print(f"    → {result['details']}")
        
        print(f"\n📊 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL WORKOUT TRACKING TESTS PASSED!")
            return True
        else:
            print("⚠️  SOME TESTS FAILED - CHECK DETAILS ABOVE")
            return False

if __name__ == "__main__":
    tester = WorkoutTrackingTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)