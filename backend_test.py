#!/usr/bin/env python3
"""
LAF Backend Testing - Final Pre-Launch Bug Fix Validation
Focus: Switch-Goal Endpoint Critical Bug Fixes
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Backend URL from frontend .env
BASE_URL = "https://fit-final.preview.emergentagent.com/api"

class LAFBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.user_token = None
        self.user_id = None
        
    def log_test(self, test_name, success, details="", expected="", actual=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if not success and expected and actual:
            print(f"    Expected: {expected}")
            print(f"    Actual: {actual}")
        print()
        
    def test_auth_signup(self):
        """Test user signup"""
        test_email = f"test-switch-goal-{uuid.uuid4().hex[:8]}@laf.com"
        test_password = "TestPassword123!"
        
        payload = {
            "email": test_email,
            "password": test_password
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/signup", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                # Handle both token formats: "token" or "access_token"
                token = data.get("token") or data.get("access_token")
                user_id = data.get("user_id")
                
                if token and user_id:
                    self.user_token = token
                    self.user_id = user_id
                    self.session.headers.update({"Authorization": f"Bearer {self.user_token}"})
                    self.log_test("AUTH_SIGNUP", True, f"User created: {test_email}")
                    return True
                else:
                    self.log_test("AUTH_SIGNUP", False, "Missing token or user_id in response", "token and user_id", str(data))
                    return False
            else:
                self.log_test("AUTH_SIGNUP", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("AUTH_SIGNUP", False, f"Exception: {str(e)}")
            return False
    
    def test_create_profile(self):
        """Test profile creation"""
        if not self.user_id:
            self.log_test("CREATE_PROFILE", False, "No user_id available")
            return False
            
        profile_data = {
            "id": self.user_id,
            "name": "Test User Switch Goal",
            "age": 30,
            "sex": "masculino",
            "height": 175.0,
            "weight": 80.0,
            "target_weight": 75.0,
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "goal": "bulking",  # Start with bulking
            "dietary_restrictions": [],
            "food_preferences": ["frango", "arroz", "batata_doce"],
            "meal_count": 6
        }
        
        try:
            response = self.session.post(f"{self.base_url}/user/profile", json=profile_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("tdee") and data.get("target_calories") and data.get("macros"):
                    tdee = data["tdee"]
                    calories = data["target_calories"]
                    macros = data["macros"]
                    
                    self.log_test("CREATE_PROFILE", True, 
                                f"Profile created - TDEE: {tdee}kcal, Target: {calories}kcal, "
                                f"Macros: P{macros['protein']}g C{macros['carbs']}g F{macros['fat']}g")
                    return True
                else:
                    self.log_test("CREATE_PROFILE", False, "Missing TDEE/calories/macros in response", 
                                "TDEE, target_calories, macros", str(data))
                    return False
            else:
                self.log_test("CREATE_PROFILE", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("CREATE_PROFILE", False, f"Exception: {str(e)}")
            return False
    
    def test_generate_diet(self):
        """Test diet generation"""
        if not self.user_id:
            self.log_test("GENERATE_DIET", False, "No user_id available")
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/diet/generate?user_id={self.user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "meals" in data and len(data["meals"]) > 0:
                    meals_count = len(data["meals"])
                    total_calories = data.get("computed_calories", 0)
                    
                    # Check if quantities are multiples of 10
                    quantities_valid = True
                    non_multiple_foods = []
                    
                    for meal in data["meals"]:
                        for food in meal.get("foods", []):
                            grams = food.get("grams", 0)
                            if grams % 10 != 0:
                                quantities_valid = False
                                non_multiple_foods.append(f"{food.get('name', 'unknown')}:{grams}g")
                    
                    if quantities_valid:
                        self.log_test("GENERATE_DIET", True, 
                                    f"Diet generated - {meals_count} meals, {total_calories}kcal, all quantities multiples of 10")
                    else:
                        self.log_test("GENERATE_DIET", False, 
                                    f"Diet generated but quantities not multiples of 10: {non_multiple_foods[:3]}")
                    return True
                else:
                    self.log_test("GENERATE_DIET", False, "No meals in response", "meals array", str(data))
                    return False
            else:
                self.log_test("GENERATE_DIET", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GENERATE_DIET", False, f"Exception: {str(e)}")
            return False
    
    def test_switch_goal(self, new_goal):
        """Test switch goal endpoint - CRITICAL BUG FIX VALIDATION"""
        if not self.user_id:
            self.log_test(f"SWITCH_GOAL_{new_goal.upper()}", False, "No user_id available")
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/user/{self.user_id}/switch-goal/{new_goal}")
            
            if response.status_code == 200:
                data = response.json()
                
                # CRITICAL VALIDATIONS
                success_check = data.get("success") == True
                new_calories = data.get("new_calories", 0)
                new_macros = data.get("new_macros", {})
                
                protein = new_macros.get("protein", 0)
                carbs = new_macros.get("carbs", 0)
                fat = new_macros.get("fat", 0)
                
                # All values must be > 0 (NOT zero)
                calories_valid = new_calories > 0
                macros_valid = protein > 0 and carbs > 0 and fat > 0
                
                if success_check and calories_valid and macros_valid:
                    self.log_test(f"SWITCH_GOAL_{new_goal.upper()}", True, 
                                f"SUCCESS - Calories: {new_calories}kcal, Macros: P{protein}g C{carbs}g F{fat}g")
                    return True
                else:
                    issues = []
                    if not success_check:
                        issues.append(f"success={data.get('success')}")
                    if not calories_valid:
                        issues.append(f"calories={new_calories}")
                    if not macros_valid:
                        issues.append(f"macros P{protein}g C{carbs}g F{fat}g")
                    
                    self.log_test(f"SWITCH_GOAL_{new_goal.upper()}", False, 
                                f"VALIDATION FAILED: {', '.join(issues)}", 
                                "success=True, calories>0, all macros>0", 
                                str(data))
                    return False
            else:
                self.log_test(f"SWITCH_GOAL_{new_goal.upper()}", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"SWITCH_GOAL_{new_goal.upper()}", False, f"Exception: {str(e)}")
            return False
    
    def test_diet_saved_correctly(self):
        """Verify that the diet was saved correctly after goal switch"""
        if not self.user_id:
            self.log_test("DIET_SAVED_CHECK", False, "No user_id available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/diet/{self.user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "meals" in data and len(data["meals"]) > 0:
                    meals_count = len(data["meals"])
                    total_calories = data.get("computed_calories", 0)
                    
                    self.log_test("DIET_SAVED_CHECK", True, 
                                f"Diet saved correctly - {meals_count} meals, {total_calories}kcal")
                    return True
                else:
                    self.log_test("DIET_SAVED_CHECK", False, "No meals found in saved diet")
                    return False
            else:
                self.log_test("DIET_SAVED_CHECK", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("DIET_SAVED_CHECK", False, f"Exception: {str(e)}")
            return False
    
    def run_complete_flow_test(self):
        """Run the complete flow test as specified in the review request"""
        print("🔥 TESTE FINAL PRE-LAUNCH - Switch-Goal Bug Fix Validation")
        print("=" * 70)
        
        # Step 1: Create user
        if not self.test_auth_signup():
            return False
            
        # Step 2: Create profile
        if not self.test_create_profile():
            return False
            
        # Step 3: Generate initial diet
        if not self.test_generate_diet():
            return False
            
        # Step 4: Test all 3 switch-goal endpoints (CRITICAL BUG FIXES)
        goals_to_test = ["cutting", "bulking", "manutencao"]
        switch_results = []
        
        for goal in goals_to_test:
            result = self.test_switch_goal(goal)
            switch_results.append(result)
            
            # Verify diet was saved after each switch
            if result:
                self.test_diet_saved_correctly()
            
            # Small delay between tests
            time.sleep(1)
        
        return all(switch_results)
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 TESTE FINAL - RESUMO DOS RESULTADOS")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de Testes: {total_tests}")
        print(f"✅ Sucessos: {passed_tests}")
        print(f"❌ Falhas: {failed_tests}")
        print(f"Taxa de Sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical switch-goal tests
        switch_tests = [r for r in self.test_results if "SWITCH_GOAL" in r["test"]]
        switch_passed = sum(1 for r in switch_tests if r["success"])
        
        print(f"\n🎯 SWITCH-GOAL ENDPOINTS (BUG CRÍTICO):")
        print(f"   Testados: {len(switch_tests)}/3")
        print(f"   Funcionando: {switch_passed}/3")
        
        if switch_passed == 3:
            print("   ✅ TODOS OS SWITCH-GOAL FUNCIONANDO!")
        else:
            print("   ❌ BUGS AINDA PRESENTES!")
        
        # Show failed tests
        failed_tests_list = [r for r in self.test_results if not r["success"]]
        if failed_tests_list:
            print(f"\n❌ TESTES FALHARAM:")
            for test in failed_tests_list:
                print(f"   • {test['test']}: {test['details']}")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    tester = LAFBackendTester()
    
    print("🚀 Iniciando Teste Final Pre-Launch...")
    print(f"Backend URL: {BASE_URL}")
    print()
    
    # Run complete flow test
    success = tester.run_complete_flow_test()
    
    # Print summary
    tester.print_summary()
    
    # Final status
    if success:
        print("🎉 TESTE FINAL: APROVADO - Pronto para lançamento!")
    else:
        print("🚨 TESTE FINAL: REPROVADO - Bugs críticos encontrados!")
    
    return success

if __name__ == "__main__":
    main()