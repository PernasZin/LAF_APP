#!/usr/bin/env python3
"""
Backend Test Suite - Diet Generation Bug Fix Validation
======================================================

This test suite validates the critical bug fix where diets were "losing" 
calories/carbs when users selected 4 or 5 meals instead of 6.

FIXES TESTED:
1. MAX_FOOD_GRAMS increased from 500g to 800g
2. Created MAX_CARB_GRAMS = 1200g for carbohydrates
3. Adjusted fat limits

SUCCESS CRITERIA:
- Carbs achieve >= 90% of target in ALL configurations (4, 5, 6 meals)
- Calories achieve >= 95% of target in ALL configurations
- Protein achieve >= 95% of target in ALL configurations
- Difference between configurations <= 10%
"""

import requests
import json
import time
from typing import Dict, List, Tuple

# Configuration
BASE_URL = "https://mealmatrix-4.preview.emergentagent.com/api"
TEST_USER_ID = "test_diet_validation"

class DietValidationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.test_user_id = TEST_USER_ID
        self.results = {}
        
    def log(self, message: str):
        """Log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def make_request(self, method: str, endpoint: str, data: dict = None) -> Tuple[int, dict]:
        """Make HTTP request and return status code and response"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "POST":
                response = requests.post(url, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=30)
            elif method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, {"error": "Invalid JSON response", "text": response.text}
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}")
            return 0, {"error": str(e)}
    
    def test_1_create_high_calorie_user(self) -> bool:
        """
        Test 1: Create high-calorie test user
        Expected: target_calories > 3800, carbs > 500g
        """
        self.log("🧪 TEST 1: Creating high-calorie test user...")
        
        user_data = {
            "id": self.test_user_id,
            "name": "Teste Validação",
            "age": 30,
            "sex": "masculino",
            "height": 185,
            "weight": 100,
            "target_weight": 105,
            "body_fat_percentage": 15,
            "activity_level": "intenso",
            "training_level": "avancado",
            "weekly_training_frequency": 5,
            "available_time_per_session": 90,
            "goal": "bulking",
            "dietary_restrictions": [],
            "food_preferences": ["frango", "arroz_branco", "ovos", "banana", "aveia", "batata_doce", "iogurte_grego"]
        }
        
        status, response = self.make_request("POST", "/user/profile", user_data)
        
        if status != 200:
            self.log(f"❌ Failed to create user profile: {status} - {response}")
            return False
            
        # Validate high calorie requirements
        target_calories = response.get("target_calories", 0)
        macros = response.get("macros", {})
        target_carbs = macros.get("carbs", 0)
        
        self.log(f"📊 User Profile Created:")
        self.log(f"   Target Calories: {target_calories} kcal")
        self.log(f"   Target Protein: {macros.get('protein', 0)}g")
        self.log(f"   Target Carbs: {target_carbs}g")
        self.log(f"   Target Fat: {macros.get('fat', 0)}g")
        
        # Validate requirements
        if target_calories < 3800:
            self.log(f"❌ Target calories too low: {target_calories} < 3800")
            return False
            
        if target_carbs < 500:
            self.log(f"❌ Target carbs too low: {target_carbs} < 500g")
            return False
            
        self.log("✅ High-calorie user profile created successfully")
        self.results["user_profile"] = response
        return True
    
    def test_diet_generation(self, meal_count: int) -> Dict:
        """
        Generate diet with specific meal count and validate results
        """
        self.log(f"🧪 Testing diet generation with {meal_count} meals...")
        
        # Step 1: Update meal count settings
        settings_data = {"meal_count": meal_count}
        status, response = self.make_request("PUT", f"/user/settings/{self.test_user_id}", settings_data)
        
        if status != 200:
            self.log(f"⚠️  Settings update failed: {status} - {response}")
            # Continue anyway, might not be implemented
        
        # Step 2: Clear existing diet cache
        status, response = self.make_request("DELETE", f"/diet/{self.test_user_id}")
        if status == 200:
            self.log(f"🗑️  Cleared existing diet cache")
        
        # Step 3: Generate new diet
        status, response = self.make_request("POST", f"/diet/generate?user_id={self.test_user_id}")
        
        if status != 200:
            self.log(f"❌ Diet generation failed: {status} - {response}")
            return {"success": False, "error": response}
        
        # Extract computed values
        computed_calories = response.get("computed_calories", 0)
        computed_macros = response.get("computed_macros", {})
        computed_protein = computed_macros.get("protein", 0)
        computed_carbs = computed_macros.get("carbs", 0)
        computed_fat = computed_macros.get("fat", 0)
        
        # Get target values
        target_calories = response.get("target_calories", 0)
        target_macros = response.get("target_macros", {})
        target_protein = target_macros.get("protein", 0)
        target_carbs = target_macros.get("carbs", 0)
        target_fat = target_macros.get("fat", 0)
        
        # Validate meal count
        meals = response.get("meals", [])
        actual_meal_count = len(meals)
        
        self.log(f"📊 Diet Generated ({meal_count} meals):")
        self.log(f"   Actual Meals: {actual_meal_count}")
        self.log(f"   Target: {target_calories}kcal P:{target_protein}g C:{target_carbs}g F:{target_fat}g")
        self.log(f"   Computed: {computed_calories}kcal P:{computed_protein}g C:{computed_carbs}g F:{target_fat}g")
        
        # Calculate percentages
        cal_percentage = (computed_calories / target_calories * 100) if target_calories > 0 else 0
        protein_percentage = (computed_protein / target_protein * 100) if target_protein > 0 else 0
        carbs_percentage = (computed_carbs / target_carbs * 100) if target_carbs > 0 else 0
        fat_percentage = (computed_fat / target_fat * 100) if target_fat > 0 else 0
        
        self.log(f"   Accuracy: Cal:{cal_percentage:.1f}% P:{protein_percentage:.1f}% C:{carbs_percentage:.1f}% F:{fat_percentage:.1f}%")
        
        return {
            "success": True,
            "meal_count": meal_count,
            "actual_meal_count": actual_meal_count,
            "target_calories": target_calories,
            "computed_calories": computed_calories,
            "target_protein": target_protein,
            "computed_protein": computed_protein,
            "target_carbs": target_carbs,
            "computed_carbs": computed_carbs,
            "target_fat": target_fat,
            "computed_fat": computed_fat,
            "cal_percentage": cal_percentage,
            "protein_percentage": protein_percentage,
            "carbs_percentage": carbs_percentage,
            "fat_percentage": fat_percentage,
            "response": response
        }
    
    def test_2_diet_6_meals(self) -> bool:
        """Test 2: Generate diet with 6 meals"""
        result = self.test_diet_generation(6)
        if not result["success"]:
            return False
            
        self.results["diet_6_meals"] = result
        
        # Validate success criteria
        if result["carbs_percentage"] < 90:
            self.log(f"❌ Carbs below 90%: {result['carbs_percentage']:.1f}%")
            return False
            
        if result["cal_percentage"] < 95:
            self.log(f"❌ Calories below 95%: {result['cal_percentage']:.1f}%")
            return False
            
        if result["protein_percentage"] < 95:
            self.log(f"❌ Protein below 95%: {result['protein_percentage']:.1f}%")
            return False
        
        self.log("✅ 6-meal diet generation passed all criteria")
        return True
    
    def test_3_diet_5_meals(self) -> bool:
        """Test 3: Generate diet with 5 meals"""
        result = self.test_diet_generation(5)
        if not result["success"]:
            return False
            
        self.results["diet_5_meals"] = result
        
        # Validate success criteria
        if result["carbs_percentage"] < 90:
            self.log(f"❌ Carbs below 90%: {result['carbs_percentage']:.1f}%")
            return False
            
        if result["cal_percentage"] < 95:
            self.log(f"❌ Calories below 95%: {result['cal_percentage']:.1f}%")
            return False
            
        if result["protein_percentage"] < 95:
            self.log(f"❌ Protein below 95%: {result['protein_percentage']:.1f}%")
            return False
        
        self.log("✅ 5-meal diet generation passed all criteria")
        return True
    
    def test_4_diet_4_meals(self) -> bool:
        """Test 4: Generate diet with 4 meals"""
        result = self.test_diet_generation(4)
        if not result["success"]:
            return False
            
        self.results["diet_4_meals"] = result
        
        # Validate success criteria
        if result["carbs_percentage"] < 90:
            self.log(f"❌ Carbs below 90%: {result['carbs_percentage']:.1f}%")
            return False
            
        if result["cal_percentage"] < 95:
            self.log(f"❌ Calories below 95%: {result['cal_percentage']:.1f}%")
            return False
            
        if result["protein_percentage"] < 95:
            self.log(f"❌ Protein below 95%: {result['protein_percentage']:.1f}%")
            return False
        
        self.log("✅ 4-meal diet generation passed all criteria")
        return True
    
    def test_5_consistency_validation(self) -> bool:
        """Test 5: Validate consistency between meal configurations"""
        self.log("🧪 TEST 5: Validating consistency between configurations...")
        
        if not all(key in self.results for key in ["diet_4_meals", "diet_5_meals", "diet_6_meals"]):
            self.log("❌ Missing diet results for consistency check")
            return False
        
        # Get calorie values
        cal_4 = self.results["diet_4_meals"]["computed_calories"]
        cal_5 = self.results["diet_5_meals"]["computed_calories"]
        cal_6 = self.results["diet_6_meals"]["computed_calories"]
        
        # Calculate differences
        max_cal = max(cal_4, cal_5, cal_6)
        min_cal = min(cal_4, cal_5, cal_6)
        cal_diff_percent = ((max_cal - min_cal) / min_cal * 100) if min_cal > 0 else 0
        
        self.log(f"📊 Consistency Analysis:")
        self.log(f"   4 meals: {cal_4} kcal")
        self.log(f"   5 meals: {cal_5} kcal")
        self.log(f"   6 meals: {cal_6} kcal")
        self.log(f"   Max difference: {cal_diff_percent:.1f}%")
        
        if cal_diff_percent > 10:
            self.log(f"❌ Calorie difference too high: {cal_diff_percent:.1f}% > 10%")
            return False
        
        self.log("✅ Consistency validation passed")
        return True
    
    def generate_summary_report(self) -> str:
        """Generate comprehensive test summary"""
        report = []
        report.append("=" * 60)
        report.append("DIET GENERATION BUG FIX VALIDATION REPORT")
        report.append("=" * 60)
        
        # Test results summary
        tests = [
            ("User Profile Creation", "user_profile" in self.results),
            ("6-Meal Diet Generation", "diet_6_meals" in self.results),
            ("5-Meal Diet Generation", "diet_5_meals" in self.results),
            ("4-Meal Diet Generation", "diet_4_meals" in self.results),
        ]
        
        report.append("\n📋 TEST RESULTS:")
        for test_name, passed in tests:
            status = "✅ PASS" if passed else "❌ FAIL"
            report.append(f"   {status} {test_name}")
        
        # Detailed analysis
        if all(key in self.results for key in ["diet_4_meals", "diet_5_meals", "diet_6_meals"]):
            report.append("\n📊 DETAILED ANALYSIS:")
            
            for meal_count in [4, 5, 6]:
                key = f"diet_{meal_count}_meals"
                result = self.results[key]
                
                report.append(f"\n   {meal_count} MEALS:")
                report.append(f"      Target: {result['target_calories']}kcal P:{result['target_protein']}g C:{result['target_carbs']}g F:{result['target_fat']}g")
                report.append(f"      Computed: {result['computed_calories']}kcal P:{result['computed_protein']}g C:{result['computed_carbs']}g F:{result['computed_fat']}g")
                report.append(f"      Accuracy: Cal:{result['cal_percentage']:.1f}% P:{result['protein_percentage']:.1f}% C:{result['carbs_percentage']:.1f}% F:{result['fat_percentage']:.1f}%")
                
                # Success criteria check
                criteria_met = []
                criteria_met.append(f"Carbs ≥90%: {'✅' if result['carbs_percentage'] >= 90 else '❌'}")
                criteria_met.append(f"Calories ≥95%: {'✅' if result['cal_percentage'] >= 95 else '❌'}")
                criteria_met.append(f"Protein ≥95%: {'✅' if result['protein_percentage'] >= 95 else '❌'}")
                report.append(f"      Criteria: {' | '.join(criteria_met)}")
        
        # Overall assessment
        report.append("\n🎯 OVERALL ASSESSMENT:")
        
        all_passed = True
        critical_issues = []
        
        for meal_count in [4, 5, 6]:
            key = f"diet_{meal_count}_meals"
            if key in self.results:
                result = self.results[key]
                if result['carbs_percentage'] < 90:
                    all_passed = False
                    critical_issues.append(f"{meal_count}-meal carbs only {result['carbs_percentage']:.1f}%")
                if result['cal_percentage'] < 95:
                    all_passed = False
                    critical_issues.append(f"{meal_count}-meal calories only {result['cal_percentage']:.1f}%")
                if result['protein_percentage'] < 95:
                    all_passed = False
                    critical_issues.append(f"{meal_count}-meal protein only {result['protein_percentage']:.1f}%")
        
        if all_passed:
            report.append("   🎉 ALL TESTS PASSED - Bug fix is working correctly!")
            report.append("   ✅ Carbs achieve ≥90% in all configurations")
            report.append("   ✅ Calories achieve ≥95% in all configurations")
            report.append("   ✅ Protein achieve ≥95% in all configurations")
        else:
            report.append("   ❌ CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                report.append(f"      • {issue}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
    
    def run_all_tests(self) -> bool:
        """Run complete test suite"""
        self.log("🚀 Starting Diet Generation Bug Fix Validation...")
        self.log(f"🔗 Testing against: {self.base_url}")
        
        tests = [
            ("Creating high-calorie test user", self.test_1_create_high_calorie_user),
            ("Testing 6-meal diet generation", self.test_2_diet_6_meals),
            ("Testing 5-meal diet generation", self.test_3_diet_5_meals),
            ("Testing 4-meal diet generation", self.test_4_diet_4_meals),
            ("Validating consistency", self.test_5_consistency_validation),
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            self.log(f"\n{'='*50}")
            self.log(f"🧪 {test_name}...")
            
            try:
                result = test_func()
                if result:
                    self.log(f"✅ {test_name} - PASSED")
                else:
                    self.log(f"❌ {test_name} - FAILED")
                    all_passed = False
            except Exception as e:
                self.log(f"💥 {test_name} - ERROR: {e}")
                all_passed = False
        
        # Generate and display summary
        self.log(f"\n{'='*50}")
        summary = self.generate_summary_report()
        print(summary)
        
        return all_passed

def main():
    """Main test execution"""
    tester = DietValidationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - Diet generation bug fix validated successfully!")
        exit(0)
    else:
        print("\n❌ TESTS FAILED - Issues found in diet generation")
        exit(1)

if __name__ == "__main__":
    main()