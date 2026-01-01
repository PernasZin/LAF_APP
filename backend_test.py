#!/usr/bin/env python3
"""
LAF Backend Testing Suite
Testa correções de bugs críticos de lógica de negócio:
1. Single Source of Truth (Calorias/Macros)
2. Frequência de Treino
3. Porções Realistas
"""

import requests
import json
import sys
from typing import Dict, Any

# Backend URL from frontend .env
BACKEND_URL = "https://laffix.preview.emergentagent.com/api"

class LAFBackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.created_users = []
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def test_health_check(self):
        """Test if backend is running"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("Backend Health Check", True, f"Status: {response.json()}")
                return True
            else:
                self.log_test("Backend Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Error: {str(e)}")
            return False
    
    def create_test_profile(self, profile_data: Dict[str, Any]) -> str:
        """Create a test user profile and return user_id"""
        try:
            response = requests.post(
                f"{self.backend_url}/user/profile",
                json=profile_data,
                timeout=15
            )
            
            if response.status_code == 200:
                user_data = response.json()
                user_id = user_data.get('id')
                self.created_users.append(user_id)
                
                # Validate TDEE and macros calculation
                expected_keys = ['tdee', 'target_calories', 'macros']
                missing_keys = [key for key in expected_keys if key not in user_data or user_data[key] is None]
                
                if missing_keys:
                    self.log_test(f"Profile Creation - {profile_data['name']}", False, 
                                f"Missing calculated fields: {missing_keys}")
                    return None
                
                self.log_test(f"Profile Creation - {profile_data['name']}", True, 
                            f"TDEE: {user_data['tdee']} kcal, Target: {user_data['target_calories']} kcal")
                return user_id
            else:
                self.log_test(f"Profile Creation - {profile_data['name']}", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test(f"Profile Creation - {profile_data['name']}", False, f"Error: {str(e)}")
            return None
    
    def test_diet_single_source_of_truth(self, user_id: str, profile_name: str):
        """Test if diet generation matches profile calories/macros exactly"""
        try:
            # Get user profile first
            profile_response = requests.get(f"{self.backend_url}/user/profile/{user_id}", timeout=10)
            if profile_response.status_code != 200:
                self.log_test(f"Diet SST - {profile_name} (Get Profile)", False, 
                            f"Failed to get profile: {profile_response.status_code}")
                return False
            
            profile = profile_response.json()
            target_calories = profile['target_calories']
            target_macros = profile['macros']
            
            # Generate diet
            diet_response = requests.post(f"{self.backend_url}/diet/generate?user_id={user_id}", timeout=30)
            
            if diet_response.status_code != 200:
                self.log_test(f"Diet SST - {profile_name}", False, 
                            f"Diet generation failed: {diet_response.status_code}, {diet_response.text}")
                return False
            
            diet_plan = diet_response.json()
            
            # Calculate total calories and macros from meals
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            
            for meal in diet_plan.get('meals', []):
                total_calories += meal.get('total_calories', 0)
                macros = meal.get('macros', {})
                total_protein += macros.get('protein', 0)
                total_carbs += macros.get('carbs', 0)
                total_fat += macros.get('fat', 0)
            
            # Check Single Source of Truth (±50 kcal, ±10g tolerance)
            cal_diff = abs(total_calories - target_calories)
            protein_diff = abs(total_protein - target_macros['protein'])
            carbs_diff = abs(total_carbs - target_macros['carbs'])
            fat_diff = abs(total_fat - target_macros['fat'])
            
            sst_passed = (cal_diff <= 50 and protein_diff <= 10 and carbs_diff <= 10 and fat_diff <= 10)
            
            details = f"Target: {target_calories}kcal, Got: {total_calories}kcal (Δ{cal_diff:.0f})"
            details += f" | P: {target_macros['protein']:.0f}g→{total_protein:.1f}g (Δ{protein_diff:.1f})"
            details += f" | C: {target_macros['carbs']:.0f}g→{total_carbs:.1f}g (Δ{carbs_diff:.1f})"
            details += f" | F: {target_macros['fat']:.0f}g→{total_fat:.1f}g (Δ{fat_diff:.1f})"
            
            self.log_test(f"Diet SST - {profile_name}", sst_passed, details)
            
            # Also test realistic portions
            self.test_realistic_portions(diet_plan, profile_name)
            
            return sst_passed
            
        except Exception as e:
            self.log_test(f"Diet SST - {profile_name}", False, f"Error: {str(e)}")
            return False
    
    def test_realistic_portions(self, diet_plan: Dict, profile_name: str):
        """Test if food portions are realistic and rounded"""
        try:
            unrealistic_portions = []
            excessive_olive_oil = []
            
            for meal in diet_plan.get('meals', []):
                meal_name = meal.get('name', 'Unknown')
                
                for food in meal.get('foods', []):
                    food_name = food.get('name', '')
                    quantity_str = food.get('quantity', '0g')
                    
                    # Extract numeric value from quantity (e.g., "150g" -> 150)
                    try:
                        quantity = float(quantity_str.replace('g', '').replace('ml', '').strip())
                    except:
                        continue
                    
                    # Check if quantity is rounded to reasonable steps
                    if quantity > 0:
                        # Check for unrealistic precision (not multiples of 5g, 10g, 25g)
                        if quantity >= 50:
                            if quantity % 25 != 0:
                                unrealistic_portions.append(f"{food_name}: {quantity_str} (should be multiple of 25g)")
                        elif quantity >= 25:
                            if quantity % 25 != 0 and quantity % 10 != 0:
                                unrealistic_portions.append(f"{food_name}: {quantity_str} (should be multiple of 10g or 25g)")
                        elif quantity >= 10:
                            if quantity % 10 != 0 and quantity % 5 != 0:
                                unrealistic_portions.append(f"{food_name}: {quantity_str} (should be multiple of 5g or 10g)")
                        elif quantity >= 5:
                            if quantity % 5 != 0:
                                unrealistic_portions.append(f"{food_name}: {quantity_str} (should be multiple of 5g)")
                    
                    # Check olive oil limits (≤15g per meal)
                    if "azeite" in food_name.lower() or "olive" in food_name.lower():
                        if quantity > 15:
                            excessive_olive_oil.append(f"{meal_name}: {food_name} {quantity_str} (max 15g)")
            
            # Test results
            portions_passed = len(unrealistic_portions) == 0
            olive_oil_passed = len(excessive_olive_oil) == 0
            
            if portions_passed:
                self.log_test(f"Realistic Portions - {profile_name}", True, "All portions properly rounded")
            else:
                self.log_test(f"Realistic Portions - {profile_name}", False, 
                            f"Unrealistic portions: {'; '.join(unrealistic_portions[:3])}")
            
            if olive_oil_passed:
                self.log_test(f"Olive Oil Limits - {profile_name}", True, "Olive oil within limits")
            else:
                self.log_test(f"Olive Oil Limits - {profile_name}", False, 
                            f"Excessive olive oil: {'; '.join(excessive_olive_oil)}")
            
            return portions_passed and olive_oil_passed
            
        except Exception as e:
            self.log_test(f"Realistic Portions - {profile_name}", False, f"Error: {str(e)}")
            return False
    
    def test_workout_frequency_match(self, user_id: str, profile_name: str, expected_frequency: int):
        """Test if workout generation creates exactly N workouts where N = weekly_training_frequency"""
        try:
            # Generate workout
            workout_response = requests.post(f"{self.backend_url}/workout/generate?user_id={user_id}", timeout=30)
            
            if workout_response.status_code != 200:
                self.log_test(f"Workout Frequency - {profile_name}", False, 
                            f"Workout generation failed: {workout_response.status_code}, {workout_response.text}")
                return False
            
            workout_plan = workout_response.json()
            
            # Check frequency match
            actual_frequency = workout_plan.get('weekly_frequency', 0)
            workout_days = workout_plan.get('workout_days', [])
            actual_workouts = len(workout_days)
            
            frequency_match = (actual_frequency == expected_frequency and actual_workouts == expected_frequency)
            
            # Check for distinct workout names
            workout_names = [day.get('name', '') for day in workout_days]
            unique_names = len(set(workout_names))
            distinct_workouts = (unique_names == actual_workouts)
            
            details = f"Expected: {expected_frequency}x/week, Got: {actual_frequency}x/week, Workouts: {actual_workouts}"
            details += f" | Names: {', '.join(workout_names[:3])}" + ("..." if len(workout_names) > 3 else "")
            
            overall_passed = frequency_match and distinct_workouts
            
            if not frequency_match:
                details += " | FREQUENCY MISMATCH"
            if not distinct_workouts:
                details += " | DUPLICATE NAMES"
            
            self.log_test(f"Workout Frequency - {profile_name}", overall_passed, details)
            
            return overall_passed
            
        except Exception as e:
            self.log_test(f"Workout Frequency - {profile_name}", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all critical bug fix tests"""
        print("=" * 60)
        print("LAF BACKEND CRITICAL BUG FIXES VALIDATION")
        print("=" * 60)
        
        # Test 1: Health check
        if not self.test_health_check():
            print("\n❌ Backend not accessible. Stopping tests.")
            return False
        
        print("\n" + "=" * 40)
        print("TESTE 1: PERFIL BULKING (5x/semana)")
        print("=" * 40)
        
        # Test 1: Create BULKING profile (5x/week)
        bulking_profile = {
            "name": "Teste Bulking",
            "age": 28,
            "sex": "masculino",
            "height": 175,
            "weight": 75,
            "training_level": "intermediario",
            "weekly_training_frequency": 5,
            "available_time_per_session": 60,
            "goal": "bulking"
        }
        
        bulking_user_id = self.create_test_profile(bulking_profile)
        if not bulking_user_id:
            print("❌ Failed to create bulking profile. Stopping tests.")
            return False
        
        # Test 2: Diet generation and SST validation
        print("\n" + "-" * 40)
        print("TESTE 2: DIETA BULKING - Single Source of Truth")
        print("-" * 40)
        self.test_diet_single_source_of_truth(bulking_user_id, "Bulking")
        
        # Test 3: Workout frequency validation
        print("\n" + "-" * 40)
        print("TESTE 3: TREINO BULKING - Frequência 5x/semana")
        print("-" * 40)
        self.test_workout_frequency_match(bulking_user_id, "Bulking", 5)
        
        print("\n" + "=" * 40)
        print("TESTE 4: PERFIL CUTTING (3x/semana)")
        print("=" * 40)
        
        # Test 4: Create CUTTING profile (3x/week)
        cutting_profile = {
            "name": "Teste Cutting",
            "age": 35,
            "sex": "feminino",
            "height": 160,
            "weight": 65,
            "training_level": "iniciante",
            "weekly_training_frequency": 3,
            "available_time_per_session": 45,
            "goal": "cutting"
        }
        
        cutting_user_id = self.create_test_profile(cutting_profile)
        if not cutting_user_id:
            print("❌ Failed to create cutting profile.")
        else:
            # Test 5: Diet generation for cutting
            print("\n" + "-" * 40)
            print("TESTE 5: DIETA CUTTING - Single Source of Truth")
            print("-" * 40)
            self.test_diet_single_source_of_truth(cutting_user_id, "Cutting")
            
            # Test 6: Workout frequency for 3x/week
            print("\n" + "-" * 40)
            print("TESTE 6: TREINO CUTTING - Frequência 3x/semana")
            print("-" * 40)
            self.test_workout_frequency_match(cutting_user_id, "Cutting", 3)
        
        # Summary
        print("\n" + "=" * 60)
        print("RESUMO DOS TESTES")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        total_tests = len(self.test_results)
        
        print(f"Testes Executados: {total_tests}")
        print(f"Testes Aprovados: {passed_tests}")
        print(f"Testes Falharam: {total_tests - passed_tests}")
        print(f"Taxa de Sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['passed']]
        if failed_tests:
            print("\n❌ TESTES FALHARAM:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = LAFBackendTester()
    
    try:
        success = tester.run_comprehensive_tests()
        
        if success:
            print("\n🎉 TODOS OS TESTES CRÍTICOS PASSARAM!")
            print("✅ Single Source of Truth funcionando")
            print("✅ Frequência de Treino funcionando") 
            print("✅ Porções Realistas funcionando")
            sys.exit(0)
        else:
            print("\n⚠️  ALGUNS TESTES FALHARAM")
            print("Verifique os detalhes acima para correções necessárias.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nTestes interrompidos pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante execução dos testes: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()