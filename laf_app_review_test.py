#!/usr/bin/env python3
"""
🔍 LAF APP BACKEND TEST - REVIEW REQUEST SPECIFIC
Test the LAF App backend endpoints as specified in the review request

Test Account:
- Email: apple-reviewer@laf.com
- Password: AppleReview2025!

Backend URL: https://laf-app.onrender.com

Tests Required:
1. Login with apple-reviewer credentials
2. Get user profile and verify goal=bulking, tdee present, target_calories > tdee
3. Get diet and verify computed_calories around 3200 (bulking) with meals/foods
4. Generate new diet and verify response
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Backend URL from review request
BASE_URL = "https://laf-app.onrender.com/api"

# Test credentials from review request
TEST_EMAIL = "apple-reviewer@laf.com"
TEST_PASSWORD = "AppleReview2025!"

class LAFAppReviewTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.timeout = 30
        self.token = None
        self.user_id = None
        self.test_results = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.log(f"{status} {test_name}")
        if details:
            self.log(f"   {details}")
        if response_data and not success:
            self.log(f"   Response: {response_data}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data, params=params)
            else:
                return False, f"Unsupported method: {method}"
            
            return True, response
        except Exception as e:
            return False, str(e)
    
    def test_1_login_apple_reviewer(self):
        """1. Test login with apple-reviewer credentials"""
        self.log("🔐 TESTING LOGIN WITH APPLE-REVIEWER CREDENTIALS")
        
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        success, response = self.make_request("POST", "/auth/login", login_data)
        
        if success and response.status_code == 200:
            try:
                data = response.json()
                # Handle both 'token' and 'access_token' response formats
                token = data.get("token") or data.get("access_token")
                user_id = data.get("user_id")
                profile_completed = data.get("profile_completed", False)
                
                if token and user_id:
                    self.token = token
                    self.user_id = user_id
                    self.log_test("Apple Reviewer Login", True, 
                                f"✅ Login successful - User ID: {user_id}, Profile completed: {profile_completed}")
                    
                    # Verify profile_completed=true as required
                    if profile_completed:
                        self.log_test("Profile Completed Check", True, "✅ profile_completed=true as required")
                    else:
                        self.log_test("Profile Completed Check", False, "❌ profile_completed should be true")
                        
                else:
                    self.log_test("Apple Reviewer Login", False, "Missing token or user_id in response", data)
            except Exception as e:
                self.log_test("Apple Reviewer Login", False, f"Error parsing response: {str(e)}", response.text)
        else:
            error_msg = response.text if success else str(response)
            status_code = response.status_code if success else "Request failed"
            self.log_test("Apple Reviewer Login", False, f"Status: {status_code}", error_msg)
    
    def test_2_user_profile(self):
        """2. Test user profile and verify goal=bulking, tdee present, target_calories > tdee"""
        self.log("👤 TESTING USER PROFILE")
        
        if not self.user_id:
            self.log_test("User Profile - No User ID", False, "Cannot test without user ID from login")
            return
        
        success, response = self.make_request("GET", f"/user/profile/{self.user_id}")
        
        if success and response.status_code == 200:
            try:
                profile_data = response.json()
                
                goal = profile_data.get("goal")
                tdee = profile_data.get("tdee")
                target_calories = profile_data.get("target_calories")
                
                # Log all profile data for inspection
                self.log(f"   Profile Data: Goal={goal}, TDEE={tdee}, Target Calories={target_calories}")
                
                # Check goal=bulking
                if goal == "bulking":
                    self.log_test("Goal Check", True, "✅ Goal is 'bulking' as required")
                else:
                    self.log_test("Goal Check", False, f"❌ Goal is '{goal}', expected 'bulking'")
                
                # Check TDEE present
                if tdee and tdee > 0:
                    self.log_test("TDEE Present", True, f"✅ TDEE is present: {tdee} kcal")
                else:
                    self.log_test("TDEE Present", False, f"❌ TDEE is missing or invalid: {tdee}")
                
                # Check target_calories > tdee (surplus for bulking)
                if target_calories and tdee and target_calories > tdee:
                    surplus = target_calories - tdee
                    surplus_percent = (surplus / tdee) * 100
                    self.log_test("Calorie Surplus", True, 
                                f"✅ Target calories ({target_calories}) > TDEE ({tdee}). Surplus: +{surplus} kcal ({surplus_percent:.1f}%)")
                else:
                    self.log_test("Calorie Surplus", False, 
                                f"❌ Target calories ({target_calories}) should be > TDEE ({tdee}) for bulking")
                
                # Store profile for later tests
                self.profile_data = profile_data
                
            except Exception as e:
                self.log_test("User Profile Parsing", False, f"Error parsing profile: {str(e)}", response.text)
        else:
            error_msg = response.text if success else str(response)
            status_code = response.status_code if success else "Request failed"
            self.log_test("User Profile", False, f"Status: {status_code}", error_msg)
    
    def test_3_user_diet(self):
        """3. Test user diet and verify computed_calories around 3200 (bulking) with meals/foods"""
        self.log("🍽️ TESTING USER DIET")
        
        if not self.user_id:
            self.log_test("User Diet - No User ID", False, "Cannot test without user ID from login")
            return
        
        success, response = self.make_request("GET", f"/diet/{self.user_id}")
        
        if success and response.status_code == 200:
            try:
                diet_data = response.json()
                
                computed_calories = diet_data.get("computed_calories")
                meals = diet_data.get("meals", [])
                
                # Log diet overview
                self.log(f"   Diet Data: Computed calories={computed_calories}, Meals count={len(meals)}")
                
                # Check computed_calories around 3200 (bulking)
                if computed_calories:
                    # Allow reasonable variance (±300 kcal from 3200)
                    target = 3200
                    variance = abs(computed_calories - target)
                    
                    if variance <= 300:
                        self.log_test("Bulking Calories Check", True, 
                                    f"✅ Computed calories ({computed_calories}) is close to bulking target (~3200). Variance: ±{variance} kcal")
                    else:
                        self.log_test("Bulking Calories Check", False, 
                                    f"❌ Computed calories ({computed_calories}) is far from bulking target (~3200). Variance: ±{variance} kcal")
                else:
                    self.log_test("Bulking Calories Check", False, "❌ computed_calories is missing")
                
                # Check meals with foods
                if len(meals) > 0:
                    total_foods = sum(len(meal.get("foods", [])) for meal in meals)
                    self.log_test("Meals with Foods", True, 
                                f"✅ Diet has {len(meals)} meals with {total_foods} total foods")
                    
                    # Log sample meals for inspection
                    for i, meal in enumerate(meals[:2]):  # Show first 2 meals
                        meal_name = meal.get("name", f"Meal {i+1}")
                        foods_count = len(meal.get("foods", []))
                        meal_calories = meal.get("total_calories", 0)
                        self.log(f"   {meal_name}: {foods_count} foods, {meal_calories} kcal")
                        
                        # Show sample foods
                        for food in meal.get("foods", [])[:2]:  # Show first 2 foods per meal
                            food_name = food.get("name", "Unknown")
                            food_grams = food.get("grams", 0)
                            food_calories = food.get("calories", 0)
                            self.log(f"     - {food_name}: {food_grams}g, {food_calories} kcal")
                else:
                    self.log_test("Meals with Foods", False, "❌ No meals found in diet")
                
                # Store diet data for later tests
                self.diet_data = diet_data
                
            except Exception as e:
                self.log_test("User Diet Parsing", False, f"Error parsing diet: {str(e)}", response.text)
        else:
            error_msg = response.text if success else str(response)
            status_code = response.status_code if success else "Request failed"
            self.log_test("User Diet", False, f"Status: {status_code}", error_msg)
    
    def test_4_generate_new_diet(self):
        """4. Test generating new diet and verify response"""
        self.log("🔄 TESTING DIET GENERATION")
        
        if not self.user_id:
            self.log_test("Diet Generation - No User ID", False, "Cannot test without user ID from login")
            return
        
        success, response = self.make_request("POST", f"/diet/generate?user_id={self.user_id}")
        
        if success and response.status_code == 200:
            try:
                new_diet_data = response.json()
                
                computed_calories = new_diet_data.get("computed_calories")
                computed_macros = new_diet_data.get("computed_macros", {})
                meals = new_diet_data.get("meals", [])
                
                # Log generation results
                self.log(f"   New Diet: Computed calories={computed_calories}, Meals count={len(meals)}")
                if computed_macros:
                    protein = computed_macros.get("protein", 0)
                    carbs = computed_macros.get("carbs", 0)
                    fat = computed_macros.get("fat", 0)
                    self.log(f"   Macros: P={protein}g, C={carbs}g, F={fat}g")
                
                # Check response structure
                success_checks = []
                
                if computed_calories and computed_calories > 0:
                    success_checks.append("computed_calories present")
                else:
                    success_checks.append("❌ computed_calories missing")
                
                if len(meals) > 0:
                    success_checks.append("meals present")
                else:
                    success_checks.append("❌ meals missing")
                
                if computed_macros:
                    success_checks.append("computed_macros present")
                else:
                    success_checks.append("❌ computed_macros missing")
                
                # Overall success if all key fields present
                all_success = all("❌" not in check for check in success_checks)
                
                if all_success:
                    self.log_test("Diet Generation Response", True, f"✅ {', '.join(success_checks)}")
                else:
                    self.log_test("Diet Generation Response", False, f"Issues: {', '.join(success_checks)}")
                
                # Verify it's still bulking-appropriate
                if computed_calories and hasattr(self, 'profile_data'):
                    profile_tdee = self.profile_data.get("tdee", 0)
                    if computed_calories > profile_tdee:
                        surplus = computed_calories - profile_tdee
                        self.log_test("New Diet Bulking Check", True, 
                                    f"✅ New diet maintains bulking surplus: +{surplus} kcal")
                    else:
                        self.log_test("New Diet Bulking Check", False, 
                                    f"❌ New diet calories ({computed_calories}) should be > TDEE ({profile_tdee})")
                
            except Exception as e:
                self.log_test("Diet Generation Parsing", False, f"Error parsing generated diet: {str(e)}", response.text)
        else:
            error_msg = response.text if success else str(response)
            status_code = response.status_code if success else "Request failed"
            self.log_test("Diet Generation", False, f"Status: {status_code}", error_msg)
    
    def run_review_tests(self):
        """Run all tests as specified in the review request"""
        self.log("🚀 STARTING LAF APP BACKEND REVIEW TESTS")
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"Test Account: {TEST_EMAIL}")
        self.log("=" * 80)
        
        # Execute tests in specified order
        self.test_1_login_apple_reviewer()
        
        if self.token:  # Only proceed if login successful
            self.test_2_user_profile()
            self.test_3_user_diet()
            self.test_4_generate_new_diet()
        else:
            self.log("❌ Cannot proceed with remaining tests - login failed")
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate final test report"""
        self.log("\n" + "=" * 80)
        self.log("📊 LAF APP BACKEND REVIEW TEST RESULTS")
        self.log("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log(f"📋 TEST SUMMARY:")
        self.log(f"   Total Tests: {total_tests}")
        self.log(f"   ✅ Passed: {passed_tests}")
        self.log(f"   ❌ Failed: {failed_tests}")
        self.log(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # List all test results
        self.log(f"\n📝 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            self.log(f"   {status} {result['test']}: {result['details']}")
        
        # Failed tests details
        if failed_tests > 0:
            self.log(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    self.log(f"   • {result['test']}: {result['details']}")
                    if result.get("response"):
                        self.log(f"     Response: {result['response']}")
        
        # Final verdict
        self.log(f"\n🏆 FINAL VERDICT:")
        if success_rate >= 90:
            self.log("   ✅ EXCELLENT: All critical endpoints working correctly")
        elif success_rate >= 75:
            self.log("   ⚠️ GOOD: Most endpoints working, minor issues found")
        elif success_rate >= 50:
            self.log("   ⚠️ CONCERNING: Several endpoints have issues")
        else:
            self.log("   ❌ CRITICAL: Major backend issues found")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "test_results": self.test_results
        }

if __name__ == "__main__":
    tester = LAFAppReviewTester()
    results = tester.run_review_tests()