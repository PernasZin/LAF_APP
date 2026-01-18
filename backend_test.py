#!/usr/bin/env python3
"""
TESTE DA FUNCIONALIDADE DE CHECK-IN E AJUSTE DE DIETA
Testa a lógica de ajuste automático de macros/calorias baseado no progresso de peso do usuário.

BASE URL: https://workoutcycler.preview.emergentagent.com/api
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuração
BASE_URL = "https://workoutcycler.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class CheckInTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> tuple[bool, Dict]:
        """Make HTTP request and return (success, response_data)"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            if response.status_code in [200, 201]:
                return True, response.json()
            else:
                return False, {
                    "status_code": response.status_code,
                    "error": response.text[:500]
                }
                
        except Exception as e:
            return False, {"error": str(e)}
    
    def create_user_profile(self, profile_data: Dict) -> Optional[str]:
        """Create user profile and return user_id"""
        success, response = self.make_request("POST", "/user/profile", profile_data)
        
        if success:
            user_id = response.get("id")
            self.log_test(
                f"Create Profile - {profile_data['name']}", 
                True, 
                f"User ID: {user_id}, Goal: {profile_data['goal']}, TDEE: {response.get('tdee')}kcal"
            )
            return user_id
        else:
            self.log_test(
                f"Create Profile - {profile_data['name']}", 
                False, 
                f"Error: {response.get('error', 'Unknown error')}"
            )
            return None
    
    def generate_diet(self, user_id: str) -> Optional[Dict]:
        """Generate diet for user"""
        success, response = self.make_request("POST", f"/diet/generate?user_id={user_id}")
        
        if success:
            total_calories = response.get("computed_calories", 0)
            macros = response.get("computed_macros", {})
            self.log_test(
                f"Generate Diet - {user_id[:8]}", 
                True, 
                f"Calories: {total_calories}kcal, P:{macros.get('protein')}g C:{macros.get('carbs')}g F:{macros.get('fat')}g"
            )
            return response
        else:
            self.log_test(
                f"Generate Diet - {user_id[:8]}", 
                False, 
                f"Error: {response.get('error', 'Unknown error')}"
            )
            return None
    
    def simulate_checkin(self, user_id: str, weight: float, scenario_name: str) -> Optional[Dict]:
        """Simulate check-in with questionnaire"""
        checkin_data = {
            "weight": weight,
            "questionnaire": {
                "diet": 8,
                "training": 8, 
                "cardio": 7,
                "sleep": 7,
                "hydration": 7,
                "energy": 7,
                "hunger": 5,
                "followedDiet": "yes",
                "followedTraining": "yes", 
                "followedCardio": "yes",
                "boredFoods": "",
                "observations": ""
            }
        }
        
        success, response = self.make_request("POST", f"/progress/checkin/{user_id}", checkin_data)
        
        if success:
            diet_kept = response.get("diet_kept", True)
            calories_change = response.get("calories_change", 0)
            self.log_test(
                f"Check-in - {scenario_name}", 
                True, 
                f"Weight: {weight}kg, Diet kept: {diet_kept}, Calories change: {calories_change}kcal"
            )
            return response
        else:
            self.log_test(
                f"Check-in - {scenario_name}", 
                False, 
                f"Error: {response.get('error', 'Unknown error')}"
            )
            return None
    
    def test_14_day_blocking(self, user_id: str) -> bool:
        """Test 14-day blocking mechanism"""
        success, response = self.make_request("GET", f"/progress/weight/{user_id}/can-update")
        
        if success:
            can_update = response.get("can_update", True)
            reason = response.get("reason", "")
            self.log_test(
                "14-Day Blocking Check", 
                True, 
                f"Can update: {can_update}, Reason: {reason}"
            )
            return can_update
        else:
            self.log_test(
                "14-Day Blocking Check", 
                False, 
                f"Error: {response.get('error', 'Unknown error')}"
            )
            return False
    
    def test_food_substitution(self, user_id: str) -> bool:
        """Test food substitution for bored foods"""
        # First, do a check-in with bored foods
        checkin_data = {
            "weight": 80.0,
            "questionnaire": {
                "diet": 8,
                "training": 8,
                "cardio": 7,
                "sleep": 7,
                "hydration": 7,
                "energy": 7,
                "hunger": 5,
                "followedDiet": "yes",
                "followedTraining": "yes",
                "followedCardio": "yes",
                "boredFoods": "frango, arroz",  # Bored of chicken and rice
                "observations": "Enjoei desses alimentos"
            }
        }
        
        success, response = self.make_request("POST", f"/progress/checkin/{user_id}", checkin_data)
        
        if success:
            foods_replaced = response.get("foods_replaced", 0)
            success_test = foods_replaced > 0
            self.log_test(
                "Food Substitution", 
                success_test, 
                f"Foods replaced: {foods_replaced}"
            )
            
            # Verify the diet was updated
            diet_success, diet_response = self.make_request("GET", f"/diet/{user_id}")
            if diet_success:
                # Check if chicken/rice were actually replaced
                meals = diet_response.get("meals", [])
                has_chicken = any(
                    any("frango" in food.get("name", "").lower() for food in meal.get("foods", []))
                    for meal in meals
                )
                has_rice = any(
                    any("arroz" in food.get("name", "").lower() for food in meal.get("foods", []))
                    for meal in meals
                )
                
                replacement_success = not (has_chicken and has_rice)  # At least one should be replaced
                self.log_test(
                    "Food Substitution Verification", 
                    replacement_success, 
                    f"Chicken still present: {has_chicken}, Rice still present: {has_rice}"
                )
                return replacement_success
            
            return success_test
        else:
            self.log_test(
                "Food Substitution", 
                False, 
                f"Error: {response.get('error', 'Unknown error')}"
            )
            return False
    
    def run_cutting_scenario(self):
        """CENÁRIO 1 - CUTTING: Peso não diminuiu → REDUZIR calorias"""
        print("\n🔥 CENÁRIO 1 - CUTTING: Peso não diminuiu → REDUZIR calorias")
        
        # Create cutting profile
        profile_data = {
            "id": f"cutting_test_{int(time.time())}",
            "name": "Teste Cutting",
            "email": "cutting_checkin@test.com",
            "age": 30,
            "sex": "masculino",
            "height": 175,
            "weight": 80,
            "target_weight": 70,
            "goal": "cutting",
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "dietary_restrictions": [],
            "food_preferences": [],
            "injury_history": []
        }
        
        user_id = self.create_user_profile(profile_data)
        if not user_id:
            return False
        
        # Generate initial diet
        initial_diet = self.generate_diet(user_id)
        if not initial_diet:
            return False
        
        initial_calories = initial_diet.get("computed_calories", 0)
        
        # Simulate first check-in (same weight - to create history)
        first_checkin = self.simulate_checkin(user_id, 80.0, "Cutting - First")
        if not first_checkin:
            return False
        
        # Wait a moment and try second check-in (weight didn't decrease)
        time.sleep(2)
        
        # For testing purposes, we'll simulate the scenario where enough time has passed
        # In real scenario, we'd need to wait 14 days or modify the database
        second_checkin = self.simulate_checkin(user_id, 80.0, "Cutting - No Weight Loss")
        
        if second_checkin:
            calories_change = second_checkin.get("calories_change", 0)
            diet_kept = second_checkin.get("diet_kept", True)
            
            # Validate: calories should DECREASE for cutting when weight doesn't drop
            success = calories_change < 0 and not diet_kept
            self.log_test(
                "CUTTING Logic Validation", 
                success, 
                f"Expected: calories_change < 0, diet_kept = false. Got: {calories_change}kcal, diet_kept = {diet_kept}"
            )
            return success
        
        return False
    
    def run_bulking_scenario(self):
        """CENÁRIO 2 - BULKING: Peso não aumentou → AUMENTAR calorias"""
        print("\n💪 CENÁRIO 2 - BULKING: Peso não aumentou → AUMENTAR calorias")
        
        # Create bulking profile
        profile_data = {
            "id": f"bulking_test_{int(time.time())}",
            "name": "Teste Bulking",
            "email": "bulking_checkin@test.com",
            "age": 25,
            "sex": "masculino",
            "height": 180,
            "weight": 75,
            "target_weight": 85,
            "goal": "bulking",
            "training_level": "avancado",
            "weekly_training_frequency": 5,
            "available_time_per_session": 90,
            "dietary_restrictions": [],
            "food_preferences": [],
            "injury_history": []
        }
        
        user_id = self.create_user_profile(profile_data)
        if not user_id:
            return False
        
        # Generate initial diet
        initial_diet = self.generate_diet(user_id)
        if not initial_diet:
            return False
        
        # Simulate first check-in (same weight)
        first_checkin = self.simulate_checkin(user_id, 75.0, "Bulking - First")
        if not first_checkin:
            return False
        
        # Simulate second check-in (weight didn't increase)
        time.sleep(2)
        second_checkin = self.simulate_checkin(user_id, 75.0, "Bulking - No Weight Gain")
        
        if second_checkin:
            calories_change = second_checkin.get("calories_change", 0)
            diet_kept = second_checkin.get("diet_kept", True)
            
            # Validate: calories should INCREASE for bulking when weight doesn't increase
            success = calories_change > 0 and not diet_kept
            self.log_test(
                "BULKING Logic Validation", 
                success, 
                f"Expected: calories_change > 0, diet_kept = false. Got: {calories_change}kcal, diet_kept = {diet_kept}"
            )
            return success
        
        return False
    
    def run_maintenance_scenario(self):
        """CENÁRIO 3 - MANUTENÇÃO: Peso variou muito → AJUSTAR"""
        print("\n⚖️ CENÁRIO 3 - MANUTENÇÃO: Peso variou muito → AJUSTAR")
        
        # Create maintenance profile
        profile_data = {
            "id": f"maintenance_test_{int(time.time())}",
            "name": "Teste Manutencao",
            "email": "manutencao_checkin@test.com",
            "age": 35,
            "sex": "feminino",
            "height": 165,
            "weight": 60,
            "target_weight": 60,
            "goal": "manutencao",
            "training_level": "iniciante",
            "weekly_training_frequency": 3,
            "available_time_per_session": 45,
            "dietary_restrictions": [],
            "food_preferences": [],
            "injury_history": []
        }
        
        user_id = self.create_user_profile(profile_data)
        if not user_id:
            return False
        
        # Generate initial diet
        initial_diet = self.generate_diet(user_id)
        if not initial_diet:
            return False
        
        # Test scenarios for maintenance
        scenarios = [
            (60.0, 62.0, "Weight Increased >1kg", "should decrease calories"),
            (60.0, 58.0, "Weight Decreased >1kg", "should increase calories"),
            (60.0, 60.5, "Weight Stable ±1kg", "should keep diet")
        ]
        
        maintenance_results = []
        
        for initial_weight, final_weight, scenario_name, expected in scenarios:
            # Create new user for each scenario to avoid 14-day blocking
            test_profile = profile_data.copy()
            test_profile["id"] = f"maintenance_test_{scenario_name.replace(' ', '_')}_{int(time.time())}"
            test_profile["weight"] = initial_weight
            
            test_user_id = self.create_user_profile(test_profile)
            if not test_user_id:
                continue
            
            # Generate diet
            self.generate_diet(test_user_id)
            
            # First check-in
            self.simulate_checkin(test_user_id, initial_weight, f"Maintenance - {scenario_name} - First")
            
            # Second check-in with weight change
            time.sleep(1)
            result = self.simulate_checkin(test_user_id, final_weight, f"Maintenance - {scenario_name}")
            
            if result:
                calories_change = result.get("calories_change", 0)
                diet_kept = result.get("diet_kept", True)
                
                # Validate logic based on scenario
                if "Increased" in scenario_name:
                    # Weight increased > 1kg → should reduce calories
                    success = calories_change < 0 and not diet_kept
                elif "Decreased" in scenario_name:
                    # Weight decreased > 1kg → should increase calories  
                    success = calories_change > 0 and not diet_kept
                else:
                    # Weight stable ± 1kg → should keep diet
                    success = diet_kept and calories_change == 0
                
                self.log_test(
                    f"MAINTENANCE {scenario_name}", 
                    success, 
                    f"{expected}. Got: {calories_change}kcal change, diet_kept = {diet_kept}"
                )
                maintenance_results.append(success)
        
        return all(maintenance_results)
    
    def run_food_substitution_scenario(self):
        """CENÁRIO 4 - Substituição de Alimentos Enjoados"""
        print("\n🔄 CENÁRIO 4 - Substituição de Alimentos Enjoados")
        
        # Create profile for food substitution test
        profile_data = {
            "id": f"food_sub_test_{int(time.time())}",
            "name": "Teste Substituicao",
            "email": "food_sub@test.com",
            "age": 28,
            "sex": "masculino",
            "height": 175,
            "weight": 75,
            "target_weight": 70,
            "goal": "cutting",
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "dietary_restrictions": [],
            "food_preferences": [],
            "injury_history": []
        }
        
        user_id = self.create_user_profile(profile_data)
        if not user_id:
            return False
        
        # Generate initial diet
        initial_diet = self.generate_diet(user_id)
        if not initial_diet:
            return False
        
        # First check-in to establish history
        first_checkin = self.simulate_checkin(user_id, 75.0, "Food Sub - First")
        if not first_checkin:
            return False
        
        # Test food substitution
        time.sleep(1)
        return self.test_food_substitution(user_id)
    
    def run_14_day_blocking_test(self):
        """Test 14-day blocking mechanism"""
        print("\n🚫 TESTE DE BLOQUEIO DE 14 DIAS")
        
        # Create profile
        profile_data = {
            "id": f"blocking_test_{int(time.time())}",
            "name": "Teste Bloqueio",
            "email": "blocking@test.com",
            "age": 30,
            "sex": "masculino",
            "height_cm": 175,
            "weight_kg": 80,
            "target_weight_kg": 75,
            "goal": "cutting",
            "training_level": "intermediario",
            "weekly_training_frequency": 4,
            "available_time_per_session": 60,
            "dietary_restrictions": [],
            "food_preferences": [],
            "injury_history": []
        }
        
        user_id = self.create_user_profile(profile_data)
        if not user_id:
            return False
        
        # Generate diet
        self.generate_diet(user_id)
        
        # First check-in
        first_checkin = self.simulate_checkin(user_id, 80.0, "Blocking Test - First")
        if not first_checkin:
            return False
        
        # Immediately try second check-in (should be blocked)
        time.sleep(1)
        
        # Check if update is allowed
        can_update = self.test_14_day_blocking(user_id)
        
        # Try to do another check-in (should fail due to 14-day rule)
        second_checkin = self.simulate_checkin(user_id, 79.0, "Blocking Test - Should Fail")
        
        # The second check-in should fail
        blocking_works = not second_checkin and not can_update
        self.log_test(
            "14-Day Blocking Mechanism", 
            blocking_works, 
            f"Second check-in blocked: {second_checkin is None}, Can update: {can_update}"
        )
        
        return blocking_works
    
    def run_all_tests(self):
        """Run all check-in and diet adjustment tests"""
        print("🧪 INICIANDO TESTES DE CHECK-IN E AJUSTE DE DIETA")
        print("=" * 60)
        
        test_results = []
        
        # Run all scenarios
        test_results.append(self.run_cutting_scenario())
        test_results.append(self.run_bulking_scenario()) 
        test_results.append(self.run_maintenance_scenario())
        test_results.append(self.run_food_substitution_scenario())
        test_results.append(self.run_14_day_blocking_test())
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        passed = sum(test_results)
        total = len(test_results)
        
        print(f"✅ Testes Aprovados: {passed}/{total}")
        print(f"❌ Testes Falharam: {total - passed}/{total}")
        print(f"📈 Taxa de Sucesso: {(passed/total)*100:.1f}%")
        
        # Detailed results
        print("\n📋 RESULTADOS DETALHADOS:")
        for i, result in enumerate(self.test_results):
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = CheckInTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema de check-in funcionando corretamente.")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM. Verifique os logs acima para detalhes.")