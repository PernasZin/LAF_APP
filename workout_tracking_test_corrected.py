#!/usr/bin/env python3
"""
Workout Day Tracking Test Suite for LAF - CORRECTED VERSION
Testing the NEW Workout Day Tracking endpoints with proper understanding of the logic.
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Get backend URL from environment
BACKEND_URL = "https://fit-final.preview.emergentagent.com/api"

class WorkoutTrackingTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_user_id = "046ca077-2173-4a40-8e20-59441d36f2f7"  # Existing user with diet
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
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
            # Test 1: Get status for a future date (should default to not trained)
            url = f"{self.base_url}/workout/status/{self.test_user_id}?date={self.day_after}"
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
                
                # Test 2: Get status without date parameter (should use today)
                url_no_date = f"{self.base_url}/workout/status/{self.test_user_id}"
                response2 = requests.get(url_no_date)
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    if data2["date"] == self.today:
                        self.log_result("Workout Status - Default Date", True, f"Uses today's date when not specified: {self.today}")
                    else:
                        self.log_result("Workout Status - Default Date", False, f"Expected date {self.today}, got {data2['date']}")
                else:
                    self.log_result("Workout Status - Default Date", False, f"HTTP {response2.status_code}")
                
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
            # Test 1: Mark workout as finished for a future date
            url = f"{self.base_url}/workout/finish/{self.test_user_id}"
            payload = {"date": self.day_after}
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("diet_type") == "training":
                    self.log_result("Finish Workout - Success Response", True, f"success=true, diet_type=training")
                    
                    # Verify the workout was actually marked as completed
                    status_url = f"{self.base_url}/workout/status/{self.test_user_id}?date={self.day_after}"
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
                
                # Test 2: Try to mark the same workout again (should fail with proper message)
                response2 = requests.post(url, json=payload)
                
                if response2.status_code == 400:
                    error_data = response2.json()
                    if "já foi marcado" in error_data.get("detail", "").lower():
                        self.log_result("Finish Workout - Duplicate Prevention", True, "Correctly prevents duplicate workout marking")
                    else:
                        self.log_result("Finish Workout - Duplicate Prevention", False, f"Unexpected error message: {error_data}")
                else:
                    self.log_result("Finish Workout - Duplicate Prevention", False, f"Expected HTTP 400, got {response2.status_code}")
                
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
                generate_url = f"{self.base_url}/diet/generate?user_id={self.test_user_id}"
                generate_response = requests.post(generate_url)
                
                if generate_response.status_code != 200:
                    self.log_result("Adjusted Macros - Diet Generation", False, f"Could not generate diet: HTTP {generate_response.status_code}")
                    return False
            
            # Get the actual diet to know the computed values (this is what gets adjusted)
            diet_response = requests.get(diet_url)
            if diet_response.status_code != 200:
                self.log_result("Adjusted Macros - Diet Access", False, f"Cannot access diet: HTTP {diet_response.status_code}")
                return False
            
            diet_data = diet_response.json()
            base_calories = diet_data.get("computed_calories", 0)
            base_macros = diet_data.get("computed_macros", {})
            base_protein = base_macros.get("protein", 0)
            base_carbs = base_macros.get("carbs", 0)
            base_fat = base_macros.get("fat", 0)
            
            # Test 1: Get adjusted macros for training day (day_after - we marked it as trained)
            url = f"{self.base_url}/workout/adjusted-macros/{self.test_user_id}?date={self.day_after}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["base_calories", "adjusted_calories", "base_protein", "adjusted_protein", 
                                 "base_carbs", "adjusted_carbs", "base_fat", "adjusted_fat", "diet_type"]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_result("Adjusted Macros - Response Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Validate that base values match the diet's computed values
                base_values_match = (
                    abs(data["base_calories"] - base_calories) <= 1 and
                    abs(data["base_protein"] - base_protein) <= 1 and
                    abs(data["base_carbs"] - base_carbs) <= 1 and
                    abs(data["base_fat"] - base_fat) <= 1
                )
                
                if base_values_match:
                    self.log_result("Adjusted Macros - Base Values Source", True, "Base values correctly sourced from computed diet values")
                else:
                    self.log_result("Adjusted Macros - Base Values Source", False, 
                                  f"Base values mismatch - Expected from diet: cal={base_calories}, p={base_protein}, c={base_carbs}, f={base_fat}")
                
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
                
                # Test 2: Get adjusted macros for rest day (use a different future date)
                future_rest_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
                url2 = f"{self.base_url}/workout/adjusted-macros/{self.test_user_id}?date={future_rest_date}"
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
    
    def test_business_logic_validation(self):
        """Test the core business logic requirements"""
        print("\n=== TESTING BUSINESS LOGIC VALIDATION ===")
        
        try:
            # Test the specific requirements from the review request
            
            # 1. Test that trained=false gives rest day multipliers
            rest_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
            status_url = f"{self.base_url}/workout/status/{self.test_user_id}?date={rest_date}"
            status_response = requests.get(status_url)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                if (not status_data["trained"] and 
                    status_data["diet_type"] == "rest" and 
                    status_data["calorie_multiplier"] == 0.95 and 
                    status_data["carb_multiplier"] == 0.80):
                    self.log_result("Business Logic - Rest Day Rules", True, 
                                  "trained=false → diet_type=rest, calorie_multiplier=0.95, carb_multiplier=0.80")
                else:
                    self.log_result("Business Logic - Rest Day Rules", False, 
                                  f"Expected rest day rules, got: trained={status_data['trained']}, "
                                  f"diet_type={status_data['diet_type']}, cal_mult={status_data['calorie_multiplier']}")
            
            # 2. Mark workout and verify training day multipliers
            finish_url = f"{self.base_url}/workout/finish/{self.test_user_id}"
            finish_response = requests.post(finish_url, json={"date": rest_date})
            
            if finish_response.status_code == 200:
                finish_data = finish_response.json()
                if finish_data.get("success") and finish_data.get("diet_type") == "training":
                    # Verify status changed
                    status_response2 = requests.get(status_url)
                    if status_response2.status_code == 200:
                        status_data2 = status_response2.json()
                        if (status_data2["trained"] and 
                            status_data2["diet_type"] == "training" and 
                            status_data2["calorie_multiplier"] == 1.05 and 
                            status_data2["carb_multiplier"] == 1.15):
                            self.log_result("Business Logic - Training Day Rules", True, 
                                          "trained=true → diet_type=training, calorie_multiplier=1.05, carb_multiplier=1.15")
                        else:
                            self.log_result("Business Logic - Training Day Rules", False, 
                                          f"Expected training day rules, got: trained={status_data2['trained']}, "
                                          f"diet_type={status_data2['diet_type']}, cal_mult={status_data2['calorie_multiplier']}")
            
            # 3. Test that protein and fat never change in adjusted macros
            macros_url = f"{self.base_url}/workout/adjusted-macros/{self.test_user_id}?date={rest_date}"
            macros_response = requests.get(macros_url)
            
            if macros_response.status_code == 200:
                macros_data = macros_response.json()
                protein_unchanged = macros_data["base_protein"] == macros_data["adjusted_protein"]
                fat_unchanged = macros_data["base_fat"] == macros_data["adjusted_fat"]
                
                if protein_unchanged and fat_unchanged:
                    self.log_result("Business Logic - Protein/Fat Unchanged", True, 
                                  f"Protein: {macros_data['base_protein']}g → {macros_data['adjusted_protein']}g, "
                                  f"Fat: {macros_data['base_fat']}g → {macros_data['adjusted_fat']}g")
                else:
                    self.log_result("Business Logic - Protein/Fat Unchanged", False, 
                                  f"Protein or fat changed: P {macros_data['base_protein']}→{macros_data['adjusted_protein']}, "
                                  f"F {macros_data['base_fat']}→{macros_data['adjusted_fat']}")
            
        except Exception as e:
            self.log_result("Business Logic - Exception", False, str(e))
    
    def run_all_tests(self):
        """Run all workout tracking tests"""
        print("🏋️ STARTING WORKOUT DAY TRACKING TESTS - CORRECTED VERSION")
        print(f"Backend URL: {self.base_url}")
        print(f"Test User ID: {self.test_user_id}")
        print(f"Test Dates: {self.today}, {self.tomorrow}, {self.day_after}")
        
        # Run tests in sequence
        self.test_workout_status_endpoint()
        self.test_finish_workout_endpoint()
        self.test_adjusted_macros_endpoint()
        self.test_business_logic_validation()
        
        # Summary
        print("\n" + "="*60)
        print("🎯 WORKOUT TRACKING TEST SUMMARY - CORRECTED VERSION")
        print("="*60)
        
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